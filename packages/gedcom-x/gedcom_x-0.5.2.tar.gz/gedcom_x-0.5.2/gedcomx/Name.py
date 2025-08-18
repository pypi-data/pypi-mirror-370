from enum import Enum
from typing import List,Optional

from .Attribution import Attribution
from .Conclusion import Conclusion, ConfidenceLevel
from .Date import Date
from .Note import Note
from .Serialization import Serialization
from .SourceReference import SourceReference
from .Resource import Resource


class NameType(Enum):
    BirthName = "http://gedcomx.org/BirthName"
    MarriedName = "http://gedcomx.org/MarriedName"
    AlsoKnownAs = "http://gedcomx.org/AlsoKnownAs"
    Nickname = "http://gedcomx.org/Nickname"
    AdoptiveName = "http://gedcomx.org/AdoptiveName"
    FormalName = "http://gedcomx.org/FormalName"
    ReligiousName = "http://gedcomx.org/ReligiousName"
    
    @property
    def description(self):
        descriptions = {
            NameType.BirthName: "Name given at birth.",
            NameType.MarriedName: "Name accepted at marriage.",
            NameType.AlsoKnownAs: "\"Also known as\" name.",
            NameType.Nickname: "Nickname.",
            NameType.AdoptiveName: "Name given at adoption.",
            NameType.FormalName: "A formal name, usually given to distinguish it from a name more commonly used.",
            NameType.ReligiousName: "A name given at a religious rite or ceremony."
        }
        return descriptions.get(self, "No description available.")

class NamePartQualifier(Enum):
    Title = "http://gedcomx.org/Title"
    Primary = "http://gedcomx.org/Primary"
    Secondary = "http://gedcomx.org/Secondary"
    Middle = "http://gedcomx.org/Middle"
    Familiar = "http://gedcomx.org/Familiar"
    Religious = "http://gedcomx.org/Religious"
    Family = "http://gedcomx.org/Family"
    Maiden = "http://gedcomx.org/Maiden"
    Patronymic = "http://gedcomx.org/Patronymic"
    Matronymic = "http://gedcomx.org/Matronymic"
    Geographic = "http://gedcomx.org/Geographic"
    Occupational = "http://gedcomx.org/Occupational"
    Characteristic = "http://gedcomx.org/Characteristic"
    Postnom = "http://gedcomx.org/Postnom"
    Particle = "http://gedcomx.org/Particle"
    RootName = "http://gedcomx.org/RootName"
    
    @property
    def description(self):
        descriptions = {
            NamePartQualifier.Title: "A designation for honorifics (e.g., Dr., Rev., His Majesty, Haji), ranks (e.g., Colonel, General), positions (e.g., Count, Chief), or other titles (e.g., PhD, MD). Name part qualifiers of type Title SHOULD NOT provide a value.",
            NamePartQualifier.Primary: "A designation for the most prominent name among names of that type (e.g., the primary given name). Name part qualifiers of type Primary SHOULD NOT provide a value.",
            NamePartQualifier.Secondary: "A designation for a name that is not primary in its importance among names of that type. Name part qualifiers of type Secondary SHOULD NOT provide a value.",
            NamePartQualifier.Middle: "Useful for cultures designating a middle name distinct from a given name and surname. Name part qualifiers of type Middle SHOULD NOT provide a value.",
            NamePartQualifier.Familiar: "A designation for one's familiar name. Name part qualifiers of type Familiar SHOULD NOT provide a value.",
            NamePartQualifier.Religious: "A name given for religious purposes. Name part qualifiers of type Religious SHOULD NOT provide a value.",
            NamePartQualifier.Family: "A name that associates a person with a group, such as a clan, tribe, or patriarchal hierarchy. Name part qualifiers of type Family SHOULD NOT provide a value.",
            NamePartQualifier.Maiden: "Original surname retained by women after adopting a new surname upon marriage. Name part qualifiers of type Maiden SHOULD NOT provide a value.",
            NamePartQualifier.Patronymic: "A name derived from a father or paternal ancestor. Name part qualifiers of type Patronymic SHOULD NOT provide a value.",
            NamePartQualifier.Matronymic: "A name derived from a mother or maternal ancestor. Name part qualifiers of type Matronymic SHOULD NOT provide a value.",
            NamePartQualifier.Geographic: "A name derived from associated geography. Name part qualifiers of type Geographic SHOULD NOT provide a value.",
            NamePartQualifier.Occupational: "A name derived from one's occupation. Name part qualifiers of type Occupational SHOULD NOT provide a value.",
            NamePartQualifier.Characteristic: "A name derived from a characteristic. Name part qualifiers of type Characteristic SHOULD NOT provide a value.",
            NamePartQualifier.Postnom: "A name mandated by law for populations in specific regions. Name part qualifiers of type Postnom SHOULD NOT provide a value.",
            NamePartQualifier.Particle: "A grammatical designation for articles, prepositions, conjunctions, and other words used as name parts. Name part qualifiers of type Particle SHOULD NOT provide a value.",
            NamePartQualifier.RootName: "The 'root' of a name part, as distinguished from prefixes or suffixes (e.g., the root of 'Wilkówna' is 'Wilk'). A RootName qualifier MUST provide a value property."
        }
        return descriptions.get(self, "No description available.")

class NamePartType(Enum):
    Prefix = "http://gedcomx.org/Prefix"
    Suffix = "http://gedcomx.org/Suffix"
    Given = "http://gedcomx.org/Given"
    Surname = "http://gedcomx.org/Surname"
    
    @property
    def description(self):
        descriptions = {
            NamePartType.Prefix: "A name prefix.",
            NamePartType.Suffix: "A name suffix.",
            NamePartType.Given: "A given name.",
            NamePartType.Surname: "A surname."
        }
        return descriptions.get(self, "No description available.")
    
