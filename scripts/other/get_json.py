from cobra import io
import os, sys, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='_load_model',
        description='Load and validate your fba metabolic model from the .sbml format.'
    )
    parser.add_argument('sbmlpath')
    args = parser.parse_args()

    model, err = io.validate_sbml_model(args.sbmlpath, validate=True)

    io.save_json_model(model, args.sbmlpath.replace('.xml', '.json'))