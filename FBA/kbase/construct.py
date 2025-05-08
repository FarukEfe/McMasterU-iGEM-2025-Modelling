import os, json, cobra
from cobra import Model, Reaction, Metabolite


if __name__ == "__main__":

    # Load KBase JSON file
    with open(os.path.join(os.getcwd(), 'fba', 'kbase', 'raw.json')) as f:
        kb_model = json.load(f)

    # Initialize COBRA model
    model = Model(kb_model["id"])

    # Add compartments (e.g., "c0" → "c")
    compartments = {
        cmp["id"]: cmp["id"].replace("0", "")  # Simplify "c0" to "c"
        for cmp in kb_model.get("modelcompartments", [])
    }
    model.compartments = compartments

    # Add metabolites
    for cpd in kb_model["modelcompounds"]:
        # Extract compartment ID (e.g., "c0" → "c")
        cmp_id = cpd["modelcompartment_ref"].split("_")[-1]
        cmp_id = compartments.get(cmp_id, cmp_id)
        
        met = Metabolite(
            id=cpd["id"],
            name=cpd.get("name", ""),
            compartment=cmp_id,
            formula=cpd.get("formula", "")
        )
        model.add_metabolites([met])

    # Add reactions
    for rxn in kb_model["modelreactions"]:
        reaction = Reaction(
            id=rxn["id"],
            name=rxn.get("name", ""),
            lower_bound=rxn.get("lower_bound", -1000),
            upper_bound=rxn.get("upper_bound", 1000)
        )
        model.add_reactions([reaction])
        
        # Add stoichiometry
        stoichiometry = {}
        for reagent in rxn["modelReactionReagents"]:
            met_id = reagent["modelcompound_ref"].split("/")[-1]
            coeff = reagent["coefficient"]
            stoichiometry[model.metabolites.get_by_id(met_id)] = coeff
        reaction.add_metabolites(stoichiometry)

    # Set objective (e.g., biomass reaction)
    if "biomass_reactions" in kb_model:
        model.objective = kb_model["biomass_reactions"][0]  # Adjust if needed

    # Print out metabolites
    print([met.name for met in model.metabolites])

    # Save model to SBML/JSON (COBRApy compatible)
    model_path = os.path.join(os.getcwd(), 'fba', 'kbase', 'model')
    sbml_path = os.path.join(model_path, 'model.xml')
    json_path = os.path.join(model_path, 'model.json')
    if not os.path.exists(model_path): os.mkdir(model_path)
    cobra.io.write_sbml_model(model, sbml_path)
    cobra.io.save_json_model(model, json_path)