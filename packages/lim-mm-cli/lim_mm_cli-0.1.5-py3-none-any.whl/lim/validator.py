import json
import jsonschema
from jsonschema import ValidationError

META_SCHEMA = {
    "type": "object",
    "required": ["name", "version", "description", "endpoint", "input", "output"],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string", "pattern": r"^\\d+\\.\\d+\\.\\d+$"},
        "description": {"type": "string"},
        "endpoint": {"type": "string", "pattern": r"^/.*"},
        "input": {
            "type": "object",
            "required": ["type", "format"],
            "properties": {
                "type": {"type": "string"},
                "format": {"type": "string"}
            }
        },
        "output": {
            "type": "object",
            "required": ["type", "format"],
            "properties": {
                "type": {"type": "string"},
                "format": {"type": "string"}
            }
        },
        "config": {
            "type": "object",
            "required": ["type", "format"],
            "properties": {
                "type": {"type": "string"},
                "format": {"type": "string"}
            }
        }
    }
}


def validate_meta(meta_path):
    with open(meta_path) as f:
        meta = json.load(f)
    try:
        jsonschema.validate(instance=meta, schema=META_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"meta.json validation failed: {e.message}")


def validate_meta_consistency(local: dict, remote: dict):
    if local != remote:
        raise ValueError(
            "meta.json content does not match /meta endpoint response")
