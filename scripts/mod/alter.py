# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite
# Other
import os, sys, argparse
import pandas as pd
from json import loads

# Toolbox
from scripts.helpers.tools import split_coef, split_coef_reac
from scripts.helpers.model import add_single_gene_reaction_pair, met_in_model

def alter(argpath: str, chloroplast: bool):

    ref, _ = io.validate_sbml_model(argpath, validate=True)
    if not ref:
        print('No model recognized. Exiting...')
        sys.exit(1)

    # Extract model name
    ref_name = os.path.split(args.sbmlpath)[-1].split('.')[0]

    # Import alteration tables for reactions and compounds
    rxns_df = pd.read_csv("./data/altered/tables/stable/reactions.csv")
    cpds_df = pd.read_csv("./data/altered/tables/stable/compounds.csv")

    # Load blueprint of alterations
    bp_path = "./data/altered/blueprint.json"
    if not os.path.exists(bp_path): # Will never happen in the current setup
        print(f"Blueprint file not found at {bp_path}. Exiting...")
        sys.exit(1)
    
    blueprint = []
    with open(bp_path, 'r') as f:
        blueprint = loads(f.read())
    
    # Add compounds to reference from cpds_df
    for cpd in cpds_df['ID'].values:
        # Get the fields of ID, Name, and Formula, and separate into variables
        cpd_id = cpd
        cpd_name = cpds_df[cpds_df['ID'] == cpd]['NAME'].values[0]
        cpd_formula = cpds_df[cpds_df['ID'] == cpd]['FORMULA'].values[0]
        cpd_comp = 'c'

        if chloroplast:
            cpd_comp = 'h'
            cpd_id = cpd[:-2] + "_h"

        # Make new metabolite and save to model
        newMet = Metabolite(
            id=cpd_id,
            name=cpd_name,
            formula=cpd_formula,
            charge=0, # Default charge (could change later)
            compartment=cpd_comp,
        )
        ref.add_metabolites([newMet])
    
    # Build each blueprint iteration
    for item in blueprint:

        print(f"\n\nProcessing item: {item['name']}")
        model = ref.copy()
        model.name = ref_name + "_" + item['name']

        if chloroplast:
            # Add aacoa_h <--> aacoa_c reaction for safety

            # ACCOAh = model.metabolites.get_by_id('accoa_h')
            # CoAh = model.metabolites.get_by_id('coa_h')

            # Add Acetoacetyl-CoA for chloroplast
            AACOAc = model.metabolites.get_by_id('aacoa_c')
            AACOAh = Metabolite(
                id='aacoa_h',
                name='Acetoacetyl-CoA',
                formula=AACOAc.formula,
                charge=0,
                compartment='h',
            )
            model.add_metabolites([AACOAh])
            # Add the transport reaction
            add_single_gene_reaction_pair(
                model=model,
                gene_id='AACOAth',
                reaction_id='AACOAth',
                reaction_name='Acetoacetyl-CoA:CoA antiporter, Chloroplast',
                reaction_subsystem='Transport, chloroplast',
                metabolites=[(-1, AACOAc.id), (1, AACOAh.id)],
                reversible=True
            )

        # Add reactions in blueprint iteration
        for _, row in rxns_df.iterrows():

            # Ignore if blueprint item doesn't contain the enzyme ec
            if not row['EC'] in item['ec']: continue

            # Get list of metabolites involved in the reaction
            reactants = list(map(split_coef_reac, row['REACTANTS'].split('+')))
            products = list(map(split_coef, row['PRODUCTS'].split('+')))
            mets = [*reactants, *products]

            if chloroplast and row['EC'] not in ["2.5.1.21", "1.14.14.17"]:
                mets = list(map(lambda x: (x[0], x[1][:-2] + "_h"), mets))

            # print(mets)

            # Add reaction to model copy
            add_single_gene_reaction_pair(
                model=model,
                gene_id=row['GENE_ID'],
                reaction_id=row['ID'],
                reaction_name=row['NAME'],
                reaction_subsystem=row['PATHWAY'],
                metabolites=mets
            )
        
        # Print out results
        print(f"New model {model.name} has {len(model.reactions)} reactions.")
        print(f"Control model {ref_name} had {len(ref.reactions)} reactions.")

        # Save altered model to repo
        save_path = f"./data/altered/xmls/{ref_name}" + ("/h" if chloroplast else "")
        if not os.path.exists(save_path): os.makedirs(save_path)
        io.write_sbml_model(model, os.path.join(save_path, f"{item['name']}.xml"))

        _ = input("Model Saved. Press Enter to continue...")
        os.system('cls') # Clear terminal to avoid clump


if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    parser.add_argument('-ch', '--chloroplast', action='store_true')
    args = parser.parse_args()

    alter(args.sbmlpath, args.chloroplast)