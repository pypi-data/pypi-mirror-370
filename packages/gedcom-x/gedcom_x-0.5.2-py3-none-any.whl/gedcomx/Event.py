from enum import Enum
from typing import List, Optional

from gedcomx.EvidenceReference import EvidenceReference
from gedcomx.Identifier import Identifier

from .Attribution import Attribution
from .Conclusion import Conclusion, ConfidenceLevel
from .Date import Date
from .Note import Note
from .PlaceReference import PlaceReference
from .SourceReference import SourceReference
from .Subject import Subject
from .Resource import Resource

class EventRoleType(Enum):
    Principal = "http://gedcomx.org/Principal"
    Participant = "http://gedcomx.org/Participant"
    Official = "http://gedcomx.org/Official"
    Witness = "http://gedcomx.org/Witness"
    
    @property
    def description(self):
        descriptions = {
            EventRole.Principal: "The person is the principal person of the event. For example, the principal of a birth event is the person that was born.",
            EventRole.Participant: "A participant in the event.",
            EventRole.Official: "A person officiating the event.",
            EventRole.Witness: "A witness of the event."
        }
        return descriptions.get(self, "No description available.")

class EventRole(Conclusion):
    identifier = 'http://gedcomx.org/v1/EventRole'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = [],
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 person: Resource = None,
                 type: Optional[EventRoleType] = None,
                 details: Optional[str] = None) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.person = person
        self.type = type
        self.details = details

