import asyncio
from jupyter_agent_toolkit.kernel.session import create_session, get_session, destroy_session
from jupyter_agent_toolkit.kernel.execution import KernelExecutor
from jupyter_agent_toolkit.kernel.variables import VariableManager

def test_kernel_variable_manager():
    session_id = create_session()
    session = get_session(session_id)
    async def run():
        await session.kernel_manager.start()
        executor = KernelExecutor(session.kernel_manager)
        var_mgr = VariableManager(executor)
        # Create variable
        await executor.execute("x = 123")
        var_list = await var_mgr.list()
        assert "x" in var_list
        # Get variable
        value = await var_mgr.get("x")
        assert value == 123 or str(value) == "123"
        await destroy_session(session_id)
    asyncio.run(run())

if __name__ == "__main__":
    test_kernel_variable_manager()
