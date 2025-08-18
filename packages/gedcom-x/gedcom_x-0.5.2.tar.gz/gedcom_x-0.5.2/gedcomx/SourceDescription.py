import base64
import uuid
import warnings

from enum import Enum
from typing import List, Optional, Dict, Any

from .Agent import Agent
from .Attribution import Attribution
from .Coverage import Coverage
from .Date import Date
from .Identifier import Identifier, IdentifierList
from .Note import Note
from .SourceCitation import SourceCitation
from .SourceReference import SourceReference
from .TextValue import TextValue
from .Resource import Resource, get_resource_as_dict
from .Serialization import Serialization
from .URI import URI

from collections.abc import Sized

class ResourceType(Enum):
    Collection = "http://gedcomx.org/Collection"
    PhysicalArtifact = "http://gedcomx.org/PhysicalArtifact"
    DigitalArtifact = "http://gedcomx.org/DigitalArtifact"
    Record = "http://gedcomx.org/Record"
    Person = "http://gedcomx.org/Person"    
    
    @property
    def description(self):
        descriptions = {
            ResourceType.Collection: "A collection of genealogical resources. A collection may contain physical artifacts (such as a collection of books in a library), records (such as the 1940 U.S. Census), or digital artifacts (such as an online genealogical application).",
            ResourceType.PhysicalArtifact: "A physical artifact, such as a book.",
            ResourceType.DigitalArtifact: "A digital artifact, such as a digital image of a birth certificate or other record.",
            ResourceType.Record: "A historical record, such as a census record or a vital record."
        }
        return descriptions.get(self, "No description available.")
    
