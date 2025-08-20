import re

EXTENDS_REGEX = re.compile(r"\{%-?\s*extends\s+\"([^\"]+)\"\s*-?%\}")
MIXIN_REGEX = re.compile(r"\{%-?\s*mixin\s+((?:\"[^\"]+\"\s*,\s*)*\"[^\"]+\")\s*-?%\}", re.MULTILINE)
INCLUDE_REGEX = re.compile(r"\{%-?\s*include\s+\"([^\"]+)\"(?:\s+with\s+(\{[\s\S]*?\}))?\s*-?%\}", re.MULTILINE)
BLOCK_REGEX = re.compile(r"\{%-?\s*block\s+([a-zA-Z0-9_:-]+)\s*-?%\}([\s\S]*?)\{%-?\s*endblock\s*-?%\}", re.MULTILINE)
VAR_REGEX = re.compile(r"\{\{-?\s*([a-zA-Z0-9_.]+)(?:\s*\|\s*default\((?:\"([^\"]*)\"|'([^']*)')\))?\s*-?\}\}")
SUPER_REGEX = re.compile(r"\{\{-?\s*super\(\s*\)\s*-?\}\}")
COMMENT_REGEX = re.compile(r"\{#-[\s\S]*?-#\}|\{#[\s\S]*?#\}")
# For and if patterns for initial search; nested processing uses manual scanning
IF_OPEN_REGEX = re.compile(r"\{%-?\s*if\s+([^%]+?)\s*-?%\}")
ELSEIF_REGEX = re.compile(r"\{%-?\s*elseif\s+([^%]+?)\s*-?%\}")
ELSE_TAG_REGEX = re.compile(r"\{%-?\s*else\s*-?%\}")
ENDIF_TAG_REGEX = re.compile(r"\{%-?\s*endif\s*-?%\}")
FOR_OPEN_REGEX = re.compile(r"\{%-?\s*for\s+([a-zA-Z0-9_]+)\s+in\s+([^%]+?)\s*-?%\}")
ENDFOR_TAG_REGEX = re.compile(r"\{%-?\s*endfor\s*-?%\}")
