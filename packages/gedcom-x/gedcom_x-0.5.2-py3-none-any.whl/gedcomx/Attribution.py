
from datetime import datetime
from typing import Optional, Dict, Any

from .Agent import Agent
from .Resource import Resource, get_resource_as_dict
from .Serialization import Serialization

class Attribution:
    """Attribution Information for a Genealogy, Conclusion, Subject and child classes

    Args:
        contributor (Agent):            Contributor to object being attributed.
        modified (timestamp):           timestamp for when this record was modified.
        changeMessage (str):            Birth date (YYYY-MM-DD).
        creator (Agent, optional):      Creator of object being attributed.
        created (timestamp):            timestamp for when this record was created

    Raises:
        
    """
    identifier = 'http://gedcomx.org/v1/Attribution'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,contributor: Optional[Agent | Resource] = None,
                 modified: Optional[datetime] = None,
                 changeMessage: Optional[str] = None,
                 creator: Optional[Agent | Resource] = None,
                 created: Optional[datetime] = None) -> None:
               
        self.contributor = contributor
        self.modified = modified
        self.changeMessage = changeMessage
        self.creator = creator
        self.created = created
        
    @property
    def _as_dict_(self) -> Dict[str, Any]:
        """
        Serialize Attribution to a JSON-ready dict, skipping None values.
        """
        type_as_dict: Dict[str, Any] = {}
        type_as_dict['contributor'] = get_resource_as_dict(self.contributor)       
        type_as_dict['modified'] = self.modified if self.modified else None
        type_as_dict['changeMessage'] = self.changeMessage if self.changeMessage else None 
        type_as_dict['creator'] = get_resource_as_dict(self.creator)         
        type_as_dict['created'] = self.created if self.created else None
                    
        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'Attribution':
        """
        Construct Attribution from a dict (as parsed from JSON).
        Handles 'created' and 'modified' as ISO strings or epoch ms ints.
        """
        # contributor
        
        contrib = None
        if 'contributor' in data:
            contrib_data = data['contributor']
            
            contrib = Resource(contrib_data['resource'],contrib_data['resourceId'])

        # creator
        creat = None
        if 'creator' in data:
            raw = data['creator']
            if isinstance(raw, dict):
                creat = Resource._from_json_(raw)
            elif isinstance(raw, str):
                creat = Resource(uri=raw)

        # parse created date
        raw_created = data.get('created')
        if isinstance(raw_created, (int, float)):
            created_dt = datetime.fromtimestamp(raw_created / 1000.0)
        elif isinstance(raw_created, str):
            created_dt = datetime.fromisoformat(raw_created)
        else:
            created_dt = None

        # parse modified date
        raw_modified = data.get('modified')
        if isinstance(raw_modified, (int, float)):
            modified_dt = datetime.fromtimestamp(raw_modified / 1000.0)
        elif isinstance(raw_modified, str):
            modified_dt = datetime.fromisoformat(raw_modified)
        else:
            modified_dt = None

        change_msg = data.get('changeMessage')

        return cls(
            contributor=contrib,
            created=created_dt,
            creator=creat,
            modified=modified_dt,
            changeMessage=change_msg
        )
