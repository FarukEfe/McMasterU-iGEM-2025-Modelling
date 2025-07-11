from data.altered.parser import parse_obj
from data.altered.model import *

if __name__ == "__main__":
    path ='./data/altered/rxns.json'
    rxns: list[Rxn] = parse_obj(path)
    for rxn in rxns:
        print(rxn)
