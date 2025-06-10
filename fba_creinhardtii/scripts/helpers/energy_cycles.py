from cobra.flux_analysis import flux_variability_analysis
from cobra.util import create_stoichiometric_matrix
from cobra.core import Model

import numpy as np
from scipy.linalg import null_space
import networkx as nx

def energy_cycles_flux(model, threshold=1e-6):
    """Detect energy-generating cycles using FVA and directional graphs"""

    # Run FVA to get reversible reactions
    fva = flux_variability_analysis(model, fraction_of_optimum=0.9)
    reversible_rxns = fva[(fva['minimum'] < -threshold) & (fva['maximum'] > threshold)].index.to_list()

    # Build Directed Graph for Reactions
    G = nx.DiGraph()
    for rxn in model.reactions:
        if rxn.id in reversible_rxns:
            for met in rxn.metabolites:
                G.add_edge(rxn.id, met.id)
                G.add_edge(met.id, rxn.id)
    
    # Find cycles in the graph
    cycles = list(nx.simple_cycles(G))
    egcs = [cycle for cycle in cycles if len(cycle) > 2]

    return egcs

def find_egcs_null_space(model: Model, threshold=1e-6):
    """Detect energy-generating cycles via nullspace of stoichiometric matrix"""

    S = create_stoichiometric_matrix(model)
    N = null_space(S)
    
    loops = []

    for i in range(N.shape[1]):
        loop_rxns = [model.reactions[j].id for j in np.where(abs(N[:, i]) > threshold)[0]]
        if len(loop_rxns) > 1:
            loops.append(loop_rxns)
    
    return loops