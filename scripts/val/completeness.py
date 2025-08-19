from cobra import io
import os, argparse
from enum import Enum
from cobra.core import Model, Reaction, Metabolite
from pyvis.network import Network

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
        names: dict[str:str] = {}
        edges: dict[str:str] = {}
        weight: dict[tuple[str,str]:int] = {}

        rxncount, metcount = 0, 0
        for rxn in rxns:
            # Create reaction node
            rxn_node = Node(is_compound=False, data=rxn)
            nodes_map[rxn.id] = rxn_node
            names[rxn.id] = rxn.name
            # Add metabolites to graph
            for item in rxn.metabolites.items():
                met, coef = item
                # Create metabolite node if not in graph
                if not (met.id in nodes_map.keys()):
                    c_node = Node(is_compound=True, data=met)
                    nodes_map[met.id] = c_node
                    names[met.id] = met.name
                
                # Connect metabolite and reaction
                src, dest = rxn.id, met.id
                if coef < 0:
                    # Node for met is source to rxn
                    src, dest = met.id, rxn.id

                if src not in edges.keys():
                    edges[src] = [dest]
                else:
                    edges[src] = edges[src] + [dest]
                # weight[(src,dest)] = abs(coef)
                weight[(src, dest)] = 1
                metcount += 1
            rxncount += 1
            
        self.nodes, self.names, self.edges, self.weight, self.rxn_count, self.met_count = nodes_map, names, edges, weight, rxncount, metcount
    
    def get_node_count(self): return (self.rxn_count + self.met_count)
        
    def get_rxn_count(self): return self.rxn_count

    def get_met_count(self): return self.met_count

    # Debug

    def get_names(self): return self.names

    def get_edges(self): return self.edges

    def get_weights(self): return self.weight

    def get_nodes(self): return self.nodes
        
    # Pathfinding

    def _get_dest(self, nid: str):
        if nid not in self.edges.keys(): return []
        return self.edges[nid]
    
    def find_sp(self, src: str):
        
        queue = [src]
        visits: list[str] = []

        count = 0
        while len(queue) > 0:

            n = queue[0]
            queue = queue[1:]
            visits.append(n)

            d = self._get_dest(n)
            for m in d:
                if m not in visits:
                    queue.append(m)
            
            count += 1
            print(count, end='\r')
        
        return visits
    
    def dijkstra_sp(self, src: str):
        
        dist, prev, queue = {}, {}, []

        for n in self.nodes.keys():
            dist[n] = float('inf')
            prev[n] = None
            queue.append(n)
        
        dist[src] = 0

        while len(queue) > 0:
            u = min(queue, key=lambda x: dist[x])
            queue.remove(u)

            if not self.get_edges()[u]: 
                dist[u] = float('inf')
                continue

            for v in self.get_edges()[u]:
                alt = dist[u] + self.weight.get((u, v), 1)

                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u

        # Return the shortest path and its distance
        return dist, prev

    def dijkstra_search(self, src: str, dest: str):
        dist, prev = self.dijkstra_sp(src)

        # Reconstruct the shortest path
        path = []
        current = dest
        while current is not None:
            path.append(current)
            current = prev.get(current)

        path.reverse()
        return path, dist.get(dest)

    # Convert pyvis

    def convert_pyvis(self, filename: str, src: str, finds: list[str], include = None):
        network = Network(directed=True)
        # Default behaviour:
        if include == None:
            include = list(self.nodes.keys()) 
        # Add nodes to pyvis graph with name label and cobra id
        for item in self.names.items():
            id, name = item
            if id not in include: continue
            is_rxn = self.nodes[id].type == NType.REACTION
            network.add_node(id, label=name, color=("#ee5533" if id == src else "#33ee88" if id in finds else "#3388ee"), size=(60 if is_rxn else 20))
        # Build edges in pyvis graph
        for edge in self.edges.items():
            n, ms = edge
            if n not in include: continue
            for m in ms:
                if m not in include: continue
                try: network.add_edge(n, m)
                except: pass
        # Save network
        network.save_graph(f"{filename}.html")

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

        target_subsystem = ["Biosynthesis of steroids"]
        find_list = ["CAS", "sql_c", "psqldp_c", "chsterol_c", "mergtrol_c", "ALTERED_R02874", "ALTERED_R06223"]
        rxns = [rxn for rxn in model.reactions if rxn.subsystem in target_subsystem or rxn.id in find_list] # if rxn.subsystem in target_subsystem]
        src_met = "SS"
        
        graph = DiGraph(rxns)
        res = graph.find_sp(src_met)

        met_list = [(met.id, met.name) for met in model.metabolites]
        rxn_list = [(rxn.id, rxn.name) for rxn in model.reactions]
        met_ids = list(map(lambda x: x[0], met_list))
        rxn_ids = list(map(lambda x: x[0], rxn_list))
        while True: 

            inp = input("Search for: 1 - Met, 2 - Rxn, 3 - pyvis, 0 - Quit\n")

            while inp not in ["0", "1", "2", "3"]:
                inp = input("Search for: 1 - Met, 2 - Rxn, 3 - pyvis, 0 - Quit\n")
            
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
                rxn_name = input("Rxn name or id: ")
                search = sort_by_similarity(rxn_list, rxn_name)[:10]
                for s in search:
                    print(f"{s[0]}: {s[1]}")
                choice = None
                while True:
                    choice = input("Choose: ")
                    if choice in rxn_ids:
                        break
                print("Rxn found in the graph" if choice in res else "Not found.", end="\n\n")
            elif inp == "3":
                name = input("Give your file a name: ")
                graph.convert_pyvis(filename=name, src=src_met, finds=find_list, include=res)
                exit(0)
            else:
                print("Input not an option, choose one of the provided.\n")

# Run on KEGG-enhanced model to ensure the connectedness of the sterol biosynthesis pathway
# Organize, modularize and make more usable & interpretable