from cobra import io
import escher
import argparse, os
from scripts.helpers.sort_similarity import sort_by_similarity

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

    search = input("Search for objective: ")
    res = sort_by_similarity([(rxn.id, rxn.name) for rxn in model.reactions], 'cycloartenol')[:30]
    print('Top 30 Most Similar Objectives: ')
    for i in range(0,len(res)): 
        print(f'{res[i][0]}: {res[i][1]}')

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

    # print("Saving vis...")
    # # Network Builder
    # builder = escher.Builder(
    #     reaction_data=soln.fluxes,
    #     model=model,
    #     map_name='c_reinhardtii.core_metabolism'  # Replace with a valid map for your organism
    # )
    # builder.save_html(os.path.join(dest_final, 'example.html'))

    print("Saving vis...")
    # Save Model to JSON
    json_path = os.path.join(dest_final, f'{file_name}.json')
    print(export_path)
    io.save_json_model(model, json_path)