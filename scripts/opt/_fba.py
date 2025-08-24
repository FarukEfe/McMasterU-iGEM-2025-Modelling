from cobra import io, Model, Solution
from cobra.flux_analysis import pfba
import escher
import argparse, os, sys

from cobra.util.solver import linear_reaction_coefficients

def flux_balance_analysis(
    model: Model,
    loopless: bool,
    objectives: list[str],
    is_pfba: bool = False,
    reactions: list[str] = None,
    pfba_factor: float = 1.1,
    fraction_of_optimum: float = 1.0,

):
    """
    Run Flux-Balance Analysis on the model for the provided objectives.
    Makes the assumption that all stated objectives in `objectives: list[str]` are equally important.

    Args:
        model (Model): The metabolic model to analyze.
        loopless (bool): Whether to use loopless FBA.
        pfba (bool): Whether to use parsimonious FBA.
        objectives (list[str]): The list of objectives to optimize.
        reactions (list[str], optional): The list of reactions to include in the analysis.
        pfba_factor (float, optional): The factor to use for pfba. Defaults to 1.1.
        fraction_of_optimum (float, optional): The fraction of the optimum to use. Defaults to 1.0.

    Returns:
        Solution: The optimized solution for the provided objectives. For more see `cobra.Solution`
    """
    assert len(objectives) > 0, "No objectives provided."
    assert all([obj in [rxn.id for rxn in model.reactions] for obj in objectives]), "Some objectives not found in model."
    
    solution = None
    if is_pfba:
        objective_obj = {model.reactions.get_by_id(obj): 1.0 / len(objectives) for obj in objectives}
        solution = pfba(
            model,
            fraction_of_optimum=fraction_of_optimum,
            objective=objective_obj,
        )
    else:
        # Set model objective
        for rxn in model.reactions:
            rxn.objective_coefficient = 0.0

        for obj in objectives:
            model.reactions.get_by_id(obj).objective_coefficient = 1.0 / len(objectives)
        
        solution = model.optimize(raise_error=True)
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
    parser.add_argument('-o', '--objectives')
    args = parser.parse_args()

    # # Print arguments
    # print(f"Loading model from: {args.sbmlpath}")
    # print(f"Destination directory: {args.dest}")

    # Model Import
    model, error = io.validate_sbml_model(args.sbmlpath)

    if not model:
        print(f'Error loading model: {error}')
        sys.exit(1)
    
    objectives = args.objectives.split(',') if args.objectives else []
    if len(objectives) > 0:
        
        solution = None
        try:
            # Run flux-balance analysis
            solution = flux_balance_analysis(model, loopless=False, is_pfba=args.pfba, objectives=objectives)
        except Exception as e:
            print(f"Error during FBA: {e}")
            sys.exit(1)

        # File name & destination
        file_name: str = os.path.split(args.sbmlpath)[-1].split('.')[0]
        dest_final: str = os.path.join(args.dest, "+".join(objectives))

        # Save to destination
        if not os.path.exists(dest_final): os.makedirs(dest_final)
        export_path = os.path.join(dest_final, f'{file_name}.csv')
        solution.fluxes.to_csv(export_path)
        exit(0)
    
    print("No objectives provided, aborting FBA...")
    exit(1)