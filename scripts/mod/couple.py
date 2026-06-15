from cobra import io
from cobra.core import Metabolite, Reaction, Gene, Model
import os, argparse, sys

def couple_biomass(args):
    
    # Load Model
    ref, _ = io.validate_sbml_model(args.sbmlpath, validate=True)
    if not ref:
        raise ValueError('No model recognized. Exiting...')

    # Copy new instance
    new = ref.copy()

    # Couple biomass to ergosterol pathway
    biomass_auto = new.reactions.get_by_id('Biomass_Chlamy_auto')
    biomass_mixo = new.reactions.get_by_id('Biomass_Chlamy_mixo')
    biomass_hetero = new.reactions.get_by_id('Biomass_Chlamy_hetero')

    # Define new pool sterol metabolite
    sterol_pool = Metabolite(
        id='sterol_pool_c',
        name='Sterol Pool Metabolite',
        charge=0,
        compartment='c'
    )
    new.add_metabolites([sterol_pool])

    # Add pool metabolite to biomass
    biomass_auto.add_metabolites({sterol_pool: -0.0034})
    biomass_mixo.add_metabolites({sterol_pool: -0.0034})
    biomass_hetero.add_metabolites({sterol_pool: -0.0034})

    # Coefficients in mmol/gDW (from Voshall 2021, total 3.4 nmol/mg DW)
    # i.e. 0.0034 mmol/gDW total ergosterol. 
    # Assume that pool is demanded at 100% in all biomass modes.
    sterol_coefficients = {
        'ergosterol_c':          -0.002142,   # 63%
        '7dhporiferasterol_c':   -0.000918,   # 27%
        'ergost7enol_c':         -0.000340,   # 10%
    }

    # Couple ergosterol
    for met_id, coef in sterol_coefficients.items():
        met = new.metabolites.get_by_id(met_id)
        rxn = Reaction(f'couple_{met_id}')
        rxn.add_metabolites({met: -1, sterol_pool: 1})
        rxn.bounds = (0, abs(coef))
        new.add_reactions([rxn])

    # Save new model
    os.makedirs(args.outdir, exist_ok=True)
    save_path = os.path.join(args.outdir, f"{os.path.basename(args.sbmlpath)}")
    io.write_sbml_model(new, save_path)
    print(f"New model with coupled biomass saved to {save_path}.")


if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='couple',
        description='Couple the biomass reaction to the ergosterol pathway.'
    )
    parser.add_argument('--sbmlpath', default="./data/fill/xmls/iCre1355_auto.xml", help='Path to the input SBML model file.')
    parser.add_argument('--outdir', default="./data/coupled/xmls", help='Directory to save the coupled model SBML file.')
    args = parser.parse_args()

    try:
        couple_biomass(args)
    except ValueError as error:
        print(error)
        sys.exit(1)
