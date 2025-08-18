"""
High-level notebook cell manipulation utilities for nbformat notebooks.
"""

from nbformat import NotebookNode
import uuid
from typing import List, Optional, Dict, Any


def create_code_cell(source: List[str], metadata: Optional[Dict[str, Any]] = None, outputs: Optional[List[Any]] = None, execution_count: Optional[int] = None) -> NotebookNode:
    """Create a new code cell."""
    cell = NotebookNode()
    cell.cell_type = "code"
    cell.metadata = metadata or {"language": "python"}
    cell.source = source
    cell.outputs = outputs or []
    cell.execution_count = execution_count
    cell.id = uuid.uuid4().hex[:16]
    return cell


def create_markdown_cell(source: List[str], metadata: Optional[Dict[str, Any]] = None) -> NotebookNode:
    """Create a new markdown cell."""
    cell = NotebookNode()
    cell.cell_type = "markdown"
    cell.metadata = metadata or {"language": "markdown"}
    cell.source = source
    cell.id = uuid.uuid4().hex[:16]
    return cell


def insert_cell(notebook: NotebookNode, cell: NotebookNode, index: int) -> None:
    """Insert a cell at a specific index."""
    notebook.cells.insert(index, cell)


def append_cell(notebook: NotebookNode, cell: NotebookNode) -> None:
    """Append a cell to the end of the notebook."""
    notebook.cells.append(cell)


def remove_cell(notebook: NotebookNode, index: int) -> None:
    """Remove a cell at a specific index."""
    del notebook.cells[index]


def get_cell(notebook: NotebookNode, index: int) -> NotebookNode:
    """Get a cell by index."""
    return notebook.cells[index]


def update_cell_source(notebook: NotebookNode, index: int, new_source: List[str]) -> None:
    """Update the source of a cell at a specific index."""
    notebook.cells[index].source = new_source


def update_cell_metadata(notebook: NotebookNode, index: int, new_metadata: Dict[str, Any]) -> None:
    """Update the metadata of a cell at a specific index."""
    notebook.cells[index].metadata = new_metadata
