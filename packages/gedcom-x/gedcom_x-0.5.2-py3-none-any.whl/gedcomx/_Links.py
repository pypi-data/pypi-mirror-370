from typing import List, Optional

class _Link():
    def __init__(self,category: str, key_val_pairs:  dict) -> None:
        self._category = category
        self._kvps: dict = key_val_pairs if key_val_pairs else {}
    
    def _add_kvp(self, key, value):
        pass

class _LinkList():
    def __init__(self) -> None:
        self.links = {}

    def add(self,link: _Link):
        if link and isinstance(link,_Link):
            if link._category in self.links.keys():
                self.links[link._category].append(link._kvps)
            else:
                self.links[link._category] = [link._kvps]
        

    @classmethod
    def _from_json_(cls,data: dict):
        
        link_list = _LinkList()
        for category in data.keys():
            link_list.add(_Link(category,data[category]))
        
        return link_list
    
    @property
    def _as_dict_(self) -> dict:
        return self.links


        