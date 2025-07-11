from pydantic import TypeAdapter as TA
from data.altered.model import Energy, Met, Rxn
from json import load

def parse_obj(json_path: str) -> list[Rxn]:
    try:
        with open(json_path, 'r') as f:
            data = load(f)
            validator = TA(list[Rxn])
            return validator.validate_python(data)
    except FileNotFoundError:
        print("File input not found.")
        return None
    except Exception as e:
        print(f"Exception occured. Message: {e}")
        return None