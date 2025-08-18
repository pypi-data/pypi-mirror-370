from typing import Dict

from collections.abc import Sized


def _has_parent_class(obj) -> bool:
    return hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__') and len(obj.__class__.__bases__) > 0

def serialize_to_dict(obj,class_values:Dict,ignore_null=True):
    def _serialize(value):
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, dict):
            return {k: _serialize(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple, set)):
            return [_serialize(v) for v in value]
        elif hasattr(value, "_as_dict_"):
            return value._as_dict_
        else:
            return str(value)  # fallback for unknown objects

    values_dict = {}
    if _has_parent_class(obj):
        values_dict.update(super(obj.__class__, obj)._as_dict_)
    if class_values:
        values_dict.update(class_values)
        # Serialize and exclude None values

    empty_fields = []
    for key, value in values_dict.items():
        if value is not None:
            values_dict[key] = _serialize(value)
        else:
            empty_fields.append(key)
    
    for key in empty_fields:
            del values_dict[key]
                
    return values_dict

class Serialization:

    @staticmethod
    def serialize_dict(dict_to_serialize: dict) -> dict:
        """
        Iterates through the dict, serilaizing all Gedcom Types into a json compatible value
        
        Parameters
        ----------
        dict_to_serialize: dict
            dict that has been created from any Gedcom Type Object's _as_dict_ property

        Raises
        ------
        ValueError
            If `id` is not a valid UUID.
        """
        def _serialize(value):
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple, set)):
                return [_serialize(v) for v in value]
            elif hasattr(value, "_as_dict_"):
                return value._as_dict_
            else:
                return str(value)  # fallback for unknown objects
        
        if dict_to_serialize and isinstance(dict_to_serialize,dict):
            for key, value in dict_to_serialize.items():
                if value is not None:
                    dict_to_serialize[key] = _serialize(value)
        
            return {
                    k: v
                    for k, v in dict_to_serialize.items()
                    if v is not None and not (isinstance(v, Sized) and len(v) == 0)
                }
        return {}
