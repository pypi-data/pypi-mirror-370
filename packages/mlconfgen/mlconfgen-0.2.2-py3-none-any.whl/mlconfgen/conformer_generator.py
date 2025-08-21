from typing import List

import torch
from rdkit import Chem

from .adj_mat_seer import AdjMatSeer
from .egnn import EGNNDynamics
from .equivariant_diffusion import (EquivariantDiffusion,
                                    PredefinedNoiseSchedule)
from .utils import (ATOM_DECODER, CONTEXT_NORMS, DIMENSION, MAX_N_NODES,
                    MIN_N_NODES, NUM_BOND_TYPES, get_context_shape,
                    ifm_get_xh_from_fragment, ifm_prepare_fragments_for_merge,
                    ifm_prepare_gen_fragment_context, inverse_coord_transform,
                    prepare_adj_mat_seer_input, prepare_edm_input,
                    prepare_fragment, redefine_bonds, samples_to_rdkit_mol,
                    standardize_mol)


class MLConformerGenerator(torch.nn.Module):
    """
    ML pipeline interface to generates novel molecules based on the 3D shape of a given reference molecule
    or an arbitrary context (principal components of MOI tensor).
    """

    def __init__(
        self,
        diffusion_steps: int = 100,
        device: torch.device = torch.device("cpu"),
        dimension: int = DIMENSION,
        num_bond_types: int = NUM_BOND_TYPES,
        min_n_nodes: int = MIN_N_NODES,
        max_n_nodes: int = MAX_N_NODES,
        context_norms: dict = CONTEXT_NORMS,
        atom_decoder: dict = ATOM_DECODER,
        edm_weights: str = "./edm_moi_chembl_15_39.pt",
        adj_mat_seer_weights: str = "./adj_mat_seer_chembl_15_39.pt",
    ):
        """
        Initialise the generator.

        :param diffusion_steps: Number of denoising steps - max 1000
        :param device: device to run the model on
        :param dimension: Maximal supported number of heavy atoms
        :param num_bond_types: Number of supported bond types
        :param min_n_nodes: Minimal value for number of heavy atoms in generated samples
        :param max_n_nodes: Maximal value for number of heavy atoms in generated samples
        :param context_norms: context normalisation parameters
        :param atom_decoder: decoder dict matching int atom encodings to string representations
        :param edm_weights: path to Equivariant Diffusion model state dict
        :param adj_mat_seer_weights: path to AdjMatSeer model state dict
        """
        super().__init__()

        self.device = device

        self.dimension = dimension

        self.context_norms = {
            key: torch.tensor(value) for key, value in context_norms.items()
        }

        self.atom_decoder = atom_decoder

        self.min_n_nodes = min_n_nodes
        self.max_n_nodes = max_n_nodes

        net_dynamics = EGNNDynamics(
            in_node_nf=9,
            context_node_nf=3,
            hidden_nf=420,
            device=device,
        )

        generative_model = EquivariantDiffusion(
            dynamics=net_dynamics,
            in_node_nf=8,
            timesteps=1000,
            noise_precision=1e-5,
        )

        adj_mat_seer = AdjMatSeer(
            dimension=dimension,
            n_hidden=2048,
            embedding_dim=64,
            num_embeddings=36,
            num_bond_types=num_bond_types,
            device=device,
        )

        generative_model.load_state_dict(
            torch.load(
                edm_weights,
                map_location=device,
            )["state_dict"]
        )

        adj_mat_seer.load_state_dict(
            torch.load(
                adj_mat_seer_weights,
                map_location=device,
            )["state_dict"]
        )

        # Update denoising steps for the Equivarinat Diffusion
        generative_model.gamma = PredefinedNoiseSchedule(
            timesteps=diffusion_steps, precision=1e-5
        )

        generative_model.time_steps = torch.flip(
            torch.arange(0, diffusion_steps, device=device), dims=[0]
        )

        generative_model.T = diffusion_steps
        # ----------------------------

        generative_model.to(device)
        adj_mat_seer.to(device)

        generative_model.eval()
        adj_mat_seer.eval()

        self.generative_model = generative_model
        self.adj_mat_seer = adj_mat_seer

    @torch.no_grad()
    def edm_samples(
        self,
        reference_context: torch.Tensor,
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
        Generates initial samples using the diffusion model
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

        # Make sure that number of atoms of generated samples is within allowed range
        if min_n_nodes < self.min_n_nodes:
            min_n_nodes = self.min_n_nodes

        if max_n_nodes > self.max_n_nodes:
            max_n_nodes = self.max_n_nodes

        node_mask, edge_mask, batch_context = prepare_edm_input(
            n_samples=n_samples,
            reference_context=reference_context,
            context_norms=self.context_norms,
            min_n_nodes=min_n_nodes,
            max_n_nodes=max_n_nodes,
            device=self.device,
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
                n_nodes = torch.sum(node_mask, dim=1).to(torch.long)

                fixed_fragment_x, fixed_fragment_h = ifm_get_xh_from_fragment(
                    fixed_fragment=fixed_fragment, device=self.device
                )

                (
                    frag_node_mask,
                    frag_edge_mask,
                    frag_context,
                    shift,
                    rotation,
                ) = ifm_prepare_gen_fragment_context(
                    fixed_fragment_x=fixed_fragment_x,
                    reference_context=reference_context,
                    n_nodes=n_nodes,
                    context_norms=self.context_norms,
                    max_n_nodes=max_n_nodes,
                    min_n_nodes=min_n_nodes,
                    device=self.device,
                )

                # Generate Fragments
                x_gen_frag, h_gen_frag = self.generative_model(
                    frag_node_mask,
                    frag_edge_mask,
                    frag_context,
                    resample_steps,
                )

                # Inverse transformations applied to the coordinates of generated fragments

                x_gen_frag = inverse_coord_transform(
                    coord=x_gen_frag, shift=shift, rotation=rotation
                )

                # Merge Fixed fragment with the generated ones

                z_known, fixed_mask = ifm_prepare_fragments_for_merge(
                    fixed_fragment_x=fixed_fragment_x,
                    fixed_fragment_h=fixed_fragment_h,
                    gen_fragments_x=x_gen_frag,
                    gen_fragments_h=h_gen_frag,
                    device=self.device,
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
                # Simple strategy with fixed fragment blending
                z_known, fixed_mask = prepare_fragment(
                    n_samples=n_samples,
                    fixed_fragment=fixed_fragment,
                    max_n_nodes=max_n_nodes,
                    min_n_nodes=min_n_nodes,
                    device=self.device,
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

        mols = samples_to_rdkit_mol(
            positions=x, one_hot=h, node_mask=node_mask, atom_decoder=self.atom_decoder
        )

        return mols

    @torch.no_grad()
    def generate_conformers(
        self,
        reference_conformer: Chem.Mol = None,
        n_samples: int = 10,
        variance: int = 2,
        reference_context: torch.Tensor = None,
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
                                           for generation with a fixed fragment instead of a simple blending.
        :param blend_power: power of the polynomial blending schedule for generation with a fixed fragment
        :param ifm_diffusion_level: The timestep from which denoising applied during fragment merging.
                                           Only applicable for inertial_fragment_matching = True.
        :return: A list of valid standardised generated molecules as RDKit Mol objects
        """
        if reference_conformer:
            # Ensure the initial mol is stripped off Hs
            reference_conformer = Chem.RemoveHs(reference_conformer)
            ref_n_atoms = reference_conformer.GetNumAtoms()
            conf = reference_conformer.GetConformer()
            ref_coord = torch.tensor(conf.GetPositions(), dtype=torch.float32)

            # move coord to center
            virtual_com = torch.mean(ref_coord, dim=0)
            ref_coord = ref_coord - virtual_com

            ref_context, aligned_coord = get_context_shape(ref_coord)

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
                "Either a reference RDkit Mol object or context as torch.Tensor should be provided for generation."
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
        ) = prepare_adj_mat_seer_input(
            mols=edm_samples,
            dimension=self.dimension,
            device=self.device,
        )

        adj_mat_batch = self.adj_mat_seer(
            elements=el_batch, dist_mat=dm_batch, adj_mat=b_adj_mat_batch
        )

        adj_mat_batch = adj_mat_batch.to("cpu")

        # Append generated bonds and standardise existing samples
        optimised_conformers = []

        for i, adj_mat in enumerate(adj_mat_batch):
            f_mol = redefine_bonds(canonicalised_samples[i], adj_mat)
            std_mol = standardize_mol(mol=f_mol, optimize_geometry=optimise_geometry)
            if std_mol:
                optimised_conformers.append(std_mol)

        return optimised_conformers

    @torch.no_grad()
    def forward(
        self,
        reference_conformer: Chem.Mol = None,
        n_samples: int = 10,
        variance: int = 2,
        reference_context: torch.Tensor = None,
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
