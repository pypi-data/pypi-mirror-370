from deepdiff import DeepDiff
from pydantic.v1 import BaseModel

EXCLUDE_FIELDS = {"created_on", "updated_on"}

def generate_clean_diff(before: BaseModel, after: BaseModel, exclude_fields: set = EXCLUDE_FIELDS):
    before_dict = before.model_dump()
    after_dict = after.model_dump()
    try:
        clean_before = {k: v for k, v in before_dict.items() if k not in exclude_fields}
        clean_after = {k: v for k, v in after_dict.items() if k not in exclude_fields}

        diff = DeepDiff(clean_before, clean_after, ignore_order=True)
        original = {}
        modified = {}

        for change_type in ["values_changed", "type_changes"]:
            changes = diff.get(change_type, {})
            for path, change in changes.items():
                keys = path.strip("root").strip("[").strip("]").replace("][", ".").replace("'", "").split(".")
                _apply_nested_keys(original, keys, change["old_value"])
                _apply_nested_keys(modified, keys, change["new_value"])

        return {"original": original, "modified": modified}
    
    except Exception as e:
        return {"original": {}, "modified": {}, "error": str(e)}

def _apply_nested_keys(base: dict, keys: list, value):
    current = base
    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1
        next_key = keys[i + 1] if not is_last else None

        # Determine if current key is an index (for lists)
        is_index = key.isdigit()
        key = int(key) if is_index else key

        # Ensure current is list if key is int
        if is_index and not isinstance(current, list):
            # Convert current to list if it isn't already
            raise TypeError(f"Expected list at {keys[:i]}, got {type(current).__name__}")

        # Handle last key
        if is_last:
            if isinstance(current, list):
                # Ensure list is big enough
                while len(current) <= key:
                    current.append(None)
                current[key] = value
            else:
                current[key] = value
            return

        # Prepare next container (dict or list)
        if isinstance(current, list):
            while len(current) <= key:
                current.append(None)
            if current[key] is None:
                current[key] = {} if (next_key and not next_key.isdigit()) else []
            current = current[key]
        else:
            if key not in current:
                current[key] = {} if (next_key and not next_key.isdigit()) else []
            current = current[key]
