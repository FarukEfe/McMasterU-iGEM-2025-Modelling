from cobra import io, Model, Reaction, Metabolite
import os, sys

path = './data/raw/iBD1106.xml'
path = './data/raw/iCre1355/iCre1355_auto.xml'
path = './data/raw/iRC1080.xml'

model, error = io.validate_sbml_model(path, validate=True)

# print(error)
# exit(1)

# print(help(model))

for i in model.boundary:
    print(i.id, "---",i.name)
exit(1)

if model:
    rxn: Reaction = model.reactions.get_by_id("SS")
    print(rxn.lower_bound, rxn.upper_bound)

    print("Setting objective...")
    objective = "BIOMASS_Chlamy_auto" if path == './data/raw/iRC1080.xml' else "Biomass_Chlamy_auto"
    #obj: Reaction = model.reactions.get_by_id(objective)
    #obj: Reaction = model.reactions.get_by_id("SS")
    obj: Reaction = model.reactions.get_by_id("CAS")
    # print(obj)
    model.objective = obj.id

    # Make a copy of the model
    copied_model = model.copy()
    copied_model.reactions.get_by_id(rxn.id).upper_bound = 1e12
    copied_model.objective = obj.id
    
    print("Optimizing models...")
    s1 = model.optimize()
    s2 = copied_model.optimize()
    r1 = s1.fluxes.get(obj.id)
    r2 = s2.fluxes.get(obj.id)
    print(r1, r2)