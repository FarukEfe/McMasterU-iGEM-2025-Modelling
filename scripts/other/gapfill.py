# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite, Model
# Toolbox
from scripts.helpers.tools import get_rxn_metabolites, sort_by_similarity
# Parse
from data.altered.model import *
from data.altered.parser import parse_obj
# Other
import os, sys
import pandas as pd

if __name__ == "__main__":

    # Get initial model path (or name) as input from command line

    pth = "./data/raw/iBD1106.xml"

    model, error = io.validate_sbml_model(pth, validate=True)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)
    
    # Import kegg .csv files
    kegg_compound_path = "./data/kegg/cre00100_compounds_ext.csv"
    kegg_rxn_path = "./data/kegg/cre00100_reactions.csv"
    if not os.path.exists(kegg_compound_path) or not os.path.exists(kegg_rxn_path):
        print(f"KEGG files not found. Exiting...")
        sys.exit(1)

    kegg_compound_df = pd.read_csv(kegg_compound_path, index_col=0)
    kegg_rxn_df = pd.read_csv(kegg_rxn_path, index_col=0)

    # Make empty model on cobra and introduece compounds and reactions
    new_model = model.copy()
    new_model.id = "KEGG_Gapfill_Model"

    # iterate through dataframe to add metabolites that are missing
    list_mets: list[tuple[str,str,Metabolite]] = [(met.id, met.name, met) for met in model.metabolites]
    for _, cpd in kegg_compound_df.iterrows():
        searches = sort_by_similarity(list_mets, cpd['NAME_SHORT'])
        print(cpd['NAME_SHORT'], f"({cpd['FORMULA']})", f". Most similar:\n\t{"\n\t".join(list(map(lambda x: f"{x[1]} ({x[2].formula}) ({x[2].compartment})", searches))[:5])}", end='\n')

        # Filter searches based on if they're in compartment 'c'
        searches = [s[2].formula for s in searches if s[2].compartment == 'c']

        if cpd['FORMULA'] in searches:
            print(f"Found matching compound: {cpd['NAME_SHORT']} ({cpd['FORMULA']})")
            continue
        else:
            print(f"No matching compound found for: {cpd['NAME_SHORT']} ({cpd['FORMULA']})")
            newMet = Metabolite(
                id=cpd['KEGG_ID'],
                name=cpd['NAME_SHORT'],
                formula=cpd['FORMULA'],
                compartment='c',
            )
            new_model.add_metabolites([newMet])
            print(f"Added {newMet.id} to the new model.")
            continue
        
        # while True:
        #     ans = input("1 - Add Met | 0 - Ignore\n")

        #     if ans == "1":
        #         newMet = Metabolite(
        #             id=cpd['KEGG_ID'],
        #             name=cpd['NAME_SHORT'],
        #             formula=cpd['FORMULA'],
        #             compartment='c',
        #         )
        #         new_model.add_metabolites([newMet])
        #         print(f"Added {newMet.id} to the new model.")
        #         break
        #     elif ans == "0":
        #         break
        #     else:
        #         continue

    # On each compartment, make a dictionary binding formulas to metabolite ids for reaction lookup
    lookup_dict = {}
    for _, cpd in kegg_compound_df.iterrows():
        lookup_dict[cpd['KEGG_ID']] = cpd['FORMULA']

    # Create a rxn id for each reaction based on the reactants and products, same as line 101
    # rxn_lookup_dict = {}
    # for rxn in model.reactions:
    #     # Get the formulas for each metabolite in the reaction
    #     reactants = get_rxn_metabolites(rxn, 'reactants')
    #     products = get_rxn_metabolites(rxn, 'products')
    #     # Create a unique id based on the sorted formulas
    #     fid = '+'.join(sorted(reactants)) + '+' + '+'.join(sorted(products))
    #     # Add to lookup dictionary
    #     rxn_lookup_dict[rxn.id] = fid

    # Create a dictionary for compartment lookup    
    compartment_dict = {}
    for met in new_model.metabolites:
        if met.compartment not in compartment_dict:
            compartment_dict[met.compartment] = {}
        compartment_dict[met.compartment][met.formula] = met

    # iterate through dataframe to add rxns in the same manner
    list_rxns: list[tuple[str,str,Reaction]] = [(rxn.id,rxn.name,rxn) for rxn in model.reactions]
    for id, rxn in kegg_rxn_df.iterrows():
        print(rxn['NAME'], f". Most similar:\n\t{"\n\t".join(list(map(lambda x: f"{x[1]} ({list(map(lambda y: y[0].name, x[2].metabolites.items()))}) ({str(x[2].compartments)})", sort_by_similarity(list_rxns, rxn['NAME'])))[:5])}", end='\n')

        # # Create rxn id by sorting the reactants' and products' formulas (then concatenate)
        # fid = '+'.join(sorted(rxn['REACTANTS'].split('+'))) + '+' + '+'.join(sorted(rxn['PRODUCTS'].split('+')))
        # # add the reaction to 'c' compartment whenever there's a missing id in already existing reactions
        # if fid in rxn_lookup_dict.values(): continue

        while True:
            ans = input("1 - Add Rxn | 0 - Ignore\n")

            if ans == "1":
                reactants = rxn['REACTANTS'].split('+')
                products = rxn['PRODUCTS'].split('+')
                # Get the formulas for each from the lookup dictionary
                r_formulas = [lookup_dict[met.strip()] for met in reactants if met.strip() in lookup_dict]
                p_formulas = [lookup_dict[met.strip()] for met in products if met.strip() in lookup_dict]
                # Get the correct ids from the dictionary lookup
                r_ids = {compartment_dict['c'][formula]: -1 for formula in r_formulas if formula in compartment_dict['c']}
                p_ids = {compartment_dict['c'][formula]: 1 for formula in p_formulas if formula in compartment_dict['c']}
                # Concatenate the dictionaries
                mets_dict = {**r_ids, **p_ids}
                # print(mets_dict)
                # Add the metabolites to reaction
                newRxn = Reaction(
                    id=id,
                    name=rxn['NAME'],
                    subsystem=rxn['PATHWAYS']
                )
                # Important info for reaction
                newRxn.reversibility = True # Add rxns in db are reversible it seems
                newRxn.lower_bound = -1000
                newRxn.upper_bound = 1000
                # Add the metabolites to the reaction
                newRxn.add_metabolites(mets_dict)
                # Add the reaction to the model
                new_model.add_reactions([newRxn])
                print(f"Added {newRxn.id} to the new model.\n")
                break
            elif ans == "0":
                break
            else:
                continue
    
    print(f"New model has {len(new_model.metabolites)} metabolites and {len(new_model.reactions)} reactions.")
    print(f"Old model has {len(model.metabolites)} metabolites and {len(model.reactions)} reactions.")

    # Export new_model to sbml
    io.write_sbml_model(new_model, "./data/altered/kegg_gapfill_model.xml")

# All reactions seem to have no coefficient, confirm
# Double check that all metabolites and reactions are added to the correct compartments
# Test new model for feasibility
# Save the new model