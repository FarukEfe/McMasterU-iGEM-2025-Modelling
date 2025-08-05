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
    res = coef.split("C")
    res[1] = "C" + res[1]
    res[0] = 1 if res[0] == "" else int(res[0])
    return tuple(res)
    
def split_coef_reac(coef: str) -> tuple[int, str]:
    res = split_coef(coef)
    return -1 * res[0], res[1]

if __name__ == "__main__":

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

    # Extract model name
    model_name = os.path.split(args.sbmlpath)[-1].split('.')[0]

    # Import alteration tables for reactions and compounds
    rxns_df = pd.read_csv("./data/altered/tables/reactions_list.csv")
    cpds_df = pd.read_csv("./data/altered/tables/compounds_list.csv")

    # Import blueprint.json file from data alterations and parse into a dictionary
    bp_path = "./data/altered/blueprint.json"
    if not os.path.exists(bp_path): # Will never happen in the current setup
        print(f"Blueprint file not found at {bp_path}. Exiting...")
        sys.exit(1)
    
    blueprint = []
    with open(bp_path, 'r') as f:
        blueprint = loads(f.read())
    
    c_add_count = 0
    for item in blueprint:

        print(f"\n\nProcessing item: {item['name']}")
        new_model = model.copy()

        # List of compound references
        compound_ref = {}
        for id, row in rxns_df.iterrows():

            # Ignore if blueprint item doesn't contain the enzyme ec
            if not row['EC'] in item['ec']:
                continue

            # Get list of metabolites involved in the reaction
            # print(f"\n\nProcessing EC {row['EC']} with reactions: {row['ID']}")
            reactants = list(map(split_coef_reac, row['REACTANTS'].split('+')))
            products = list(map(split_coef, row['PRODUCTS'].split('+')))
            compounds = [*reactants, *products]
            # print(compounds)

            add_mets = {}
            for coef, cpd in compounds:

                # Add compound if previously discovered
                if cpd in compound_ref.keys():
                    print(f"Compound {cpd} already exists in compound_ref. Skipping...")
                    met_ref = compound_ref[cpd]
                    add_mets[met_ref] = coef
                    continue

                # Try to find compound match based on formula and compartment
                formula = cpds_df[cpds_df['ID'] == cpd]['FORMULA'].values[0]
                if pd.isna(formula):
                    print(f"Compound {cpd} has no formula in compounds_list.csv. Skipping...")
                    continue

                # Search for existing compound in the model
                # print(f"Processing compound {cpd} with formula: {formula}")
                hits = [met for met in new_model.metabolites if met.compartment == 'c' and met.formula == formula]
                # Create new compound if not found (should be the case for almost all compounds)
                if len(hits) == 0:

                    cpd_name = cpds_df[cpds_df['ID'] == cpd]['NAME'].values[0]

                    # Manually search, let user decide if it should be added or not
                    similars = sort_by_similarity([(met.id, met.name, met) for met in new_model.metabolites if met.compartment == 'c'], cpd_name)
                    print(f"Compound name: {cpd_name}.\nSimilar finds:\n\t", "\n\t".join(list(map(lambda x: str(x), similars[:8]))))

                    inp = input("Add or replace? (Type in component id to add, otherwise nothing)")

                    if inp != "":
                        # Add metabolite from model reference if user decides there's enough similarity
                        metRef = new_model.metabolites.get_by_id(inp)
                        compound_ref[cpd] = metRef
                        c_add_count += 1
                    else:
                        # Make a new metabolite for the model if user decides
                        print(f"Compound {cpd} not found in model. Adding...")
                        newMet = Metabolite(
                            id=cpd,
                            name=cpd_name,
                            formula=formula,
                            compartment='c',
                        )
                        new_model.add_metabolites([newMet])
                        compound_ref[cpd] = newMet
                        c_add_count += 1
                else:
                    compound_ref[cpd] = hits[0]
                # Add the metabolite associated with KEGG compound
                met_ref = compound_ref[cpd]
                add_mets[met_ref] = coef
            
            newRxn = Reaction(
                id=f"ALTERED_{row['ID']}",
                name=row['NAME'],
            )
            newRxn.add_metabolites(add_mets)
            new_model.add_reactions([newRxn])
        
        # Print out results
        print(f"New model {item['name']} created with {len(new_model.metabolites)} metabolites and {len(new_model.reactions)} reactions.")
        print(f"Control model {model_name} had {len(model.metabolites)} metabolites and {len(model.reactions)} reactions.")
        _ = input("Press Enter to continue...")
        
        save_path = f"./data/altered/xmls/{model_name}"
        if not os.path.exists(save_path): os.makedirs(save_path)
        io.write_sbml_model(new_model, os.path.join(save_path, f"{item['name']}.xml"))
