from typing import List, Optional

from .URI import URI
    
class Resource:
    """
    Class used to track and resolve URIs and references between datastores.

    Parameters
    ----------
    
    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    def __init__(self,uri: Optional[URI|str] = None, id:Optional[str] = None,top_lvl_object: Optional[object] = None,target= None) -> None:
        
        self.resource = URI.from_url(uri.value)
        self.Id = id

        self.type = None
        self.resolved = False
        self.target: object = target
        self.remote: bool | None = None    # is the resource pointed to persitent on a remote datastore?

        if target:
            self.resource = target._uri
            self.Id = target.id
            self.type = type(target)
   
    @property
    def _as_dict_(self):
        return {'resource':self.resource.value,
                'resourceId':self.Id}

def get_resource_as_dict(value):
    """
    If value is truthy:
      - If it's already a Resource, return it.
      - Otherwise, wrap it in Resource using (value._uri, value.id).
    Returns None if value is falsy.
    """
    
    if not value:
        return None

    if isinstance(value, Resource):
        return value._as_dict_
    
    try:
        return Resource(
            getattr(value, "uri", None),
            getattr(value, "id", None)
        )._as_dict_
    except AttributeError:
        print('get_resource_as_dict',type(value),value)
        print((f"value: {value} as inproper attributes"))
        exit()

    