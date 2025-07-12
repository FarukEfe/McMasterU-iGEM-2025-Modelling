# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite
# Toolbox
from scripts.helpers.tools import get_rxn_metabolites, sort_by_similarity
# Parse
from data.altered.model import *
from data.altered.parser import parse_obj
# Other
import os, sys

if __name__ == "__main__":

    # Get initial model path (or name) as input from command line

    pth = "./data/raw/iBD1106.xml"

    model, err = io.validate_sbml_model(pth)
    print(len(model.reactions), len(model.metabolites))
    if model:
        # Get mets in the nucleic compartment
        mets = [met for met in model.metabolites if met.compartment == 'n']
        # Parse the json rxns from the mva pathway
        new_rxns: list[Rxn] = parse_obj('./data/altered/rxns.json')
        # Add each rxn into the nucleic compartment and make a separate model copy
        for rxn in new_rxns:
            print(f"Reaction: {rxn.name}")
            # Declare new model and reaction
            new_model = model.copy()
            new_rxn = Reaction(rxn.name.strip().replace(" ", "_"))
            new_rxn.name = rxn.name
            # Format new_rxn metabolites for insertion
            _format_subs = lambda x: Met(name=x.name, coef=(-1*x.coef))
            new_mets = list(map(_format_subs, rxn.subs)) + rxn.prod
            # If a metabolite already exists in the same compartment, ignore. Otherwise add the new metabolite. User controlled.
            for nm in new_mets:
                search_results = sort_by_similarity([str((met.name, met.compartment)) for met in new_model.metabolites], nm.name)[:5]
                inp = input(f"\tMetabolite: {nm.name}. Similar finds:\n\t{"\n\t".join(search_results).strip()}\n\tAdd to species?\n\t1 - Yes | Ignore on anything else\n")
                if inp == "1":
                    add_met = Metabolite()
                    # Generate unique id, and set compartment as the nucleus
            # Add metabolites to reaction
            new_rxn.add_metabolites({})
            print("New reaction: ", new_rxn.name, str(new_rxn.metabolites))
            # New model and add the reaction
            new_model.add_reactions([new_rxn])
            print("Model state: ", new_rxn in new_model.reactions, new_rxn in model.reactions)
            # Export the new model
            export_path = './data/altered/xmls'
            if not os.path.exists(export_path): os.mkdir(export_path)
            print("Compare metabolites: ", len(model.metabolites), len(new_model.metabolites))
            print("Compare reactions: ", len(model.reactions), len(new_model.reactions))
            io.write_sbml_model(new_model, os.path.join(export_path, f"iBD1106_{new_rxn.id}.xml"))
                

        
        
    
    

    
    
    
# for rxn in model.reactions:
#     print(help(rxn))