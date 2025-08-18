from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Identifier import IdentifierList
from .Note import Note
from .SourceReference import SourceReference
from .TextValue import TextValue
from .Resource import Resource
from .Serialization import Serialization
from .Subject import Subject
from .URI import URI

class PlaceDescription(Subject):
    identifier = "http://gedcomx.org/v1/PlaceDescription"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str =None,
                 lang: str = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: Resource = None, notes: Optional[List[Note]] =[],
                 confidence: ConfidenceLevel = None,
                 attribution: Attribution = None,
                 extracted: bool = None,
                 evidence: List[EvidenceReference] = None,
                 media: List[SourceReference] = [],
                 identifiers: List[IdentifierList] = [],
                 names: List[TextValue] = [],
                 type: Optional[str] = None,
                 place: Optional[URI] = None,
                 jurisdiction: Optional["Resource | PlaceDescription"] = None, # PlaceDescription
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 temporalDescription: Optional[Date] = None,
                 spatialDescription: Optional[Resource] = None,) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        self.names = names
        self.type = type
        self.place = place
        self.jurisdiction = jurisdiction
        self.latitide = latitude
        self.longitute = longitude
        self.temporalDescription = temporalDescription
        self.spacialDescription = spatialDescription

    @property
    def _as_dict_(self):
        place_description_dict = super()._as_dict_
        place_description_dict.update({
            "names": [n for n in self.names] if self.names else None,
            "type": self.type if self.type else None,
            "place": self.place._as_dict_ if self.place else None,
            "jurisdiction": self.jurisdiction._as_dict_ if self.jurisdiction else None,
            "latitude": float(self.latitide) if self.latitide else None,
            "longitude": float(self.longitute) if self.longitute else None,
            "temporalDescription": self.temporalDescription if self.temporalDescription else None,
            "spatialDescription": self.spacialDescription._as_dict_ if self.temporalDescription else None            
        })
        return Serialization.serialize_dict(place_description_dict)    