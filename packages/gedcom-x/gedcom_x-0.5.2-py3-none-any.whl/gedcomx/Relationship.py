from enum import Enum
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .EvidenceReference import EvidenceReference
from .Fact import Fact
from .Identifier import Identifier
from .Note import Note
from .Person import Person
from .Serialization import Serialization
from .SourceReference import SourceReference
from .Resource import Resource

from .Subject import Subject

class RelationshipType(Enum):
    Couple = "http://gedcomx.org/Couple"
    ParentChild = "http://gedcomx.org/ParentChild"
    
    @property
    def description(self):
        descriptions = {
            RelationshipType.Couple: "A relationship of a pair of persons.",
            RelationshipType.ParentChild: "A relationship from a parent to a child."
        }
        return descriptions.get(self, "No description available.")
    
class Relationship(Subject):
    """Represents a relationship between two Person(s)

    Args:
        type (RelationshipType): Type of relationship 
        person1 (Person) = First Person in Relationship
        person2 (Person): Second Person in Relationship

    Raises:
        ValueError: If `id` is not a valid UUID.
    """
    identifier = 'http://gedcomx.org/v1/Relationship'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, 
             id: Optional[str] = None,
             lang: Optional[str] = None,
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[Resource] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: Optional[bool] = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[List[Identifier]] = None,
             type: Optional[RelationshipType] = None,
             person1: Optional[Person | Resource] = None,
             person2: Optional[Person | Resource] = None,
             facts: Optional[List[Fact]] = None) -> None:
    
        # Call superclass initializer if required
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        
        # Initialize optional parameters with default empty lists if None
        #self.sources = sources if sources is not None else []
        #self.notes = notes if notes is not None else []
        #self.evidence = evidence if evidence is not None else []
        #self.media = media if media is not None else []
        #self.identifiers = identifiers if identifiers is not None else []
        #self.facts = facts if facts is not None else []

        # Initialize other attributes
        self.type = type
        self.person1 = person1
        self.person2 = person2
        self.facts = facts if facts else None
    
    @property
    def _as_dict_(self):
        return serialize_to_dict(self, {
            "type": self.type.value if isinstance(self.type, RelationshipType) else self.type,
            "person1": self.person1.uri,
            "person2": self.person2.uri,
            "facts": [fact for fact in self.facts] if self.facts else None
        })

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Relationship instance from a JSON-dict (already parsed).
        """
        def ensure_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]  # wrap single item in list

        # Basic scalar fields (adjust as needed)
        id_        = data.get('id')
        type_      = data.get('type')
        extracted  = data.get('extracted', None)
        private    = data.get('private', None)

        # Complex singletons (adjust as needed)
        person1    = Resource.from_url(data.get('person1')['resource']) if data.get('person1') else None
        person2    = Resource.from_url(data.get('person2')['resource']) if data.get('person2') else None
        facts      = [Fact._from_json_(o) for o in ensure_list(data.get('facts'))]
        sources    = [SourceReference._from_json_(o) for o in ensure_list(data.get('sources'))]
        notes      = [Note._from_json_(o) for o in ensure_list(data.get('notes'))]

        # Build the instance
        inst = cls(
            id        = id_,
            type      = type_,
            extracted = extracted,
            #private   = private,       #TODO Has this been added?
            person1   = person1,
            person2   = person2,
            facts     = facts,
            sources   = sources,
            notes     = notes
        )

        return inst

    