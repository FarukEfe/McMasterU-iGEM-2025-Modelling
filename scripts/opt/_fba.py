from cobra import io
import escher
import argparse, os
from scripts.helpers.sort_similarity import sort_by_similarity
from cobra.util.solver import linear_reaction_coefficients

import warnings, sys
warnings.filterwarnings('ignore')
sys.stderr = open(os.devnull, 'w') # Redirect stderr to null to suppress warnings

if __name__ == "__main__":
    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    parser.add_argument('-d', '--dest')
    args = parser.parse_args()

    # Model Import
    model, error = io.validate_sbml_model(args.sbmlpath)

    if not model:
        print(f'Error loading model: {error}')
        sys.exit(1)

    search = input("Search for objective: ")
    res = sort_by_similarity([(rxn.id, rxn.name) for rxn in model.reactions], search)[:30]
    print('Top 30 Most Similar Objectives: ')
    for i in range(0,len(res)): 
        print(f'{res[i][0]}: {res[i][1]}')

    # Saw this here: https://groups.google.com/g/cobra-pie/c/IrXS8Xa06Js/m/_I3EmBZBAgAJ?pli=1
    # Will look into this later
    linear_reaction_coefficients(model)
    # Pre-saved objectives that are relevant to our project
    objectives = ['Biomass_Chlamy_mixo','Biomass_Chlamy_auto','SS','CAS']
    rxn = input('\nChoose objective. Some relevant ones are ' + ' -- '.join(objectives) + '\nChoose: ')
    model.objective = rxn
    soln = model.optimize()

    print("Saving results...")
    # Save Results
    file_name: str = os.path.split(args.sbmlpath)[-1].split('.')[0]
    dest_final: str = os.path.join(args.dest, file_name)
    if not os.path.exists(dest_final): os.mkdir(dest_final)
    export_path = os.path.join(dest_final, f'{rxn}.csv')
    soln.fluxes.to_csv(export_path)