from cobra import io, Reaction, Model, Metabolite
from scripts.helpers.tools import find_rxns_with_metabolites, sort_by_similarity

import csv
"""
This script is to see what reactions in the flux that are related to the ergosterol synthesis have 0 flux (don't produce or missing components)

The below are some metabolites we find the reactions for and look them up by similarity in the optimized flux table for biomass.
"""
if __name__ == "__main__":

    _list = [
        'M_7dhchsterol_c',
        'M_44mctr_c',
        'M_44mzym_c',
        'M_4mzym_c',
        'M_4mzym_DASH_int1_c',
        'M_4mzym_DASH_int2_c'
    ]
    csv_path = './results/fluxes/iBD1106/Biomass_Chlamy_auto.csv'

    model, error = io.validate_sbml_model("./data/raw/iBD1106.xml")

    if model:

        flux_list = []

        try:
            with open(csv_path, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    flux_list.append(tuple(row))
        except FileNotFoundError:
            print('File for flux path not found.')
            exit(1)
        except Exception as e:
            print(f'Error occured: {str(e)}')
            exit(1)

        rxns: list[Reaction] = find_rxns_with_metabolites(model, _list)
        print(rxns)

        for rxn in rxns:
            most_common = sort_by_similarity(flux_list, rxn.id)[:5]
            print('\n'.join(most_common))
            _ = input(f'Results for {rxn.id}.Press enter to continue ...')