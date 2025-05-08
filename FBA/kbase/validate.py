import os, json, cobra

if __name__ == "__main__":
    sbml_path = os.path.join(os.getcwd(), 'fba', 'kbase', 'model', 'model.xml')
    (model, error) = cobra.io.validate_sbml_model(sbml_path)
    print(model, error)