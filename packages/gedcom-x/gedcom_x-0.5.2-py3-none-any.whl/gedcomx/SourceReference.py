from typing import List, Optional

from .Attribution import Attribution
from .Qualifier import Qualifier

from .Resource import Resource
from .URI import URI

from collections.abc import Sized

class KnownSourceReference(Qualifier):
    CharacterRegion = "http://gedcomx.org/CharacterRegion"
    RectangleRegion = "http://gedcomx.org/RectangleRegion"
    TimeRegion = "http://gedcomx.org/TimeRegion"
    Page = "http://gedcomx.org/Page"
    
    @property
    def description(self):
        descriptions = {
            self.CharacterRegion: (
                "A region of text in a digital document, in the form of a,b where a is the index of the start "
                "character and b is the index of the end character. The meaning of this qualifier is undefined "
                "if the source being referenced is not a digital document."
            ),
            self.RectangleRegion: (
                "A rectangular region of a digital image. The value of the qualifier is interpreted as a series "
                "of four comma-separated numbers. If all numbers are less than 1, it is interpreted as x1,y1,x2,y2, "
                "representing percentage-based coordinates of the top-left and bottom-right corners. If any number is "
                "more than 1, it is interpreted as x,y,w,h where x and y are coordinates in pixels, and w and h are "
                "the width and height of the rectangle in pixels."
            ),
            self.TimeRegion: (
                "A region of time in a digital audio or video recording, in the form of a,b where a is the starting "
                "point in milliseconds and b is the ending point in milliseconds. This qualifier's meaning is undefined "
                "if the source is not a digital audio or video recording."
            ),
            self.Page: (
                "A single page in a multi-page document, represented as a 1-based integer. This always references the "
                "absolute page number, not any custom page number. This qualifier is undefined if the source is not a "
                "multi-page document."
            )
        }
        return descriptions.get(self, "No description available.")
    
class SourceReference:
    identifier = 'http://gedcomx.org/v1/SourceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self,
                 description: URI | object | None = None,
                 descriptionId: Optional[str] = None,
                 attribution: Optional[Attribution] = None,
                 qualifiers: Optional[List[Qualifier]] = None
                 ) -> None:
        
        #if not isinstance(description,URI): raise ValueError(f"description is of type {type(description)}")
        '''from .SourceDescription import SourceDescription
        self._description_object = None
        if isinstance(description,URI):
            #TODO See if Local, If not try to resolve,
            self._description_object = description
            
        elif isinstance(description,SourceDescription):
            self._description_object = description
            if hasattr(description,'_uri'):
                self.description = description._uri
            else:
                assert False
                self.description = Resource(object=description)
                description._uri = self.description
                description._object = description
        else:
            raise ValueError(f"'description' must be of type 'SourceDescription' or 'URI', type: {type(description)} was provided")'''
        
        
        self.description = description
        self.descriptionId = descriptionId
        self.attribution = attribution
        self.qualifiers = qualifiers

    def add_qualifier(self, qualifier: Qualifier):
        if isinstance(qualifier, Qualifier):
            self.qualifiers.append(qualifier)
    
    def append(self, text_to_add: str):
        if text_to_add and isinstance(text_to_add, str):
            if self.descriptionId is None:
                self.descriptionId = text_to_add
            else:
                self.descriptionId += text_to_add
        else:
            raise ValueError("The 'text_to_add' must be a non-empty string.")
    
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

        # Only add Relationship-specific fields
        sourcereference_fields = {
            'description':self.description.uri if self.description else None,
            'descriptionId': self.descriptionId.replace("\n"," ").replace("\r"," ") if self.descriptionId else None,
            'attribution': self.attribution._as_dict_ if self.attribution else None,
            'qualifiers':[qualifier.value for qualifier in self.qualifiers ] if self.qualifiers else None
            }

        # Serialize and exclude None values
        for key, value in sourcereference_fields.items():
            if value is not None:
                sourcereference_fields[key] = _serialize(value)

        return {
            k: v
            for k, v in sourcereference_fields.items()
            if v is not None and not (isinstance(v, Sized) and len(v) == 0)
        }
        

    @classmethod
    def _from_json_(cls, data: dict):
                
        """
        Rehydrate a SourceReference from the dict form produced by _as_dict_.
        """
        from .SourceDescription import SourceDescription

        # 1) Reconstruct the SourceDescription object
        desc_json = data.get('description')
        #if not desc_json:
        #    raise ValueError("SourceReference JSON missing 'description'")
        #desc_obj = SourceDescription._from_json_(desc_json)
        desc_obj = URI.from_url_(data.get('description')) #TODO <--- URI Reference
        

        # 2) Simple fields
        description_id = data.get('descriptionId')
        
        # 3) Attribution (if present)
        attrib = None
        if data.get('attribution') is not None:
            attrib = Attribution._from_json_(data['attribution'])
        
        # 4) Qualifiers list
        raw_quals = data.get('qualifiers', [])
        qualifiers: List[Qualifier] = []
        for q in raw_quals:
            try:
                # Try the known‐source enum first
                qualifiers.append(KnownSourceReference(q))
            except ValueError:
                # Fallback to generic Qualifier
                qualifiers.append(Qualifier(q))

        # 5) Instantiate via your existing __init__
        inst = cls(
            description=desc_obj,
            descriptionId=description_id,
            attribution=attrib,
            qualifiers=qualifiers
        )
        return inst

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False  

        return (
            self.description.uri == other.description.uri
        )
