import base64
import uuid
import warnings

from typing import List, Optional

from .Attribution import Attribution
#from .Document import Document
from .Note import Note
from .Qualifier import Qualifier
from .Serialization import Serialization
from .SourceReference import SourceReference
from .Resource import Resource, URI
from ._Links import _LinkList, _Link

from collections.abc import Sized

class ConfidenceLevel(Qualifier):
    High = "http://gedcomx.org/High"
    Medium = "http://gedcomx.org/Medium"
    Low = "http://gedcomx.org/Low"
    
    @property
    def description(self):
        descriptions = {
            ConfidenceLevel.High: "The contributor has a high degree of confidence that the assertion is true.",
            ConfidenceLevel.Medium: "The contributor has a medium degree of confidence that the assertion is true.",
            ConfidenceLevel.Low: "The contributor has a low degree of confidence that the assertion is true."
        }
        return descriptions.get(self, "No description available.")
    
class Conclusion:
    """
    Represents a conclusion in the GEDCOM X conceptual model. A conclusion is a 
    genealogical assertion about a person, relationship, or event, derived from 
    one or more sources, with optional supporting metadata such as confidence, 
    attribution, and notes.

    Args:
        id (str, optional): A unique identifier for the conclusion. If not provided, 
            a UUID-based identifier will be automatically generated.
        lang (str, optional): The language code of the conclusion. Defaults to 'en'.
        sources (list[SourceReference], optional): A list of source references that 
            support the conclusion.
        analysis (Document | Resource, optional): A reference to an analysis document 
            or resource that supports the conclusion.
        notes (list[Note], optional): A list of notes providing additional context. 
            Defaults to an empty list.
        confidence (ConfidenceLevel, optional): The contributor's confidence in the 
            conclusion (High, Medium, or Low).
        attribution (Attribution, optional): Information about who contributed the 
            conclusion and when.
        uri (Resource, optional): A URI reference for the conclusion. Defaults to a 
            URI with the fragment set to the `id`.
        links (_LinkList, optional): A list of links associated with the conclusion. 
            Defaults to an empty `_LinkList`.

    Methods:
        add_note(note_to_add): Adds a note if it is not a duplicate and does not 
            exceed the maximum allowed notes.
        add_source(source_to_add): Adds a source reference if it is not already present.
        add_link(link): Adds a link to the `_LinkList`.
    """
    identifier = 'http://gedcomx.org/v1/Conclusion'
    version = 'http://gedcomx.org/conceptual-model/v1'

    @staticmethod
    def default_id_generator():
        # Generate a standard UUID
        standard_uuid = uuid.uuid4()
        # Convert UUID to bytes
        uuid_bytes = standard_uuid.bytes
        # Encode bytes to a Base64 string
        short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return short_uuid
    
    def __init__(self,
                 id: Optional[str],
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[object | Resource] = None,
                 notes: Optional[List[Note]] = [],
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 uri: Optional[Resource] = None,
                 _max_note_count: int = 20,
                 links: Optional[_LinkList] = None) -> None:
        
        self._id_generator = Conclusion.default_id_generator

        self.id = id if id else self._id_generator()
        self.lang = lang
        self.sources = sources if sources else []
        self.analysis = analysis
        self.notes = notes if notes else []
        self.confidence = confidence
        self.attribution = attribution
        self.max_note_count = _max_note_count
        self.uri = uri if uri else URI(fragment=id)
        self.links = links if links else _LinkList()    #NOTE This is not in specification, following FS format
    
    def add_note(self,note_to_add: Note):
        if self.notes and len(self.notes) >= self.max_note_count:
            warnings.warn(f"Max not count of {self.max_note_count} reached for id: {self.id}")
            return False
        if note_to_add and isinstance(note_to_add,Note):
            for existing in self.notes:
                if note_to_add == existing:
                    return False
            self.notes.append(note_to_add)

    def add_source(self, source_to_add: SourceReference):
        if source_to_add and isinstance(source_to_add,SourceReference):
            for current_source in self.sources:
                if source_to_add == current_source:
                    return
            self.sources.append(source_to_add)
        else:
            raise ValueError()
        
    def add_link(self,link: _Link):
        if link and isinstance(link,_Link):
            self.links.add(link)
    
    @property
    def _as_dict_(self):
        type_as_dict = {
            'id':self.id,
            'lang':self.lang,
            'sources': [source._as_dict_ for source in self.sources] if self.sources else None,
            'analysis': self.analysis if self.analysis else None,
            'notes': [note for note in self.notes] if self.notes else None,
            'confidence':self.confidence,
            'attribution':self.attribution,
            'links':self.links._as_dict_ if self.links else None
        }
      
        return Serialization.serialize_dict(type_as_dict) 
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return (
            self.id == other.id and
            self.lang == other.lang and
            self.sources == other.sources and
            self.analysis == other.analysis and
            self.notes == other.notes and
            self.confidence == other.confidence and
            self.attribution == other.attribution
        )