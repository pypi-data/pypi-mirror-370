# Load and validate YAML/JSON settings
import yaml

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        # optionally validate data
        return data