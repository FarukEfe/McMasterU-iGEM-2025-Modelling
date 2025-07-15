from cobra import io
import os, argparse
from enum import Enum
from cobra.core import Model, Reaction, Metabolite

from scripts.helpers.tools import sort_by_similarity

class NType(Enum):
    COMPOUND = True
    REACTION = False

class Node:

    def __init__(self, is_compound: bool, data: Metabolite | Reaction):
        self.type: NType = is_compound
        self.data = data


class DiGraph:

    # Initializer and readers

    def __init__(self, rxns: list[Reaction]):

        nodes_map: dict[str:Node] = {}
        edges: dict[str:str] = {}
        weight: dict[tuple[str,str]:int] = {}

        rxncount, metcount = 0, 0
        for rxn in rxns:
            # Create reaction node
            rxn_node = Node(is_compound=False, data=rxn)
            nodes_map[rxn.id] = rxn_node
            # Add metabolites to graph
            for item in rxn.metabolites.items():
                met, coef = item
                # Create metabolite node if not in graph
                if not (met.id in nodes_map.keys()):
                    c_node = Node(is_compound=True, data=met)
                    nodes_map[met.id] = c_node
                
                # Connect metabolite and reaction
                src, dest = rxn.id, met.id
                if coef < 0:
                    # Node for met is source to rxn
                    src, dest = met.id, rxn.id

                if src not in edges.keys():
                    edges[src] = [dest]
                else:
                    edges[src] = edges[src] + [dest]
                weight[(src,dest)] = abs(coef)
                metcount += 1
            rxncount += 1
            
        self.nodes, self.edges, self.weight, self.rxn_count, self.met_count = nodes_map, edges, weight, rxncount, metcount
    
    def get_node_count(self): return (self.rxn_count + self.met_count)
        
    def get_rxn_count(self): return self.rxn_count

    def get_met_count(self): return self.met_count

    # Debug

    def get_edges(self): return self.edges

    def get_weights(self): return self.weight

    def get_nodes(self): return self.nodes
        
    # Pathfinding

    def _get_dest(self, nid: str):
        return self.edges[nid]
    
    def find_sp(self, src: str):
        
        queue = [src]
        visits: list[str] = []

        while len(queue) > 0:

            n = queue[0]
            queue = queue[1:]
            visits.append(n)

            d = self._get_dest(n)
            for m in d:
                if m not in visits:
                    visits.append(m)
        
        return visits
                


if __name__ == "__main__":

    # Script Argument(s)
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    parser.add_argument('-d', '--dest')
    args = parser.parse_args()

    model, err = io.validate_sbml_model(args.sbmlpath)

    if model:

        target_subsystem = ["Pyruvate metabolism", "Transport, chloroplast", "Biosynthesis of steroids"]
        rxns = [rxn for rxn in model.reactions if rxn.subsystem in target_subsystem]
        
        graph = DiGraph(rxns)
        res = graph.find_sp("FRDPth")

        met_list = [(met.id, met.name) for met in model.metabolites]
        rxn_list = [(rxn.id, rxn.name) for rxn in model.reactions]
        met_ids = list(map(lambda x: x[0], met_list))
        rxn_ids = list(map(lambda x: x[0], rxn_list))
        while True: 

            inp = input("Search for: 1 - Met, 2 - Rxn, 0 - Quit\n")

            while inp not in ["0", "1", "2"]:
                inp = input("Search for: 1 - Met, 2 - Rxn, 0 - Quit\n")
            
            if inp == "0":
                break
            elif inp == "1":
                met_name = input("Met name or id: ")
                search = sort_by_similarity(met_list, met_name)[:10]
                for s in search:
                    print(f"{s[0]}: {s[1]}")
                choice = None
                while True:
                    choice = input("Choose: ")
                    if choice in met_ids:
                        break
                print("Metabolite found in the graph" if choice in res else "Not found.", end="\n\n")
            elif inp == "2":
                rxn_name = input("Met name or id: ")
                search = sort_by_similarity(rxn_list, rxn_name)[:10]
                for s in search:
                    print(f"{s[0]}: {s[1]}")
                choice = None
                while True:
                    choice = input("Choose: ")
                    if choice in rxn_ids:
                        break
                print("Rxn found in the graph" if choice in res else "Not found.", end="\n\n")
                    
        