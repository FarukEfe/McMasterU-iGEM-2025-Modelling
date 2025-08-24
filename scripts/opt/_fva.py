# FVA
    # Run FVA
    # List blocked reactions
    # Export flux ranges
from cobra import io
import argparse, os
import warnings, sys

from cobra.core import Model, Reaction, Metabolite
from cobra.flux_analysis import flux_variability_analysis

def run_flux_variability_analysis(
        model: Model,
        loopless: bool = True,
        pfba_factor: float = 1.1,
        fraction_of_optimum: float = 1.0,
        objectives: list[str] = None,
        reactions: list[str] = None
    ):
    """
    Perform flux variability analysis on the given model.

    Args:
        model (Model): The metabolic model to analyze.
        reactions (list[str], optional): A list of reaction IDs to include in the analysis.

    Returns:
        pd.DataFrame: A DataFrame containing the flux ranges for each reaction.
    """

    # Assert rules for job success
    assert objectives is not None and len(objectives) > 0, "No objectives provided."
    assert not loopless or (reactions is not None and len(reactions) > 0), "No reactions provided for loopless FVA."

    # Set objective coefficients
    for rxn in model.reactions:
        rxn.objective_coefficient = 0.0
    
    for obj in objectives:
        model.reactions.get_by_id(obj).objective_coefficient = 1.0 / len(objectives)

    # cobra.flux_analysis.flux_variability_analysis
    solution = flux_variability_analysis(
        model,
        loopless=loopless,
        pfba_factor=pfba_factor,
        fraction_of_optimum=fraction_of_optimum,
        reaction_list=reactions,
        processes=None
    )
    return solution

if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    parser.add_argument('-d', '--dest')
    parser.add_argument('-p', '--pfba', action='store_true')
    parser.add_argument('-l', '--loopless', action='store_true')
    parser.add_argument('-o', '--objectives')
    parser.add_argument('-r', '--reactions')
    args = parser.parse_args()

    print("Model import from SBML file... {}".format(args.sbmlpath))

    # Model Import
    model, error = io.validate_sbml_model(args.sbmlpath)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)

    # r: Reaction = model.reactions.get_by_id("SS")
    # r.objective_coefficient = 1.0
    flux_ranges = None
    objectives = args.objectives.split(',') if args.objectives else None
    reactions = args.reactions.split(',') if args.reactions else None

    if not objectives or len(objectives) == 0:
        print("No objectives provided. Exiting...")
        sys.exit(1)

    try:
        flux_ranges = run_flux_variability_analysis(
            model,
            loopless=args.loopless,
            pfba_factor=1.1 if args.pfba else None,
            objectives=objectives,
            reactions=reactions
        )
    except Exception as e:
        print(f"Error during flux variability analysis: {e}")
        sys.exit(1)

    file_name: str = os.path.split(args.sbmlpath)[-1].split('.')[0]
    output_dest: str = os.path.join(args.dest, file_name)
    if not os.path.exists(output_dest): os.makedirs(output_dest)

    export_path = os.path.join(output_dest, f"{'+'.join(objectives)}_fva.csv")
    flux_ranges.to_csv(export_path)
    exit(0)
