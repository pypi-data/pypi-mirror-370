import asyncio
import os
from pathlib import Path
import nbformat
from jupyter_agent_toolkit.kernel.session import create_session, get_session, destroy_session
from jupyter_agent_toolkit.kernel.execution import KernelExecutor
from jupyter_agent_toolkit.notebook.cells import create_code_cell, create_markdown_cell
from jupyter_agent_toolkit.notebook.utils import save_notebook, load_notebook, validate_notebook
from jupyter_agent_toolkit.notebook.paths import ensure_allowed_for_write

def test_notebook_integration():
    nb_path = ensure_allowed_for_write(Path(__file__).parent / "notebook_integration_test.ipynb")
    nb = nbformat.v4.new_notebook()
    # Add markdown cell
    nb.cells.append(create_markdown_cell([
        "# Notebook Integration Test",
        "Test DataFrame creation, inspection, and export using notebook and kernel."
    ]))
    out_csv = str(Path(__file__).parent / "data/notebook_integration_output.csv")
    code_cells = [
        "import pandas as pd",
        "df = pd.DataFrame({'a': [1, 3], 'b': [2, 4]})",
        "df",
        "print(df.shape[0], df.shape[1])",
        f"df.to_csv(r'{out_csv}', index=False)",
        "del df"
    ]
    for code in code_cells:
        nb.cells.append(create_code_cell([code]))
    save_notebook(nb, nb_path)
    session_id = create_session()
    session = get_session(session_id)
    async def run():
        await session.kernel_manager.start()
        executor = KernelExecutor(session.kernel_manager)
        for idx, code in enumerate(code_cells):
            result = await executor.execute(code)
            assert result.status == "ok"
            nb = load_notebook(nb_path)
            outputs = list(result.outputs) if result.outputs else []
            if result.stdout:
                outputs.append({
                    "output_type": "stream",
                    "name": "stdout",
                    "text": result.stdout,
                })
            nb.cells[idx + 1]["outputs"] = outputs
            nb.cells[idx + 1]["execution_count"] = result.execution_count
            save_notebook(nb, nb_path)
        assert os.path.exists(out_csv)
        validate_notebook(nb)
        await destroy_session(session_id)
        os.remove(out_csv)
        os.remove(nb_path)
    asyncio.run(run())

if __name__ == "__main__":
    test_notebook_integration()
