from cobra import io
from cobra.core import Metabolite, Reaction, Model
import os, argparse
import pandas as pd

from scripts.helpers.model import add_single_gene_reaction_pair
from scripts.helpers.tools import split_coef, split_coef_reac

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
    # Get file name
    model_name = os.path.splitext(os.path.basename(args.sbmlpath))[0]

    # Import the manual reactions and compounds tables
    reactions_df = pd.read_csv("./data/fill/reactions.csv")
    compounds_df = pd.read_csv("./data/fill/compounds.csv")

    print("Adding compounds ...\n")
    for index, row in compounds_df.iterrows():

        # print(f"Cpd: {row['ID']}, {row['NAME_SHORT']}")
        newMet = Metabolite(
            id=row['ID'],
            name=row['NAME_SHORT'],
            formula=row['FORMULA'],
            charge=row['CHARGE'],  # Default charge (could change later)
            compartment='c',
        )
        model.add_metabolites([newMet])

    for index, row in reactions_df.iterrows():

        # Get reactants x products
        reactants = list(map(split_coef_reac, row['REACTANTS'].split('+')))
        products = list(map(split_coef, row['PRODUCTS'].split('+')))
        # Add reaction to list
        add_single_gene_reaction_pair(
            model=model,
            gene_id=row['GENE_ID'],
            reaction_id=row['ID'],
            reaction_name=row['NAME'],
            reaction_subsystem=row['PATHWAY'],
            metabolites=[*reactants, *products]
        )

    print(f"\n\nFinal model has {len(model.metabolites)} metabolites and {len(model.reactions)} reactions.")
    print(f"Old model has {len(old.metabolites)} metabolites and {len(old.reactions)} reactions.")

    save_path = "./data/fill/xmls"
    os.makedirs(save_path, exist_ok=True)
    save_file = os.path.join(save_path, f"MNL_{model_name}_GAPFILL.xml")
    io.write_sbml_model(model, save_file)
