# FVA
    # Run FVA
    # List blocked reactions
    # Export flux ranges
from cobra import io
import argparse, os

from cobra.flux_analysis import flux_variability_analysis

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
    args = parser.parse_args()

    # Model Import
    model, error = io.validate_sbml_model(args.sbmlpath)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(0)

    flux_ranges = flux_variability_analysis(model)

    for reaction_id, flux_range in flux_ranges:
        print(f"{reaction_id}: Minimum = {flux_range['minimum']}, Maximum = {flux_range['maximum']}")
    
