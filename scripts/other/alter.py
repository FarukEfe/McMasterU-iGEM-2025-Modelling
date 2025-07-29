# Cobra package
from cobra import io
from cobra.core import Reaction, Metabolite
# Toolbox
from scripts.helpers.tools import get_rxn_metabolites, sort_by_similarity
# Parse
from data.altered.model import *
from data.altered.parser import parse_obj
# Other
import os, sys

if __name__ == "__main__":

    # Get initial model path (or name) as input from command line

    pth = "./data/raw/iBD1106.xml"

    model, error = io.validate_sbml_model(pth, validate=True)

    if not model:
        print('No model recognized. Exiting...')
        sys.exit(1)
    
    