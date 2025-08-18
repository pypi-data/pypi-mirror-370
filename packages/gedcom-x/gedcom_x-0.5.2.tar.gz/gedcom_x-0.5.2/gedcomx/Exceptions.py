

class GedcomXError(Exception):
    """Base for all app-specific errors."""

class TagConversionError(GedcomXError):
    def __init__(self, record,levelstack):
        msg = f"Cannot convert: #{record.line} TAG: {record.tag} {record.xref if record.xref else ''} Value:{record.value} STACK: {type(levelstack[record.level-1]).__name__}"
        super().__init__(msg)
        