class SourceDescription:
    """
    The SourceDescription data type defines a description of a source of genealogical information.
    http://gedcomx.org/v1/SourceDescription

    Parameters
    ----------
    id : str
        Unique identifier for this SourceDescription.
    attribution : Attribution Object
        Attribution information for the Genealogy
    filepath : str
        Not Implimented.
    description : str
        Description of the Genealogy: ex. 'My Family Tree'

    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    identifier = "http://gedcomx.org/v1/SourceDescription"
    """
    Gedcom-X Specification Identifier
    """

    def __init__(self, id: Optional[str] = None,
                 resourceType: Optional[ResourceType] = None,
                 citations: Optional[List[SourceCitation]] = [],
                 mediaType: Optional[str] = None,
                 about: Optional[URI] = None,
                 mediator: Optional[Resource] = None,
                 publisher: Optional[Resource|Agent] = None,
                 authors: Optional[List[Resource]] = None,
                 sources: Optional[List[SourceReference]] = None, # SourceReference
                 analysis: Optional[Resource] = None,  # analysis should be of type 'Document', not specified to avoid circular import
                 componentOf: Optional[SourceReference] = None, # SourceReference
                 titles: Optional[List[TextValue]] = None,
                 notes: Optional[List[Note]] = None,
                 attribution: Optional[Attribution] = None,
                 rights: Optional[List[Resource]] = [],
                 coverage: Optional[Coverage] = None, # Coverage
                 descriptions: Optional[List[TextValue]] = None,
                 identifiers: Optional[IdentifierList] = None,
                 created: Optional[Date] = None,
                 modified: Optional[Date] = None,
                 published: Optional[Date] = None,
                 repository: Optional[Agent] = None,
                 max_note_count: int = 20):
        
        self.id = id if id else SourceDescription.default_id_generator()
        self.resourceType = resourceType
        self.citations = citations or []
        self.mediaType = mediaType
        self.about = about
        self.mediator = mediator
        self._publisher = publisher 
        self.authors = authors or []
        self.sources = sources or []
        self.analysis = analysis
        self.componentOf = componentOf
        self.titles = titles or []
        self.notes = notes or []
        self.attribution = attribution
        self.rights = rights or []
        self.coverage = coverage or []
        self.descriptions = descriptions or []
        self.identifiers = identifiers or IdentifierList()
        self.created = created
        self.modified = modified
        self.published = published
        self.repository = repository
        self.max_note_count = max_note_count

        self.uri = URI(fragment=id)
    
    @property
    def publisher(self) -> Resource | Agent | None:
        return self._publisher
    

    @publisher.setter
    def publisher(self, value: Resource | Agent):
        if value is None:
            self._publisher = None
        elif isinstance(value,Resource):
            self._publisher = value
        elif isinstance(value,Agent):
            self._publisher = value
        else:
            raise ValueError(f"'publisher' must be of type 'URI' or 'Agent', type: {type(value)} was provided")
    
    def add_description(self, desccription_to_add: TextValue):
        if desccription_to_add and isinstance(desccription_to_add,TextValue):
            for current_description in self.descriptions:
                if desccription_to_add == current_description:
                    return
            self.descriptions.append(desccription_to_add)

    def add_identifier(self, identifier_to_add: Identifier):
        if identifier_to_add and isinstance(identifier_to_add,Identifier):
            self.identifiers.append(identifier_to_add)
    
    def add_note(self,note_to_add: Note):
        if len(self.notes) >= self.max_note_count:
            warnings.warn(f"Max not count of {self.max_note_count} reached for id: {self.id}")
            return False
        if note_to_add and isinstance(note_to_add,Note):
            for existing in self.notes:
                if note_to_add == existing:
                    return False
            self.notes.append(note_to_add)
    
    def add_source(self, source_to_add: object):
        #from .SourceReference import SourceReference
        if source_to_add and isinstance(object,SourceReference):
            for current_source in self.sources:
                if current_source == source_to_add:
                    return
            self.sources.append(source_to_add)

    def add_title(self, title_to_add: TextValue):
        if isinstance(title_to_add,str): title_to_add = TextValue(value=title_to_add)
        if title_to_add and isinstance(title_to_add, TextValue):
            for current_title in self.titles:
                if title_to_add == current_title:
                    return False
            self.titles.append(title_to_add)
        else:
            raise ValueError(f"Cannot add title of type {type(title_to_add)}")
        
    @staticmethod
    def default_id_generator():
        # Generate a standard UUID
        standard_uuid = uuid.uuid4()
        # Convert UUID to bytes
        uuid_bytes = standard_uuid.bytes
        # Encode bytes to a Base64 string
        short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return 'SD-' + str(short_uuid)
    
    @property
    def _as_dict_(self) -> Dict[str, Any]:
        

        
        type_as_dict = {
            'id': self.id,
            'about': self.about._as_dict_ if self.about else None,
            'resourceType': self.resourceType.value if self.resourceType else None,
            'citations': [c._as_dict_ for c in self.citations] or None,
            'mediaType': self.mediaType,
            'mediator': get_resource_as_dict(self.mediator),
            'publisher': get_resource_as_dict(self.publisher),
            'authors': [get_resource_as_dict(a) for a in self.authors] or None,
            'sources': [s._as_dict_ for s in self.sources] or None,
            'analysis': self.analysis._as_dict_ if self.analysis else None,
            'componentOf': self.componentOf._as_dict_ if self.componentOf else None,
            'titles': [t._as_dict_ for t in self.titles] or None,
            'notes': [n._as_dict_ for n in self.notes] or None,
            'attribution': self.attribution._as_dict_ if self.attribution else None,
            'rights': [r._as_dict_ for r in self.rights] or None,
            'coverage': self.coverage._as_dict_ if self.coverage else None,
            'descriptions': [d._as_dict_ for d in self.descriptions] or None,
            'identifiers': self.identifiers._as_dict_ if self.identifiers else None,
            'created': self.created if self.created else None,
            'modified': self.modified if self.modified else None,
            'published': self.published if self.published else None,
            'repository': get_resource_as_dict(self.repository),
            'uri': self.uri.value
        }
        
        return Serialization.serialize_dict(type_as_dict)
         
            
    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'SourceDescription':
        # TODO Hande Resource/URI
        
        # Basic fields
        id_ = data.get('id')
        rt = ResourceType(data['resourceType']) if data.get('resourceType') else None

        # Sub-objects
        citations    = [SourceCitation._from_json_(c) for c in data.get('citations', [])]
        about        = URI._from_json_(data['about']) if data.get('about') else None
        mediator     = Resource._from_json_(data['mediator']) if data.get('mediator') else None
        publisher    = Resource._from_json_(data['publisher']) if data.get('publisher') else None
        authors      = [Resource._from_json_(a) for a in data.get('authors', [])]
        sources      = [SourceReference._from_json_(s) for s in data.get('sources', [])]
        analysis     = Resource._from_json_(data['analysis']) if data.get('analysis') else None
        component_of = SourceReference._from_json_(data['componentOf']) if data.get('componentOf') else None
        titles       = [TextValue._from_json_(t) for t in data.get('titles', [])]
        notes        = [Note._from_json_(n) for n in data.get('notes', [])]
        attribution  = Attribution._from_json_(data['attribution']) if data.get('attribution') else None
        rights       = [URI._from_json_(r) for r in data.get('rights', [])]
        coverage     = [Coverage._from_json_(cvg) for cvg in data.get('coverage',[])] 
        descriptions = [TextValue._from_json_(d) for d in data.get('descriptions', [])]
        identifiers  = IdentifierList._from_json_(data.get('identifiers', []))
        
        created      = Date._from_json_(data['created']) if data.get('created') else None
        modified     = data.get('modified',None)
        published    = Date._from_json_(data['published']) if data.get('published') else None
        repository   = Agent._from_json_(data['repository']) if data.get('repository') else None

        return cls(
            id=id_, resourceType=rt, citations=citations,
            mediaType=data.get('mediaType'), about=about,
            mediator=mediator, publisher=publisher,
            authors=authors, sources=sources,
            analysis=analysis, componentOf=component_of,
            titles=titles, notes=notes, attribution=attribution,
            rights=rights, coverage=coverage,
            descriptions=descriptions, identifiers=identifiers,
            created=created, modified=modified,
            published=published, repository=repository
        )

    