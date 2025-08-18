from typing import Optional

class Qualifier:
    identifier = 'http://gedcomx.org/v1/Qualifier'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, name: str, value: Optional[str]) -> None:
        self.name = name
        self.value = value
    
    @property
    def __as_dict__(self):
        from .Serialization import serialize_to_dict

        data =  {
            "name":self.name if self.name else None,
            "value":self.value if self.value else None
        }

        return serialize_to_dict(data,False)
    
    # Qualifier
Qualifier._from_json_ = classmethod(lambda cls, data: Qualifier(
    name=data.get('name'),
    value=data.get('value')
))

