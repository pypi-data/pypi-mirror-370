"""
Central registry for variable operation code templates (variable ops) for multiple languages.
"""

from typing import Dict

class VariableOpsRegistry:
    def __init__(self):
        self.ops: Dict[str, Dict[str, str]] = {}

    def register(self, language: str, list_code: str, get_code: str, set_code: str):
        self.ops[language] = {
            "list": list_code,
            "get": get_code,
            "set": set_code,
        }

    def get(self, language: str, op: str) -> str:
        if language not in self.ops or op not in self.ops[language]:
            raise ValueError(f"No code template for {op} in language {language}")
        return self.ops[language][op]

# Example: Register Python variable ops
VARIABLE_OPS = VariableOpsRegistry()
VARIABLE_OPS.register(
    "python",
    list_code="import json; print(json.dumps([k for k in globals() if not k.startswith('_')]))",
    get_code="import json; print(json.dumps({name}))",
    set_code="import json; {name} = json.loads('''{value}''')",
)
