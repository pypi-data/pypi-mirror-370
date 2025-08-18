from enum import Enum
from typing import Optional, List

from gedcomx.Attribution import Attribution
#from gedcomx.Conclusion import ConfidenceLevel
from gedcomx.Note import Note
from gedcomx.SourceReference import SourceReference
from gedcomx.Resource import Resource

from .Conclusion import Conclusion

class DocumentType(Enum):
    Abstract = "http://gedcomx.org/Abstract"
    Transcription = "http://gedcomx.org/Transcription"
    Translation = "http://gedcomx.org/Translation"
    Analysis = "http://gedcomx.org/Analysis"
    
    @property
    def description(self):
        descriptions = {
            DocumentType.Abstract: "The document is an abstract of a record or document.",
            DocumentType.Transcription: "The document is a transcription of a record or document.",
            DocumentType.Translation: "The document is a translation of a record or document.",
            DocumentType.Analysis: "The document is an analysis done by a researcher; a genealogical proof statement is an example of one kind of analysis document."
        }
        return descriptions.get(self, "No description available.")

class TextType(Enum):
    plain = 'plain'
    xhtml = 'xhtml'

class Document(Conclusion):
    identifier = 'http://gedcomx.org/v1/Document'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[object] = None, # ConfidenceLevel
                 attribution: Optional[Attribution] = None,
                 type: Optional[DocumentType] = None,
                 extracted: Optional[bool] = None, # Default to False
                 textType: Optional[TextType] = None,
                 text: Optional[str] = None,
                 ) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.type = type
        self.extracted = extracted
        self.textType = textType
        self.text = text