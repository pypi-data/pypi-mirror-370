class PyLRCTool(Exception):
    """Exceptions used by pylrctool."""


class LRCParseError(PyLRCTool):
    """Error parsing LRC data."""


class LRCUnsupportedType(PyLRCTool):
    """Unsupported LRC event type."""


class LCRMissingTime(PyLRCTool):
    """LRC event missing time information."""
