"""
Notebook utility functions for reading, writing, validating, and manipulating notebook files and cells.
"""
import nbformat
from pathlib import Path
from jupyter_agent_toolkit.notebook.paths import ensure_allowed, ensure_allowed_for_write

def validate_notebook(nb: nbformat.NotebookNode) -> None:
    nbformat.validate(nb)

def atomic_write_notebook(nb: nbformat.NotebookNode, path: Path) -> None:
    target = ensure_allowed_for_write(path)
    tmp = target.with_suffix(target.suffix + ".tmp")
    nbformat.write(nb, tmp)
    tmp.replace(target)

def load_notebook(path: Path) -> nbformat.NotebookNode:
    p = ensure_allowed(path)
    return nbformat.read(p, as_version=4)

def save_notebook(nb: nbformat.NotebookNode, path: Path, validate: bool = True) -> None:
    # Convert outputs to NotebookNode objects for nbformat compatibility
    import nbformat as _nbformat
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code" and "outputs" in cell:
            cell["outputs"] = [_nbformat.from_dict(out) if not isinstance(out, _nbformat.NotebookNode) else out for out in cell["outputs"]]
    if validate:
        validate_notebook(nb)
    atomic_write_notebook(nb, path)
