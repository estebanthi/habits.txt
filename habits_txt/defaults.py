import os

DATE_FMT = "%Y-%m-%d"
COMMENT_CHAR = "#"
ALLOWED_QUOTES = ('"', "'")
BOOLEAN_TRUE = "yes"
BOOLEAN_FALSE = "no"
MEASURABLE_KEYWORD = "measurable"
APPDATA_PATH = os.path.join(os.path.expanduser("~"), ".habits.txt")
