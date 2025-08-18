
from enum import Enum

from typing import List, Optional, Dict, Any

from .Qualifier import Qualifier
from .Resource import Resource
from .URI import URI

class IdentifierType(Enum):
    Primary = "http://gedcomx.org/Primary"
    Authority = "http://gedcomx.org/Authority"
    Deprecated = "http://gedcomx.org/Deprecated"
    Persistant = "http://gedcomx.org/Persistent"
    External = "https://gedcom.io/terms/v7/EXID"
    Other = "user provided"
    
    @property
    def description(self):
        descriptions = {
            IdentifierType.Primary: (
                "The primary identifier for the resource. The value of the identifier MUST resolve to the instance of "
                "Subject to which the identifier applies."
            ),
            IdentifierType.Authority: (
                "An identifier for the resource in an external authority or other expert system. The value of the identifier "
                "MUST resolve to a public, authoritative source for information about the Subject to which the identifier applies."
            ),
            IdentifierType.Deprecated: (
                "An identifier that has been relegated, deprecated, or otherwise downgraded. This identifier is commonly used "
                "as the result of a merge when what was once a primary identifier for a resource is no longer the primary identifier. "
                "The value of the identifier MUST resolve to the instance of Subject to which the identifier applies."
            )
        }
        return descriptions.get(self, "No description available.")
    
class Identifier:
    identifier = 'http://gedcomx.org/v1/Identifier'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[List[URI]], type: Optional[IdentifierType] = IdentifierType.Primary) -> None:
        if not isinstance(value,list):
            value = [value]
        self.type = type
        self.values = value if value else []
    
    @property
    def _as_dict_(self):
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

        identifier_fields = {
            'value': self.values if self.values else None,
            'type': self.type.value if self.type else None
                           
        }

        # Serialize and exclude None values
        for key, value in identifier_fields.items():
            if value is not None:
                identifier_fields[key] = _serialize(value)

        return identifier_fields

    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'Identifier | None':
        """
        Construct an Identifier from a dict parsed from JSON.
        """
        #for name, member in IdentifierType.__members__.items():
        #    print(name)

        # Parse value (URI dict or string)
        print('--------------',data)
        for key in data.keys():
            type = key
            value = data[key]
        uri_obj: Optional[Resource] = None
        # TODO DO THIS BETTER

        # Parse type
        raw_type = data.get('type')
        if raw_type is None:
            return None
        id_type: Optional[IdentifierType] = IdentifierType(raw_type) if raw_type else None
        return cls(value=value, type=id_type)

class IdentifierList():
    def __init__(self) -> None:
        self.identifiers = {}
    
    def make_hashable(self, obj):
        """Convert any object into a hashable representation."""
        if isinstance(obj, dict):
            # Convert dict to sorted tuple of key/value pairs
            return tuple(sorted((k, self.make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, (list, set, tuple)):
            # Convert sequences/sets into tuples
            return tuple(self.make_hashable(i) for i in obj)
        elif hasattr(obj,'_as_dict_'):
            as_dict = obj._as_dict_
            t = tuple(sorted((k, self.make_hashable(v)) for k, v in as_dict.items()))
            return t
        else:
            return obj  # Immutable stays as is

    def unique_list(self, items):
        """Return a list without duplicates, preserving order."""
        seen = set()
        result = []
        for item in items:
            h = self.make_hashable(item)
            if h not in seen:
                seen.add(h)
                result.append(item)
        return result
    
    def append(self, identifier: Identifier):
        if isinstance(identifier, Identifier): 
            self.add_identifer(identifier)
        else:
            raise ValueError()

    def add_identifer(self, identifier: Identifier):
        if identifier and isinstance(identifier,Identifier):
            if identifier.type.value in self.identifiers.keys():
                self.identifiers[identifier.type.value].extend(identifier.values)
            else:
                self.identifiers[identifier.type.value] = identifier.values
            print(self.identifiers[identifier.type.value])
            self.identifiers[identifier.type.value] = self.unique_list(self.identifiers[identifier.type.value])
        
    # TODO Merge Identifiers
    def contains(self,identifier: Identifier):
        if identifier and isinstance(identifier,Identifier):
            if identifier.type.value in self.identifiers.keys():
                pass
    
    def __get_item__(self):
        pass

    @classmethod
    def _from_json_(cls,data):
        identifier_list = IdentifierList()
        for name, member in IdentifierType.__members__.items():
            values = data.get(member.value,None)
            if values:
                identifier_list.add_identifer(Identifier(values,IdentifierType(member.value)))
        return identifier_list
    
    @property
    def _as_dict_(self):
        identifiers_dict = {}
        for key in self.identifiers.keys():
            # Should always be flat due to unique_list in add method.
            identifiers_dict[key] = [u.value for u in self.identifiers[key]]

        return identifiers_dict





