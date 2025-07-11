from cobra import io
from cobra.core import Reaction
from scripts.helpers.tools import get_rxn_metabolites
import os

pth = "./data/raw/iBD1106.xml"

model, err = io.validate_sbml_model(pth)


if model:
    # sample = model.reactions[50]
    # # print(sample.id, sample.name, sample.subsystem, model.repair, sep='\n')
    # rxn_new = Reaction("sth")
    # rxn_new.get_coefficient
    # # print(help(rxn_new))
    # sample = model.metabolites[50]
    # print(help(sample))
    # print(sample.id, sample.name, sample.compartment, )
    sample = model.reactions[100]
    mets, cofs = get_rxn_metabolites(sample.id, model)
    print(mets, cofs, sep="\n")

    
    
    
# for rxn in model.reactions:
#     print(help(rxn))