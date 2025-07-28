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

    print("Model import from SBML file... {}".format(args.sbmlpath))

    # Model Import
    model, error = io.validate_sbml_model(args.sbmlpath)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)

    model.objective = "BIOMASS_Chlamy_auto"  # Set a default objective, can be changed later
    try:
        flux_ranges = flux_variability_analysis(model)
    except Exception as e:
        print(f"Error during flux variability analysis: {e}")
        sys.exit(1)

    print("idgaf")

    file_name: str = os.path.split(args.sbmlpath)[-1].split('.')[0]
    output_file = f"{file_name}_fva.csv"
    export_path = os.path.join('./results/ranges', output_file)
    with open(export_path, 'w') as f:
        for reaction_id, flux_range in flux_ranges.iterrows():
            f.write(f"{reaction_id}: Minimum = {flux_range['minimum']}, Maximum = {flux_range['maximum']}, Range = {flux_range['maximum'] - flux_range['minimum']}\n")
        # Save the file after writing
        f.close()
        print(f"Results saved to {export_path}")
