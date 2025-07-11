from fuzzywuzzy import fuzz
from cobra import Reaction, Model, Metabolite, io
import numpy as np
from builtins import map

def get_rxn_metabolites(reaction_id: str, model: Model) -> tuple[list[Metabolite], list[int]]:

    rxn = model.reactions.get_by_id(reaction_id)

    mets, coefs = [], []
    for met, coef in rxn.metabolites.items():
        if coef != 0:
            mets.append(met)
            coefs.append(coef)
    return mets, coefs


def sort_by_similarity(strings: list[tuple[str,str]], ref: str):
    return sorted(strings, key=lambda s: max(fuzz.ratio(ref, s[0]), fuzz.ratio(ref, s[1])), reverse=True)