from typing import Optional

from .Date import Date
from .PlaceReference import PlaceReference

class Coverage:
    identifier = 'http://gedcomx.org/v1/Coverage'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,spatial: Optional[PlaceReference], temporal: Optional[Date]) -> None:
        self.spatial = spatial
        self.temporal = temporal    
    
    # ...existing code...

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Coverage instance from a JSON-dict (already parsed).
        """
        from .PlaceReference import PlaceReference
        from .Date import Date

        spatial = PlaceReference._from_json_(data.get('spatial')) if data.get('spatial') else None
        temporal = Date._from_json_(data.get('temporal')) if data.get('temporal') else None
        return cls(spatial=spatial, temporal=temporal)