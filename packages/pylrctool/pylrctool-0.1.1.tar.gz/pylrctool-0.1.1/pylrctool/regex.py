# --- ID TAGS ---
TAG_NAME = r"(?:ti|ar|al|au|lr|length|by|offset|re|tool|ve)"
TAG_VALUE = r"[^\]]*"
ID_TAG = rf"^\[(?P<tag>{TAG_NAME}):(?P<value>{TAG_VALUE})\]$"

# --- SPECIAL CASES ---
OFFSET_TAG = r"^\[offset:(?P<offset>[+-]?\d+)\]$"
LENGTH_TAG = r"^\[length:\s*(?P<minutes>\d{{1,2}}):(?P<seconds>\d{{2}})\]$"

# --- COMMENTS ---
COMMENT_TAG = r"^\#(?P<comment>.*)$"

# --- TIMESTAMPS ---
TIME_TAG = r"\[(?P<minutes>\d{2}):(?P<seconds>\d{2})(?:\.(?P<centiseconds>\d{1,2}))?\]"
TIME_TAG_MULTI = rf"(?:{TIME_TAG})+"

# --- TIMED LYRICS ---
TIMED_LINE = rf"^{TIME_TAG_MULTI}(?P<lyric>.*)$"

# --- COMBINED MATCH ---
LRC_LINE = rf"(?:{ID_TAG}|{COMMENT_TAG}|{TIMED_LINE})"
