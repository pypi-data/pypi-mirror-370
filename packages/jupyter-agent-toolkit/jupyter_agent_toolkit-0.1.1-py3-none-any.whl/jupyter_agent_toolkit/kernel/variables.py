
"""
Variable management utilities for kernel subsystem.
"""

import json
from typing import Any, List
from .variable_ops import VARIABLE_OPS


class VariableManager:
    """
    Language-agnostic variable manager using code templates and kernel executor.
    """
    def __init__(self, executor, language: str = "python"):
        self.executor = executor
        self.language = language


    async def set(self, name: str, value: Any, mimetype: str = None):
        """
        Set a variable in the kernel as its native Python object. Use mimetypes serialization only for agent/notebook boundary, not for in-kernel assignment.
        """
        # For JSON-serializable types, use JSON; for others, use repr and exec
        import json
        try:
            # Try to serialize as JSON and assign
            json_str = json.dumps(value)
            code = f"import json; {name} = json.loads('''{json_str}''')"
        except Exception:
            # Fallback: assign using repr (works for most Python objects)
            code = f"{name} = {repr(value)}"
        await self.executor.execute(code)


    async def get(self, name: str) -> Any:
        """
        Get a variable from the kernel as its native Python object. Use mimetypes serialization only for agent/notebook boundary, not for in-kernel retrieval.
        """
        code = f"import json; print(json.dumps(globals().get('{name}', None), default=str))"
        result = await self.executor.execute(code)
        out = result.stdout.strip()
        # Try to parse as JSON, else return as string
        import json
        try:
            return json.loads(out)
        except Exception:
            return out

    async def list(self) -> List[str]:
        code = VARIABLE_OPS.get(self.language, "list")
        result = await self.executor.execute(code)
        out = result.stdout.strip()
        try:
            return json.loads(out)
        except Exception:
            return []
