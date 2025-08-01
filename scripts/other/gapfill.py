# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite, Model
# Toolbox
from scripts.helpers.tools import get_rxn_metabolites, sort_by_similarity
# Other
import os, sys, argparse
import pandas as pd

if __name__ == "__main__":

    # Get initial model path (or name) as input from command line

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    args = parser.parse_args()

    model, error = io.validate_sbml_model(args.sbmlpath, validate=True)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)
    
    # Define model name from file input
    model_name = os.path.split(args.sbmlpath)[-1].split('.')[0]
    print(f"Model name: {model_name}")
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
    list_mets: list[tuple[str,str,Metabolite]] = [(met.id, met.name, met) for met in new_model.metabolites]
    for _, cpd in kegg_compound_df.iterrows():
        searches = sort_by_similarity(list_mets, cpd['NAME_SHORT'])
        print(cpd['NAME_SHORT'], f"({cpd['FORMULA']})", f". Most similar:\n\t{"\n\t".join(list(map(lambda x: f"{x[1]} ({x[2].formula}) ({x[2].compartment})", searches))[:5])}", end='\n')

        # Formulas of compounds already in the cytoplasm of the new_model (need to recompute since additions are being made)
        list_forms: list[str] = [met.formula for met in new_model.metabolites if met.compartment == 'c']

        if cpd['FORMULA'] in list_forms:
            hit = [met for met in new_model.metabolites if (met.compartment == 'c' and met.formula == cpd['FORMULA'])][0]
            print(f"Found matching compound for {cpd['NAME_SHORT']} ({cpd['FORMULA']}):\n\t{hit.id}, {hit.name}, {hit.formula}, {hit.compartment}")
        else:
            print(f"No matches. Adding to model")
            newMet = Metabolite(
                id=cpd['KEGG_ID'],
                name=cpd['NAME_SHORT'],
                formula=cpd['FORMULA'],
                compartment='c',
            )
            new_model.add_metabolites([newMet])
            print(f"Added {newMet.id} to the new model.")

        _ = input("Waiting to continue...")

    # On each compartment, make a dictionary binding formulas to metabolite ids for reaction lookup
    lookup_dict = {}
    for _, cpd in kegg_compound_df.iterrows():
        lookup_dict[cpd['KEGG_ID']] = cpd['FORMULA']

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
    save_path = f"./data/kegg/xmls/{model_name}"
    if not os.path.exists(save_path): os.makedirs(save_path)
    io.write_sbml_model(new_model, os.path.join(save_path, f"KEGG_{model_name}_GAPFILL.xml"))