import os
import re
import sys
import yaml
from copy import deepcopy
from dateutil.parser import parse

def infer_type(s):
    s_low = s.strip().lower()

    # If starts with specific tokens return string
    if(s.startswith("\"") or s.startswith("\'")):
        return s.strip("\"").strip("\'")

    # Check for boolean
    if s_low in ['true', 'false']:
        return s_low == 'true'
    elif s_low in ['yes', 'no']:
        return s_low == 'yes'
    
    # None type
    if s in ['None', 'null', 'none', 'NONE', 'NULL', 'Null']:
        return None
    
    # Check for integer
    try:
        return int(s)
    except ValueError:
        pass

    # Check for float
    try:
        return float(s)
    except ValueError:
        pass

    # Check for date/time
    try:
        return parse(s)
    except ValueError:
        pass

    # Check for list (e.g., "[1, 2, 3]" or "[1,2,3]")
    if re.match(r'^\[.*\]$', s):
        try:
            return eval(s)
        except:
            pass

    # Default to string
    return s

class Configure(object):
    def __init__(self, data=None, name="RootConfig"):
        super().__setattr__("__config", dict())
        super().__setattr__("__name", name)
        if(data is not None):
            super().__getattribute__("__config").update(data)

    def from_yaml(self, file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        super().__getattribute__("__config").update(data)

    def from_dict(self, data):
        super().__getattribute__("__config").update(data)

    def get_dict(self, attr):
        config = super().__getattribute__("__config")
        if attr in config:
            return deepcopy(config[attr])
        name = super().__getattribute__("__name")
        raise AttributeError(f"'{name}' object has no attribute '{attr}'")

    def clear(self):
        config = super().__getattribute__("__config")
        for key in config:
            del config[key]

    def has_attr(self, attr):
        config = super().__getattribute__("__config")
        if attr in config:
            return True
        return False

    def __getattr__(self, attr):
        config = super().__getattribute__("__config")
        if attr in config:
            value = config[attr]
            if isinstance(value, dict):
                return Configure(value, attr)
            return value
        name = super().__getattribute__("__name")
        raise AttributeError(f"'{name}' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        d = super().__getattribute__("__config")
        if('.' in attr):
            keys = attr.split('.')
            for key in keys[:-1]:
                if(key not in d):
                    d[key] = dict()
                d = d[key]
            d[keys[-1]] = infer_type(value)
        else:
            d[attr] = infer_type(value)

    def set_value(self, attr, value):
        self.__setattr__(attr, value)

    def __repr__(self):
        config = super().__getattribute__("__config")
        def rec_prt(d, n_tab):
            _repr=""
            for k in d:
                v = d[k]
                if(isinstance(v, dict)):
                    _repr += "\t"*n_tab
                    _repr += f"{k}:\n"
                    _repr += rec_prt(v, n_tab + 1)
                else:
                    _repr += "\t"*n_tab
                    _repr += f"{k} = {v}\n"
            return _repr
        return f"\n\n{self.__class__.__name__}\n\n" + rec_prt(config, 0) + "\n\n"

    def to_yaml(self, file_path):
        config = super().__getattribute__("__config")
        head='---\n'
        head+=f"# Configuration file for {self.__class__.__name__}\n"
        def rec_prt(d, n_tab):
            _repr=""
            for k in d:
                v = d[k]
                _repr += "  "*n_tab
                _repr += f"{k}:"
                if(isinstance(v, dict)):
                    _repr += "\n" 
                    _repr += rec_prt(v, n_tab + 1)
                    _repr += "\n"
                elif(isinstance(v, list)):
                    _repr += "\n"
                    for item in v:
                        _repr += "  "*(n_tab + 1)
                        _repr += f"- {item}\n"
                    _repr += "\n"
                else:
                    _repr += f" {v}\n"
            return _repr

        with open(file_path, 'w') as file:
            file.write(head)
            file.write(rec_prt(config, 0))