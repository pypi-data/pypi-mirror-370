import yaml
from datetime import datetime

def to_openstep_plist(data, indent=0, indent_size=1):
    """Convert Python data to OpenStep plist string with proper indentation."""
    def format_indent(level):
        return " " * (level * indent_size)
    
    def format_value(val, level, is_value_side=False):
        if isinstance(val, str):
            # Always quote strings on the right side of =, escape special characters
            if is_value_side:
                val = val.replace('"', '\\"').replace('\n', '\\n')
                return f'"{val}"'
            # For keys, quote only if needed
            if any(c in val for c in " \n\t;={}()<>") or not val.isalnum():
                val = val.replace('"', '\\"').replace('\n', '\\n')
                return f'"{val}"'
            return val
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, (int, float)):
            return str(val)  # Numbers are not quoted
        elif isinstance(val, list):
            if not val:
                return "()"
            items = [format_value(item, level + 1, is_value_side=True) for item in val]
            return f"({', '.join(items)})"
        elif isinstance(val, dict):
            if not val:
                return "{}"
            lines = [f"{format_indent(level)}{{"]
            for key, value in val.items():
                key_str = format_value(key, level + 1, is_value_side=False)
                value_str = format_value(value, level + 1, is_value_side=True)
                lines.append(f"{format_indent(level + 1)}{key_str} = {value_str};")
            lines.append(f"{format_indent(level)}}}")
            return "\n".join(lines)
        elif isinstance(val, datetime):
            return f"<*D{val.strftime('%Y-%m-%d %H:%M:%S %z')}>"
        elif val is None:
            return "{}"  # Replace <*N> with {}
        else:
            raise ValueError(f"Unsupported type: {type(val)}")

    # Handle top-level dictionary as a key-value pair if it has a single key
    if isinstance(data, dict) and len(data) == 1:
        key, value = next(iter(data.items()))
        key_str = format_value(key, indent, is_value_side=False)
        value_str = format_value(value, indent, is_value_side=True)
        return f"{key_str} = {value_str};"
    return format_value(data, indent, is_value_side=True)

def to_plist(yaml_data):
    """Convert YAML data (Python object) to OpenStep plist string."""
    try:
        return to_openstep_plist(yaml_data)
    except Exception as e:
        raise ValueError(f"Failed to convert YAML data to OpenStep plist: {str(e)}")

def to_yaml_file(yaml_file_path, plist_file_path):
    """Convert YAML file to OpenStep plist file."""
    try:
        # Read and parse the YAML file
        with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)
        
        # Convert to OpenStep plist format
        plist_data = to_openstep_plist(data)
        
        # Write to output plist file
        with open(plist_file_path, 'w', encoding='utf-8') as plist_file:
            plist_file.write(plist_data)
        
        return True
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {yaml_file_path} was not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {yaml_file_path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to convert YAML to OpenStep plist: {str(e)}")