class NamePart:
    identifier = 'http://gedcomx.org/v1/NamePart'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 type: Optional[NamePartType] = None,
                 value: Optional[str] = None,
                 qualifiers: Optional[List[NamePartQualifier]] = []) -> None:
        self.type = type
        self.value = value
        self.qualifiers = qualifiers
    
    def _as_dict_(self):
        return Serialization.serialize_dict(
            {'type': self.type.value if self.type else None,
             'value': self.value if self.value else None,
             'qualifiers': [qualifier.value for qualifier in self.qualifiers] if self.qualifiers else None})

    def __eq__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return (self.type == other.type and
                self.value == other.value and
                self.qualifiers == other.qualifiers)    

class NameForm:
    identifier = 'http://gedcomx.org/v1/NameForm'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, lang: Optional[str] = 'en', fullText: Optional[str] = None,parts: Optional[List[NamePart]] = []) -> None:
        self.lang = lang
        self.fullText = fullText
        self.parts = parts
    
    @property
    def _as_dict_(self):
        return Serialization.serialize_dict(
            {'lang': self.lang,
             'fullText': self.fullText,
             'parts': [part._as_dict_() for part in self.parts] if self.parts else None})
    
    def _fulltext_parts(self):
        pass

class Name(Conclusion):
    identifier = 'http://gedcomx.org/v1/Name'
    version = 'http://gedcomx.org/conceptual-model/v1'

    @staticmethod
    def simple(text: str):
        """
        Takes a string and returns a GedcomX Name Object
        """
        if text:
            text = text.replace("/","")
            parts = text.rsplit(' ', 1)
        
            # Assign val1 and val2 based on the split
            given = parts[0] if len(parts) > 1 else ""
            surname = parts[1] if len(parts) > 1 else parts[0]
            
            # Remove any '/' characters from both val1 and val2
            #given = given.replace('/', '')
            #surname = surname.replace('/', '')

            given_name_part = NamePart(type = NamePartType.Given, value=given)
            surname_part = NamePart(type = NamePartType.Surname, value=surname)

            name_form = NameForm(fullText=text,parts=[given_name_part,surname_part])
            name = Name(type=NameType.BirthName,nameForms=[name_form])
        else:
            name = Name()
        return name

    def __init__(self, id: str = None,
                 lang: str = 'en',
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Resource = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 type: Optional[NameType] = None,
                 nameForms: Optional[List[NameForm]]= None,
                 date: Optional[Date] = None) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.type = type
        self.nameForms = nameForms if nameForms else []
        self.date = date
    
    def _add_name_part(self, namepart_to_add: NamePart):
        if namepart_to_add and isinstance(namepart_to_add, NamePart):
            for current_namepart in self.nameForms[0].parts:
                if namepart_to_add == current_namepart:
                    return False
            self.nameForms[0].parts.append(namepart_to_add)
    
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
            
        name_as_dict = super()._as_dict_

        name_as_dict.update( {
            'type':self.type.value if self.type else None,
            'nameForms': [nameForm._as_dict_ for nameForm in self.nameForms],
            'date': self.date._as_dict_ if self.date else None})
        
        #del name_as_dict['id']
        # Serialize and exclude None values
        for key, value in name_as_dict.items():
            if value is not None:
                name_as_dict[key] = _serialize(value)

        # 3) merge and filter out None *at the top level*
        return {
            k: v
            for k, v in name_as_dict.items()
            if v is not None
        }
    
        return name_as_dict

def ensure_list(val):
    if val is None:
        return []
    return val if isinstance(val, list) else [val]
    
NamePart._from_json_ = classmethod(lambda cls, data: NamePart(
    type=NamePartType(data['type']) if 'type' in data else None,
    value=data.get('value'),
    qualifiers=[NamePartQualifier(q) for q in ensure_list(data.get('qualifiers'))]
))

NamePart._to_dict_ = lambda self: {
    'type': self.type.value if self.type else None,
    'value': self.value,
    'qualifiers': [q.value for q in self.qualifiers] if self.qualifiers else []
}


# NameForm
NameForm._from_json_ = classmethod(lambda cls, data: NameForm(
    lang=data.get('lang', 'en'),
    fullText=data.get('fullText'),
    parts=[NamePart._from_json_(p) for p in ensure_list(data.get('parts'))]
))

NameForm._to_dict_ = lambda self: {
    'lang': self.lang,
    'fullText': self.fullText,
    'parts': [p._to_dict_() for p in self.parts] if self.parts else []
}


# Name
Name._from_json_ = classmethod(lambda cls, data: cls(
    id=data.get('id'),
    lang=data.get('lang', 'en'),
    sources=[SourceReference._from_json_(s) for s in ensure_list(data.get('sources'))],
    analysis=Resource._from_json_(data['analysis']) if data.get('analysis') else None,
    notes=[Note._from_json_(n) for n in ensure_list(data.get('notes'))],
    confidence=ConfidenceLevel._from_json_(data['confidence']) if data.get('confidence') else None,
    attribution=Attribution._from_json_(data['attribution']) if data.get('attribution') else None,
    type=NameType(data['type']) if data.get('type') else None,
    nameForms=[NameForm._from_json_(nf) for nf in ensure_list(data.get('nameForms'))],
    date=Date._from_json_(data['date']) if data.get('date') else None
))



