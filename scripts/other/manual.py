from cobra import io
from cobra.core import Metabolite, Reaction, Model
import os, argparse
import pandas as pd

def split_coef(inp: str) -> tuple[int, str]:
    try:
        coef, cpd = inp[:1], inp[1:]
        coef = 1 if coef == "" else int(coef)
        return coef, cpd
    except:
        return 1, inp

def split_coef_reac(inp: str) -> tuple[int, str]:
    res = split_coef(inp)
    return -1 * res[0], res[1]

if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    args = parser.parse_args()

    old, err = io.validate_sbml_model(args.sbmlpath)
    if not old:
        print(f"Error loading model: {err}")
        exit(1)

    model = old.copy()
    
    # Import the manual reactions and compounds tables
    reactions_df = pd.read_csv("./data/manual/reactions.csv")
    compounds_df = pd.read_csv("./data/manual/compounds.csv")

    print("Adding compounds ...\n")
    for index, row in compounds_df.iterrows():

        print(f"Cpd: {row['ID']}, {row['NAME_SHORT']}")
        newMet = Metabolite(
            id=row['ID'],
            name=row['NAME_SHORT'],
            formula=row['FORMULA'],
            compartment='c',
        )
        model.add_metabolites([newMet])

    for index, row in reactions_df.iterrows():
        print(f"Rxn: {row['ID']}, {row['NAME']}")
        reactants = list(map(split_coef_reac, row['REACTANTS'].split('+')))
        products = list(map(split_coef, row['PRODUCTS'].split('+')))
        compounds = [*reactants, *products]
        
        add_mets = {}
        for coef, cpd in compounds:
            met_ref = model.metabolites.get_by_id(cpd)
            if met_ref:
                add_mets[met_ref] = coef
            # print(f"Adding {coef} of {cpd}") # TEST THIS!!!

        # Create reaction
        newRxn = Reaction(
            id=row['ID'],
            name=row['NAME'],
            subsystem=row['PATHWAY']
        )
        newRxn.reversibility = row['REVERSIBLE'] == 'True'
        newRxn.lower_bound = -1000 if row['REVERSIBLE'] == 'True' else 0
        newRxn.upper_bound = 1000
        # Add compounds to rxn
        newRxn.add_metabolites(add_mets)
        # Add rxn to model
        model.add_reactions([newRxn])

    print(f"\n\nFinal model has {len(model.metabolites)} metabolites and {len(model.reactions)} reactions.")
    print(f"Old model has {len(old.metabolites)} metabolites and {len(old.reactions)} reactions.")

    save_path = "./data/manual/xmls"
    save_file = os.path.join(save_path, f"MNL_{model.id}_GAPFILL.xml")
    if not os.path.exists(save_path): os.makedirs(save_path)
    io.write_sbml_model(model, save_file)
