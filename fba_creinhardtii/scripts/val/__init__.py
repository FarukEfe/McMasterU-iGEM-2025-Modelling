import cobra.io as io, argparse, requests
from cobra.manipulation.validate import check_mass_balance, check_metabolite_compartment_formula
from cobra.flux_analysis import add_loopless, find_blocked_reactions
from scripts.helpers.energy_cycles import energy_cycles_flux, find_egcs_null_space
from cobra.core import Model, Reaction, Metabolite

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

    # Basic Check
    assert len(model.reactions) > 0, "Not reactions found."
    assert len(model.metabolites) > 0, "No metabolites found."
    assert len(model.genes) > 0, "No genes found."