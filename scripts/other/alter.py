# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite
# Toolbox
from scripts.helpers.tools import get_rxn_metabolites, sort_by_similarity
# Other
import os, sys, argparse
import pandas as pd
from json import loads

# Format a compound to split the coefficient
def split_coef(coef: str) -> tuple[int, str]:
    try:
        return int(coef[:1]), coef[1:]
    except:
        return 1, coef

def split_coef_reac(coef: str) -> tuple[int, str]:
    res = split_coef(coef)
    return -1 * res[0], res[1]

def alter(argpath: str):

    model, error = io.validate_sbml_model(argpath, validate=True)
    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)

    # Extract model name
    model_name = os.path.split(args.sbmlpath)[-1].split('.')[0]

    # Import alteration tables for reactions and compounds
    rxns_df = pd.read_csv("./data/altered/tables/stable/reactions_list.csv")
    cpds_df = pd.read_csv("./data/altered/tables/stable/compounds_list.csv")

    # Import blueprint.json file from data alterations and parse into a dictionary
    bp_path = "./data/altered/blueprint.json"
    if not os.path.exists(bp_path): # Will never happen in the current setup
        print(f"Blueprint file not found at {bp_path}. Exiting...")
        sys.exit(1)
    
    blueprint = []
    with open(bp_path, 'r') as f:
        blueprint = loads(f.read())

    
    # For compound in the cpds_df table, add the compounds
    # We add all compounds since there's not that many, and unused ones will simply not get any flux
    for cpd in cpds_df['ID'].values:
        # Get the fields of ID, Name, and Formula, and separate into variables
        cpd_name = cpds_df[cpds_df['ID'] == cpd]['NAME'].values[0]
        cpd_formula = cpds_df[cpds_df['ID'] == cpd]['FORMULA'].values[0]
        # Debug
        # print(cpd,cpd_name,cpd_formula)
        # Make new metabolite and save to model
        newMet = Metabolite(
            id=cpd,
            name=cpd_name,
            formula=cpd_formula,
            compartment='c',
        )
        model.add_metabolites([newMet])
    
    for item in blueprint:

        print(f"\n\nProcessing item: {item['name']}")
        new_model = model.copy()

        # List of compound references
        for _, row in rxns_df.iterrows():

            # Ignore if blueprint item doesn't contain the enzyme ec
            if not row['EC'] in item['ec']: continue

            # Get list of metabolites involved in the reaction
            reactants = list(map(split_coef_reac, row['REACTANTS'].split('+')))
            products = list(map(split_coef, row['PRODUCTS'].split('+')))
            compounds = [*reactants, *products]

            # Get metabolite objects for the dictionary to add in reaction
            add_mets = {}
            for coef, cpd in compounds:
                # print(cpd)
                met_ref = new_model.metabolites.get_by_id(cpd)
                add_mets[met_ref] = coef

            print(row['ID'], row['NAME'], add_mets)
            newRxn = Reaction(
                id=row['ID'],
                name=row['NAME'],
            )
            newRxn.lower_bound = 0
            newRxn.upper_bound = 1000  # Set a high upper bound for the reaction
            newRxn.add_metabolites(add_mets)
            new_model.add_reactions([newRxn])
        
        # Print out results
        print(f"New model {item['name']} has {len(new_model.reactions)} reactions.")
        print(f"Control model {model_name} had {len(model.reactions)} reactions.")
        
        # Save altered model to repo
        save_path = f"./data/altered/xmls/{model_name}"
        if not os.path.exists(save_path): os.makedirs(save_path)
        io.write_sbml_model(new_model, os.path.join(save_path, f"{item['name']}.xml"))

        _ = input("Model Saved. Press Enter to continue...")
        os.system('cls') # Clear terminal to avoid clump


if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    args = parser.parse_args()

    alter(args.sbmlpath)