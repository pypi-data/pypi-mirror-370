from enum import Enum
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Fact import Fact, FactType
from .Gender import Gender, GenderType
from .Identifier import IdentifierList
from .Name import Name
from .Note import Note
from .SourceReference import SourceReference
from .Subject import Subject
from .Resource import Resource
from collections.abc import Sized
from ._Links import _LinkList

class Person(Subject):
    """A person in the system.

    Args:
        id (str):      Unique identifier for this person.
        name (str):    Full name.
        birth (date):  Birth date (YYYY-MM-DD).
        friends (List[Person], optional): List of friends. Defaults to None.

    Raises:
        ValueError: If `id` is not a valid UUID.
    """
    identifier = 'http://gedcomx.org/v1/Person'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str | None = None,
             lang: str = 'en',
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[Resource] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: bool = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[IdentifierList] = None,
             private: Optional[bool] = False,
             gender: Optional[Gender] = Gender(type=GenderType.Unknown),
             names: Optional[List[Name]] = None,
             facts: Optional[List[Fact]] = None,
             living: Optional[bool] = False,
             links: Optional[_LinkList] = None) -> None:
        # Call superclass initializer if needed
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers,links=links)
        
        # Initialize mutable attributes to empty lists if None
        self.sources = sources if sources is not None else []
        self.notes = notes if notes is not None else []
        self.evidence = evidence if evidence is not None else []
        self.media = media if media is not None else []
        self.identifiers = identifiers if identifiers is not None else []
        self.names = names if names is not None else []
        self.facts = facts if facts is not None else []

        self.private = private
        self.gender = gender

        self.living = living       #TODO This is from familysearch API

        self._relationships = []
          
    def add_fact(self, fact_to_add: Fact) -> bool:
        if fact_to_add and isinstance(fact_to_add,Fact):
            for current_fact in self.facts:
                if fact_to_add == current_fact:
                    return False
            self.facts.append(fact_to_add)
            return True

    def add_name(self, name_to_add: Name) -> bool:
        if len(self.names) > 5: 
            for name in self.names:
                print(name)
            raise
        if name_to_add and isinstance(name_to_add, Name):
            for current_name in self.names:
                if name_to_add == current_name:
                    return False
            self.names.append(name_to_add)
            return True
    
    def _add_relationship(self, relationship_to_add: object):
        from .Relationship import Relationship
        if isinstance(relationship_to_add,Relationship):
            self._relationships.append(relationship_to_add)
        else:
            raise ValueError()
    
    def display(self):
        display = {
        "ascendancyNumber": "1",
        "deathDate": "from 2001 to 2005",
        "descendancyNumber": "1",
        "gender": self.gender.type,
        "lifespan": "-2005",
        "name": self.names[0].nameForms[0].fullText
            }
        
        return display

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

        subject_fields = super()._as_dict_  # Start with base class fields
        # Only add Relationship-specific fields
        subject_fields.update({
            'private': self.private,
            'living': self.living,
            'gender': self.gender._as_dict_ if self.gender else None,
            'names': [name._as_dict_ for name in self.names],
            'facts': [fact for fact in self.facts],
            'uri': 'uri: ' + self.uri.value
                           
        })

        # Serialize and exclude None values
        for key, value in subject_fields.items():
            if value is not None:
                subject_fields[key] = _serialize(value)

        # 3) merge and filter out None *at the top level*
        return {
                k: v
                for k, v in subject_fields.items()
                if v is not None and not (isinstance(v, Sized) and len(v) == 0)
            }
        
        
    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        
        
        # Basic scalar fields
        id_        = data.get('id')
        lang       = data.get('lang', 'en')
        private    = data.get('private', False)
        extracted  = data.get('extracted', False)

        living  = data.get('extracted', False)

        # Complex singletons
        analysis    = Resource._from_json_(data['analysis']) if data.get('analysis') else None
        attribution = Attribution._from_json_(data['attribution']) if data.get('attribution') else None
        confidence  = ConfidenceLevel_from_json_(data['confidence']) if data.get('confidence') else None

        # Gender (string or dict depending on your JSON)
        gender_json = data.get('gender')
        if isinstance(gender_json, dict):
            gender = Gender._from_json_(gender_json)
        else:
            # if it's just the enum value
            gender = Gender(type=GenderType(gender_json)) if gender_json else Gender(type=GenderType.Unknown)
        
        
        sources     = [SourceReference._from_json_(o)   for o in data.get('sources')] if data.get('sources') else None
        notes       = [Note._from_json_(o)              for o in data.get('notes')] if data.get('notes') else None
        evidence    = [EvidenceReference._from_json_(o) for o in data.get('evidence')] if data.get('evidence') else None
        media       = [SourceReference._from_json_(o)   for o in data.get('media')] if data.get('media') else None
        identifiers = IdentifierList._from_json_(data.get('identifiers'))      if data.get('identifiers') else None
        names       = [Name._from_json_(o)              for o in data.get('names')] if data.get('names') else None
        facts       = [Fact._from_json_(o)              for o in data.get('facts')] if data.get('facts') else None
        links       = _LinkList._from_json_(data.get('links'))     if data.get('links') else None

        # Build the instance
        inst = cls(
            id          = id_,
            lang        = lang,
            sources     = sources,
            analysis    = analysis,
            notes       = notes,
            confidence  = confidence,
            attribution = attribution,
            extracted   = extracted,
            evidence    = evidence,
            media       = media,
            identifiers = identifiers,
            private     = private,
            gender      = gender,
            names       = names,
            facts       = facts,
            living      = living,
            links       = links
        )

        return inst

class QuickPerson:
    """A GedcomX Person Data Type created with basic information.

    Underlying GedcomX Types are created for you.
        
    Args:
        name (str):    Full name.
        birth (date,Optional):  Birth date (YYYY-MM-DD).
        death (date, Optional)

        

    Raises:
        ValueError: If `id` is not a valid UUID.
    """
    def __new__(cls, name: Optional[str], dob: Optional[str], dod: Optional[str]):
        # Build facts from args
        facts = []
        if dob:
            facts.append(Fact(type=FactType.Birth, date=Date(original=dob)))
        if dod:
            facts.append(Fact(type=FactType.Death, date=Date(original=dod)))

        # Return the different class instance
        return Person(facts=facts, names=[name] if name else None)