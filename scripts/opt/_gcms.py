import argparse, json, os, sys
import numpy as np, pandas as pd
from typing import TypedDict, Literal

from cobra import io, Model
from scripts.opt._fba import run_flux_balance_analysis
from scripts.opt._fva import run_flux_variability_analysis


if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_gcms',
        description='Sterol profile comparison to GCMS experiments under stress conditions.'
    )
    parser.add_argument('--sbmlpath', required=True, help='Path to the input SBML model file.')
    parser.add_argument('--outdir', default="./res/gcms", help='Directory to save the GCMS results.')
    args = parser.parse_args()
    