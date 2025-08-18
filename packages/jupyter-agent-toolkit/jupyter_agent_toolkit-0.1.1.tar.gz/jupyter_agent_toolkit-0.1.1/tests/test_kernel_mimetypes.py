"""
Test mimetypes and serialization in kernel.
"""
import asyncio
from jupyter_agent_toolkit.kernel.session import create_session, get_session, destroy_session
from jupyter_agent_toolkit.kernel import serialization

def test_kernel_mimetypes():
    session_id = create_session()
    session = get_session(session_id)
    async def run():
        await session.kernel_manager.start()
        # Test serialization
        data = {'a': 1, 'b': 2}
        ser = serialization.serialize_value(data)
        deser = serialization.deserialize_value(ser["data"], ser["metadata"])
        assert deser == data
        # Test mimetypes using standard library
        import mimetypes as std_mimetypes
        mt, _ = std_mimetypes.guess_type('test.png')
        assert mt == 'image/png'
        await destroy_session(session_id)
    asyncio.run(run())

if __name__ == "__main__":
    test_kernel_mimetypes()
