"""
Kernel lifecycle management.
Manages kernel start, stop, restart, health checks, and exposes channels.
"""

import asyncio
import logging
from typing import Optional
from jupyter_client.manager import AsyncKernelManager
from jupyter_client.asynchronous.client import AsyncKernelClient
from .errors import KernelError

logger = logging.getLogger(__name__)

class KernelManager:
    """
    Manages a single Jupyter kernel using AsyncKernelManager and AsyncKernelClient.
    """
    def __init__(self, kernel_name: str = "python3", startup_timeout: float = 60.0):
        self.kernel_name = kernel_name
        self.startup_timeout = startup_timeout
        self._km: Optional[AsyncKernelManager] = None
        self._kc: Optional[AsyncKernelClient] = None
        self._lock = asyncio.Lock()

    async def start(self):
        async with self._lock:
            if self._km is not None:
                logger.warning("Kernel already started.")
                return
            self._km = AsyncKernelManager(kernel_name=self.kernel_name)
            await self._km.start_kernel()
            self._kc = self._km.client()
            self._kc.start_channels()
            await self._kc.wait_for_ready(timeout=self.startup_timeout)
            logger.info("Kernel started, channels opened, and kernel is ready.")

    async def shutdown(self):
        async with self._lock:
            if self._kc:
                try:
                    self._kc.stop_channels()
                except Exception as e:
                    logger.warning(f"Error stopping kernel channels: {e}")
            if self._km:
                try:
                    await self._km.shutdown_kernel(now=True)
                except Exception as e:
                    logger.warning(f"Error shutting down kernel: {e}")
            self._kc = None
            self._km = None
            logger.info("Kernel shutdown complete.")

    async def restart(self):
        async with self._lock:
            if not self._km:
                raise KernelError("No kernel to restart.")
            await self._km.restart_kernel(now=True)
            self._kc = self._km.client()
            self._kc.start_channels()
            await self._kc.wait_for_ready(timeout=self.startup_timeout)
            logger.info("Kernel restarted and ready.")

    async def is_alive(self) -> bool:
        if self._km is None:
            return False
        try:
            return bool(self._km.is_alive())
        except Exception:
            return False

    async def is_healthy(self) -> bool:
        if self._kc is None or self._km is None:
            return False
        try:
            msg_id = self._kc.kernel_info()
            for _ in range(10):
                msg = await self._kc.get_shell_msg(timeout=0.5)
                if msg and msg.get("parent_header", {}).get("msg_id") == msg_id:
                    return True
            return False
        except Exception as e:
            logger.warning(f"Kernel health check failed: {e}")
            return False

    @property
    def client(self) -> Optional[AsyncKernelClient]:
        return self._kc

    @property
    def shell_channel(self):
        return self._kc.shell_channel if self._kc else None

    @property
    def iopub_channel(self):
        return self._kc.iopub_channel if self._kc else None

    @property
    def stdin_channel(self):
        return self._kc.stdin_channel if self._kc else None

    @property
    def control_channel(self):
        return self._kc.control_channel if self._kc else None

    @property
    def hb_channel(self):
        return self._kc.hb_channel if self._kc else None
