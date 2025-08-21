from typing import List

import numpy as np
from rdkit import Chem

from .equivariant_diffusion_onnx import EquivariantDiffusionONNX
from .utils import (ATOM_DECODER, CONTEXT_NORMS, DIMENSION, MAX_N_NODES,
                    MIN_N_NODES, get_context_shape_onnx,
                    ifm_get_xh_from_fragment_onnx,
                    ifm_prepare_fragments_for_merge_onnx,
                    ifm_prepare_gen_fragment_context_onnx,
                    inverse_coord_transform_onnx,
                    prepare_adj_mat_seer_input_onnx, prepare_edm_input_onnx,
                    prepare_fragment_onnx, redefine_bonds_onnx,
                    samples_to_rdkit_mol_onnx, standardize_mol)


class MLConformerGeneratorONNX:
    """
    PyTorch-free ONNX-based implementation
    ML pipeline interface to generates novel molecules based on the 3D shape of a given reference molecule
    or an arbitrary context (principal components of MOI tensor).
    """

    def __init__(
        self,
        diffusion_steps: int = 100,
        dimension: int = DIMENSION,
        min_n_nodes: int = MIN_N_NODES,
        max_n_nodes: int = MAX_N_NODES,
        context_norms: dict = CONTEXT_NORMS,
        atom_decoder: dict = ATOM_DECODER,
        egnn_onnx: str = "./egnn_chembl_15_39.onnx",
        adj_mat_seer_onnx: str = "./adj_mat_seer_chembl_15_39.onnx",
    ):
        """
        Initialise the generator.

        :param min_n_nodes: Minimal value for number of heavy atoms in generated samples
        :param max_n_nodes: Maximal value for number of heavy atoms in generated samples
        :param context_norms: context normalisation parameters
        :param atom_decoder: decoder dict matching int atom encodings to string representations
        :param egnn_onnx: path to EGNN model in the ONNX format
        :param adj_mat_seer_onnx: path to AdjMatSeer model in the ONNX format
        """
        try:
            import onnxruntime
        except ImportError as e:
            raise ImportError(
                'Failed to import onnxruntime. To resolve run `pip install "mlconfgen[onnx]"`\n'
            ) from e

        super().__init__()

        self.context_norms = {
            key: np.array(value) for key, value in context_norms.items()
        }

        self.dimension = dimension

        self.atom_decoder = atom_decoder

        self.min_n_nodes = min_n_nodes
        self.max_n_nodes = max_n_nodes

        self.generative_model = EquivariantDiffusionONNX(
            egnn_onnx=egnn_onnx,
            timesteps=diffusion_steps,
            in_node_nf=8,
            noise_precision=1e-5,
        )

        self.adj_mat_seer = onnxruntime.InferenceSession(adj_mat_seer_onnx)

    def edm_samples(
        self,
        reference_context: np.ndarray,
        n_samples: int = 100,
        max_n_nodes: int = 32,
        min_n_nodes: int = 25,
        resample_steps: int = 0,
        fixed_fragment: Chem.Mol = None,
        inertial_fragment_matching: bool = True,
        blend_power: int = 3,
        ifm_diffusion_level: int = 50,
    ) -> List[Chem.Mol]:
        """
        Generates initial samples using generative diffusion model
        :param reference_context: reference context - tensor of shape (3)
        :param n_samples: number of samples to be generated
        :param max_n_nodes: the maximal number of heavy atoms in the among requested molecules
        :param min_n_nodes: the minimal number of heavy atoms in the among requested molecules
        :param resample_steps: number of resampling steps applied for harmonisation of generation
        :param fixed_fragment: fragment to retain during generation, optional
        :param inertial_fragment_matching: If Inertial fragment matching is to be used
                                           for generation with a fixed fragment
        :param blend_power: power of polynomial blending of a fixed fragment during generation
        :param ifm_diffusion_level: The timestep from which denoising applied during fragment merging.
                                           Only applicable for inertial_fragment_matching = True.
                                           Recommended between 20-50% of total diffusion steps.
        :return: a list of generated samples, without atom adjacency as RDkit Mol objects
        """

        # Make sure that number of atoms of generated samples is within requested range
        if min_n_nodes < self.min_n_nodes:
            min_n_nodes = self.min_n_nodes

        if max_n_nodes > self.max_n_nodes:
            max_n_nodes = self.max_n_nodes

        node_mask, edge_mask, batch_context = prepare_edm_input_onnx(
            n_samples=n_samples,
            reference_context=reference_context,
            context_norms=self.context_norms,
            min_n_nodes=min_n_nodes,
            max_n_nodes=max_n_nodes,
        )
        if fixed_fragment is None:
            x, h = self.generative_model(
                node_mask,
                edge_mask,
                batch_context,
                resample_steps,
            )
        else:
            if inertial_fragment_matching:
                # Inertial Fragment Matching strategy:
                # generate fragments separately -> merge fixed and generated fragments

                # Prepare context for generation of individual fragments
                n_nodes = np.sum(node_mask, axis=1).astype(np.int64)

                fixed_fragment_x, fixed_fragment_h = ifm_get_xh_from_fragment_onnx(fixed_fragment=fixed_fragment)

                (
                    frag_node_mask,
                    frag_edge_mask,
                    frag_context,
                    shift,
                    rotation,
                ) = ifm_prepare_gen_fragment_context_onnx(
                    fixed_fragment_x=fixed_fragment_x,
                    reference_context=reference_context,
                    n_nodes=n_nodes,
                    context_norms=self.context_norms,
                    max_n_nodes=max_n_nodes,
                    min_n_nodes=min_n_nodes,
                )

                # Generate Fragments
                x_gen_frag, h_gen_frag = self.generative_model(
                    frag_node_mask,
                    frag_edge_mask,
                    frag_context,
                    resample_steps,
                )

                # Inverse transformations applied to the coordinates of generated fragments

                x_gen_frag = inverse_coord_transform_onnx(
                    coord=x_gen_frag, shift=shift, rotation=rotation
                )

                # Merge Fixed fragment with the generated ones

                z_known, fixed_mask = ifm_prepare_fragments_for_merge_onnx(
                    fixed_fragment_x=fixed_fragment_x,
                    fixed_fragment_h=fixed_fragment_h,
                    gen_fragments_x=x_gen_frag,
                    gen_fragments_h=h_gen_frag,
                    max_n_nodes=max_n_nodes,
                )

                x, h = self.generative_model.merge_fragments(
                    node_mask=node_mask,
                    edge_mask=edge_mask,
                    fixed_mask=fixed_mask,
                    context=batch_context,
                    z_known=z_known,
                    diffusion_level=ifm_diffusion_level,  # light noise only
                    resample_steps=resample_steps,
                    blend_power=blend_power,
                )
            else:
                z_known, fixed_mask = prepare_fragment_onnx(
                    n_samples=n_samples,
                    fragment=fixed_fragment,
                    max_n_nodes=max_n_nodes,
                    min_n_nodes=min_n_nodes,
                )
                x, h = self.generative_model.inpaint(
                    node_mask,
                    edge_mask,
                    batch_context,
                    z_known,
                    fixed_mask,
                    resample_steps,
                    blend_power,
                )

        mols = samples_to_rdkit_mol_onnx(
            positions=x, one_hot=h, node_mask=node_mask, atom_decoder=self.atom_decoder
        )

        return mols

    def generate_conformers(
        self,
        reference_conformer: Chem.Mol = None,
        n_samples: int = 10,
        variance: int = 2,
        reference_context: np.ndarray = None,
        n_atoms: int = None,
        optimise_geometry: bool = True,
        resample_steps: int = 0,
        fixed_fragment: Chem.Mol = None,
        inertial_fragment_matching: bool = True,
        blend_power: int = 3,
        ifm_diffusion_level: int = 50,
    ) -> List[Chem.Mol]:
        """
        Main method to generate samples from either reference molecule or an arbitrary context.
        :param reference_conformer: A 3D conformer of a reference molecule as an RDKit Mol object
        :param n_samples: number of molecules to generate
        :param variance: int - variation in number of heavy atoms for generated molecules from reference
        :param reference_context: Arbitrary Reference context if applicable, instead of reference_conformer
        :param n_atoms: Reference number of atoms when generating using arbitrary context
        :param optimise_geometry: If true will apply constrained MMFF94 geometry optimisation to generated molecules
        :param resample_steps: number of resampling steps applied for harmonisation of generation
                               improves generation quality, while sacrificing speed
        :param fixed_fragment: Fragment to fix during generation as an RDKit Mol object
        :param inertial_fragment_matching: If Inertial fragment matching is to be used
                                           for generation with a fixed fragment
        :param blend_power: power of the polynomial blending schedule for generation with a fixed fragment
        :param ifm_diffusion_level: The timestep from which denoising applied during fragment merging.
                                           Only applicable for inertial_fragment_matching = True.
                                           Recommended between 20-50% of total diffusion steps.
        :return: A list of valid standardised generated molecules as RDKit Mol objects.
        """
        if reference_conformer:
            # Ensure the initial mol is stripped off Hs
            reference_conformer = Chem.RemoveHs(reference_conformer)
            ref_n_atoms = reference_conformer.GetNumAtoms()
            conf = reference_conformer.GetConformer()
            ref_coord = np.array(conf.GetPositions(), dtype=np.float32)

            # move coord to center
            virtual_com = np.mean(ref_coord, axis=0)
            ref_coord = ref_coord - virtual_com

            ref_context, aligned_coord = get_context_shape_onnx(ref_coord)

        elif reference_context is not None:
            if n_atoms:
                ref_n_atoms = n_atoms
            else:
                raise ValueError(
                    "Reference Number of Atoms should be provided, when generating samples using context."
                )

            ref_context = reference_context

        else:
            raise ValueError(
                "Either a reference RDkit Mol object or context as numpy.ndarray should be provided for generation."
            )

        edm_samples = self.edm_samples(
            reference_context=ref_context,
            n_samples=n_samples,
            min_n_nodes=ref_n_atoms - variance,
            max_n_nodes=ref_n_atoms + variance,
            resample_steps=resample_steps,
            fixed_fragment=fixed_fragment,
            inertial_fragment_matching=inertial_fragment_matching,
            blend_power=blend_power,
            ifm_diffusion_level=ifm_diffusion_level,
        )

        (
            el_batch,
            dm_batch,
            b_adj_mat_batch,
            canonicalised_samples,
        ) = prepare_adj_mat_seer_input_onnx(
            mols=edm_samples,
            dimension=self.dimension,
        )

        adj_mat_batch = self.adj_mat_seer.run(
            None,
            {"elements": el_batch, "dist_mat": dm_batch, "adj_mat": b_adj_mat_batch},
        )[0]

        # Append generated bonds and standardise existing samples
        optimised_conformers = []

        for i, adj_mat in enumerate(adj_mat_batch):
            f_mol = redefine_bonds_onnx(canonicalised_samples[i], adj_mat)
            std_mol = standardize_mol(mol=f_mol, optimize_geometry=optimise_geometry)
            if std_mol:
                optimised_conformers.append(std_mol)

        return optimised_conformers

    def __call__(
        self,
        reference_conformer: Chem.Mol = None,
        n_samples: int = 10,
        variance: int = 2,
        reference_context: np.ndarray = None,
        n_atoms: int = None,
        optimise_geometry: bool = True,
        resample_steps: int = 0,
        fixed_fragment: Chem.Mol = None,
        inertial_fragment_matching: bool = True,
        blend_power: int = 3,
        ifm_diffusion_level: int = 50,
    ) -> List[Chem.Mol]:
        out = self.generate_conformers(
            reference_conformer,
            n_samples,
            variance,
            reference_context,
            n_atoms,
            optimise_geometry,
            resample_steps,
            fixed_fragment,
            inertial_fragment_matching,
            blend_power,
            ifm_diffusion_level,
        )

        return out
