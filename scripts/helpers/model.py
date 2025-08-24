from cobra.flux_analysis import flux_variability_analysis
from cobra.util import create_stoichiometric_matrix
from cobra.core import Model, Gene, Metabolite, Reaction

import numpy as np
from scipy.linalg import null_space
import networkx as nx

def met_in_model(model, met: str):
    try:
        model.metabolites.get_by_id(met)
        return True
    except:
        return False

def add_single_gene_reaction_pair(
    model: Model, 
    gene_id: str, 
    reaction_id: str, 
    reaction_name: str,
    reaction_subsystem: str, 
    metabolites: list[tuple[int, str]],
    gene_name=None,
    reversible=False
):
    """Add a gene-reaction pair to the model."""

    # Avoid duplicates for gene and reaction
    assert not model.genes.query(lambda k: k == gene_id, attribute='id')
    assert not model.reactions.query(lambda k: k == reaction_id, attribute='id')
    # Avoid metabolites not in model and subsystem exists
    assert all(list(map(lambda x: met_in_model(model, x[1]), metabolites)))
    assert reaction_subsystem in [grp.name for grp in model.groups]

    # Add gene and reaction to model
    rxn = Reaction(id=reaction_id)

    if gene_name is None:
        gene_name = gene_id
    gene = Gene(gene_id, name=gene_name)

    model.add_reactions([rxn])
    model.genes.add(gene)

    rxn.name = reaction_name
    rxn.bounds = (-1000, 1000) if reversible else (0, 1000)

    # Find metabolite objects from id list
    add_mets = {}
    for coeff, met_id in metabolites:
        met = model.metabolites.get_by_id(met_id)
        add_mets[met] = coeff
    # Add metabolites and gene to reaction data
    rxn.add_metabolites(add_mets)
    rxn.gene_reaction_rule = gene_id

# BELOW IS DEPRECATED!!!

# def energy_cycles_flux(model, threshold=1e-6):
#     """Detect energy-generating cycles using FVA and directional graphs"""

#     # Run FVA to get reversible reactions
#     fva = flux_variability_analysis(model, fraction_of_optimum=0.9)
#     reversible_rxns = fva[(fva['minimum'] < -threshold) & (fva['maximum'] > threshold)].index.to_list()

#     # Build Directed Graph for Reactions
#     G = nx.DiGraph()
#     for rxn in model.reactions:
#         if rxn.id in reversible_rxns:
#             for met in rxn.metabolites:
#                 G.add_edge(rxn.id, met.id)
#                 G.add_edge(met.id, rxn.id)
    
#     # Find cycles in the graph
#     cycles = list(nx.simple_cycles(G))
#     egcs = [cycle for cycle in cycles if len(cycle) > 2]

#     return egcs

# def find_egcs_null_space(model: Model, threshold=1e-6):
#     """Detect energy-generating cycles via nullspace of stoichiometric matrix"""

#     S = create_stoichiometric_matrix(model)
#     N = null_space(S)
    
#     loops = []

#     for i in range(N.shape[1]):
#         loop_rxns = [model.reactions[j].id for j in np.where(abs(N[:, i]) > threshold)[0]]
#         if len(loop_rxns) > 1:
#             loops.append(loop_rxns)
    
#     return loops