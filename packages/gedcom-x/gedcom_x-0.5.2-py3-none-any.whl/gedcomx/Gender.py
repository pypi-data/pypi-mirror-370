from enum import Enum
from typing import List, Optional

from gedcomx.Attribution import Attribution
from gedcomx.Conclusion import ConfidenceLevel
from gedcomx.Note import Note
from gedcomx.SourceReference import SourceReference
from gedcomx.Resource import Resource

from .Conclusion import Conclusion
from .Qualifier import Qualifier

from collections.abc import Sized

class GenderType(Enum):
    Male = "http://gedcomx.org/Male"
    Female = "http://gedcomx.org/Female"
    Unknown = "http://gedcomx.org/Unknown"
    Intersex = "http://gedcomx.org/Intersex"
    
    @property
    def description(self):
        descriptions = {
            GenderType.Male: "Male gender.",
            GenderType.Female: "Female gender.",
            GenderType.Unknown: "Unknown gender.",
            GenderType.Intersex: "Intersex (assignment at birth)."
        }
        return descriptions.get(self, "No description available.")
    
class Gender(Conclusion):
    identifier = 'http://gedcomx.org/v1/Gender'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None, 
                 type: Optional[GenderType] = None
                 ) -> None:
        super().__init__(id=id, lang=lang, sources=sources, analysis=analysis, notes=notes, confidence=confidence, attribution=attribution)
        self.type = type
    
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
            
        gender_fields = super()._as_dict_  # Start with base class fields
        # Only add Relationship-specific fields
        gender_fields.update({
            'type':self.type.value if self.type else None
                           
        })
        
        # Serialize and exclude None values
        for key, value in gender_fields.items():
            if value is not None:
                gender_fields[key] = _serialize(value)

        return {
            k: v
            for k, v in gender_fields.items()
            if v is not None and not (isinstance(v, Sized) and len(v) == 0)
        }
        
        return gender_fields

    @classmethod
    def _from_json_(cls,data):
        id = data.get('id') if data.get('id') else None
        lang = data.get('lang',None)
        sources = [SourceReference._from_json_(o)   for o in data.get('sources')] if data.get('sources') else None
        analysis = None #URI.from_url(data.get('analysis')) if data.get('analysis',None) else None,
        notes = [Note._from_json_(o) for o in data.get('notes',[])]
        #TODO confidence = ConfidenceLevel(data.get('confidence')),
        attribution = Attribution._from_json_(data.get('attribution')) 
        type = GenderType(data.get('type'))
        
        
        return Gender(id=id,
                      lang=lang,
                      sources=sources,
                      analysis=analysis,
                      notes=notes,
                      attribution=attribution,
                      type=type)
        