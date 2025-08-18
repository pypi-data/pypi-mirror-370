import asyncio
from jupyter_agent_toolkit.kernel.session import create_session, get_session, destroy_session
from jupyter_agent_toolkit.kernel.execution import KernelExecutor

def test_kernel_basic():
    session_id = create_session()
    session = get_session(session_id)
    async def run():
        await session.kernel_manager.start()
        executor = KernelExecutor(session.kernel_manager)
        result = await executor.execute("print('Hello from kernel!')\nx = 42\nx")
        assert result.status == "ok"
        assert "Hello from kernel!" in result.stdout
        await destroy_session(session_id)
    asyncio.run(run())

if __name__ == "__main__":
    test_kernel_basic()
