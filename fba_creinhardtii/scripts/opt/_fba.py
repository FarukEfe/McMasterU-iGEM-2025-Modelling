from cobra import io
import argparse, os
from helpers.sort_similarity import sort_by_similarity

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
    for i in range(0,len(res), 3): 
        print(f'{res[i]}\t{res[i+1]}\t{res[i+2]}')

    # Pre-saved objectives that are relevant to our project
    objectives = ['Biomass_Chlamy_mixo','Biomass_Chlamy_auto','SS','CAS']
    rxn = input('Choose objective. Some relevant ones: ' + '\t'.join(objectives))
    model.objective = rxn
    soln = model.optimize()

    export_path = os.path.join(args.dest, 'fluxes', f'{rxn}.csv')
    soln.fluxes.to_csv(export_path)