class EventType(Enum):
    Adoption = "http://gedcomx.org/Adoption"
    AdultChristening = "http://gedcomx.org/AdultChristening"
    Annulment = "http://gedcomx.org/Annulment"
    Baptism = "http://gedcomx.org/Baptism"
    BarMitzvah = "http://gedcomx.org/BarMitzvah"
    BatMitzvah = "http://gedcomx.org/BatMitzvah"
    Birth = "http://gedcomx.org/Birth"
    Blessing = "http://gedcomx.org/Blessing"
    Burial = "http://gedcomx.org/Burial"
    Census = "http://gedcomx.org/Census"
    Christening = "http://gedcomx.org/Christening"
    Circumcision = "http://gedcomx.org/Circumcision"
    Confirmation = "http://gedcomx.org/Confirmation"
    Cremation = "http://gedcomx.org/Cremation"
    Death = "http://gedcomx.org/Death"
    Divorce = "http://gedcomx.org/Divorce"
    DivorceFiling = "http://gedcomx.org/DivorceFiling"
    Education = "http://gedcomx.org/Education"
    Engagement = "http://gedcomx.org/Engagement"
    Emigration = "http://gedcomx.org/Emigration"
    Excommunication = "http://gedcomx.org/Excommunication"
    FirstCommunion = "http://gedcomx.org/FirstCommunion"
    Funeral = "http://gedcomx.org/Funeral"
    Immigration = "http://gedcomx.org/Immigration"
    LandTransaction = "http://gedcomx.org/LandTransaction"
    Marriage = "http://gedcomx.org/Marriage"
    MilitaryAward = "http://gedcomx.org/MilitaryAward"
    MilitaryDischarge = "http://gedcomx.org/MilitaryDischarge"
    Mission = "http://gedcomx.org/Mission"
    MoveFrom = "http://gedcomx.org/MoveFrom"
    MoveTo = "http://gedcomx.org/MoveTo"
    Naturalization = "http://gedcomx.org/Naturalization"
    Ordination = "http://gedcomx.org/Ordination"
    Retirement = "http://gedcomx.org/Retirement"
    
    @property
    def description(self):
        descriptions = {
            EventType.Adoption: "An adoption event.",
            EventType.AdultChristening: "An adult christening event.",
            EventType.Annulment: "An annulment event of a marriage.",
            EventType.Baptism: "A baptism event.",
            EventType.BarMitzvah: "A bar mitzvah event.",
            EventType.BatMitzvah: "A bat mitzvah event.",
            EventType.Birth: "A birth event.",
            EventType.Blessing: "An official blessing event, such as at the hands of a clergy member or at another religious rite.",
            EventType.Burial: "A burial event.",
            EventType.Census: "A census event.",
            EventType.Christening: "A christening event at birth. Note: use AdultChristening for a christening event as an adult.",
            EventType.Circumcision: "A circumcision event.",
            EventType.Confirmation: "A confirmation event (or other rite of initiation) in a church or religion.",
            EventType.Cremation: "A cremation event after death.",
            EventType.Death: "A death event.",
            EventType.Divorce: "A divorce event.",
            EventType.DivorceFiling: "A divorce filing event.",
            EventType.Education: "An education or educational achievement event (e.g., diploma, graduation, scholarship, etc.).",
            EventType.Engagement: "An engagement to be married event.",
            EventType.Emigration: "An emigration event.",
            EventType.Excommunication: "An excommunication event from a church.",
            EventType.FirstCommunion: "A first communion event.",
            EventType.Funeral: "A funeral event.",
            EventType.Immigration: "An immigration event.",
            EventType.LandTransaction: "A land transaction event.",
            EventType.Marriage: "A marriage event.",
            EventType.MilitaryAward: "A military award event.",
            EventType.MilitaryDischarge: "A military discharge event.",
            EventType.Mission: "A mission event.",
            EventType.MoveFrom: "An event of a move (i.e., change of residence) from a location.",
            EventType.MoveTo: "An event of a move (i.e., change of residence) to a location.",
            EventType.Naturalization: "A naturalization event (i.e., acquisition of citizenship and nationality).",
            EventType.Ordination: "An ordination event.",
            EventType.Retirement: "A retirement event."
        }
        return descriptions.get(self, "No description available.")

    @staticmethod
    def guess(description):
        keywords_to_event_type = {
            "adoption": EventType.Adoption,
            "christening": EventType.Christening,
            "annulment": EventType.Annulment,
            "baptism": EventType.Baptism,
            "bar mitzvah": EventType.BarMitzvah,
            "bat mitzvah": EventType.BatMitzvah,
            "birth": EventType.Birth,
            "blessing": EventType.Blessing,
            "burial": EventType.Burial,
            "census": EventType.Census,
            "circumcision": EventType.Circumcision,
            "confirmation": EventType.Confirmation,
            "cremation": EventType.Cremation,
            "death": EventType.Death,
            "divorce": EventType.Divorce,
            "divorce filing": EventType.DivorceFiling,
            "education": EventType.Education,
            "engagement": EventType.Engagement,
            "emigration": EventType.Emigration,
            "excommunication": EventType.Excommunication,
            "first communion": EventType.FirstCommunion,
            "funeral": EventType.Funeral,
            "arrival": EventType.Immigration,
            "immigration": EventType.Immigration,
            "land transaction": EventType.LandTransaction,
            "marriage": EventType.Marriage,
            "military award": EventType.MilitaryAward,
            "military discharge": EventType.MilitaryDischarge,
            "mission": EventType.Mission,
            "move from": EventType.MoveFrom,
            "move to": EventType.MoveTo,
            "naturalization": EventType.Naturalization,
            "ordination": EventType.Ordination,
            "retirement": EventType.Retirement,
        }

        description_lower = description.lower()

        for keyword, event_type in keywords_to_event_type.items():
            if keyword in description_lower:
                return event_type

        return None  # Default to UNKNOWN if no match is found

class Event(Subject):
    identifier = 'http://gedcomx.org/v1/Event'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = [],
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 extracted: Optional[bool] = False,
                 evidence: Optional[List[EvidenceReference]] = [],
                 media: Optional[List[SourceReference]] = [],
                 identifiers: Optional[List[Identifier]] = [],
                 type: Optional[EventType] = None,
                 date: Optional[Date] = None,
                 place: Optional[PlaceReference] = None,
                 roles: Optional[List[EventRole]] = []) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)