import yaml
import json

def yaml2json(yaml_data:yaml) -> json:
        
    output = json.dumps(yaml.safe_load(yaml_data), indent=2)

    return json.loads(output)

def json2yaml(data) -> yaml:
    
    data=json.dumps(data,default=lambda o: del_none(o.__dict__))
    
    data=json.loads(data)
    output = yaml.dump(data)
    
    return output

def del_none(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.
    """

    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d  
