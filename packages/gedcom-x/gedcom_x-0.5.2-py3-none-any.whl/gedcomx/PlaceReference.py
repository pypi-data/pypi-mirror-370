from typing import Optional

from .Resource import Resource
from .Serialization import Serialization

class PlaceReference:
    identifier = 'http://gedcomx.org/v1/PlaceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, original: Optional[str], descriptionRef: Optional[Resource]) -> None:
        self.original = original
        self.descriptionRef = descriptionRef

    @property
    def _as_dict_(self):
        place_reference_dict = {
            'original': self.original,
            'descriptionRef': self.descriptionRef._as_dict_ if isinstance(self.descriptionRef,Resource) else Resource(target=self.descriptionRef)._as_dict_
            } 
        return Serialization.serialize_dict(place_reference_dict)

def ensure_list(val):
    if val is None:
        return []
    return val if isinstance(val, list) else [val]

# PlaceReference
PlaceReference._from_json_ = classmethod(lambda cls, data: PlaceReference(
    original=data.get('original'),
    descriptionRef=Resource._from_json_(data['description']) if data.get('description') else None
))

   