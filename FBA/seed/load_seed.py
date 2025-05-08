import os, json, cobra
from cobra import Model, Reaction, Metabolite


if __name__ == "__main__":

    sbml_path = os.path.join(os.getcwd(), 'fba', 'seed', 'model', 'seed_model.sbml')

    if not os.path.exists(sbml_path): 
        print('couldn\'t find path, aborting...')
        exit(0)

    print('path exists, compiling...')

    (model, error) = cobra.io.validate_sbml_model(sbml_path)

    for k in error.keys():
        if len(error[k]) > 0:
            print(f"{k}: {error[k]}")
    else:
        for met in model.metabolites:
            print(met.name)

        print(len(model.metabolites))
        print(len(model.reactions))