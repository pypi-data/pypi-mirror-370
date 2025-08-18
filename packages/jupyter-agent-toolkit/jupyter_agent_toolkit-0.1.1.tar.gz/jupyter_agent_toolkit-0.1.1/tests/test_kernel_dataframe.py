"""
Test DataFrame creation, manipulation, and export in kernel (no notebook).
"""
import asyncio
import os
from pathlib import Path
from jupyter_agent_toolkit.kernel.session import create_session, get_session, destroy_session
from jupyter_agent_toolkit.kernel.execution import KernelExecutor

def test_kernel_dataframe():
    out_csv = str(Path(__file__).parent / "data/test_kernel_output.csv")
    session_id = create_session()
    session = get_session(session_id)
    async def run():
        await session.kernel_manager.start()
        executor = KernelExecutor(session.kernel_manager)
        # var_mgr = VariableManager(executor)  # Unused variable removed
        code = [
            "import pandas as pd",
            "df = pd.DataFrame({'a': [1, 3], 'b': [2, 4]})",
            f"df.to_csv(r'{out_csv}', index=False)",
            "del df"
        ]
        for c in code:
            result = await executor.execute(c)
            if result.status != "ok":
                print(f"Error executing code: {c}")
                print(f"stderr: {result.stderr}")
                print(f"evalue: {result.evalue}")
                print(f"traceback: {result.traceback}")
            assert result.status == "ok"
        assert os.path.exists(out_csv)
        await destroy_session(session_id)
        os.remove(out_csv)
    asyncio.run(run())

if __name__ == "__main__":
    test_kernel_dataframe()
