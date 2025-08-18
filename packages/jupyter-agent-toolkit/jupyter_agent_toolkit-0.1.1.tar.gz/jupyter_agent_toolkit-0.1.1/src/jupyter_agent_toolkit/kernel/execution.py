"""
Code execution and result parsing for kernel subsystem.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .manager import KernelManager
from .errors import KernelExecutionError
from .hooks import kernel_hooks

@dataclass
class ExecutionResult:
    stdout: str = ""
    stderr: str = ""
    execution_count: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    ename: Optional[str] = None
    evalue: Optional[str] = None
    traceback: Optional[List[str]] = None
    status: str = "ok"  # "ok" | "error" | "timeout" | "exception"
    interrupted: bool = False

class KernelExecutor:
    """Handles code execution and output/result parsing."""

    def __init__(self, kernel_manager: KernelManager):
        self.kernel_manager = kernel_manager

    async def execute(
        self,
        code: str,
        timeout: Optional[float] = 30.0,
        store_history: bool = True,
        allow_stdin: bool = False,
        stop_on_error: bool = True,
        auto_interrupt_on_timeout: bool = True,
    ) -> ExecutionResult:
        """
        Execute code asynchronously in the kernel and return a structured result.
        Uses execute_interactive and hooks for robust async execution.
        """
        km = self.kernel_manager
        kc = km.client
        if kc is None:
            raise KernelExecutionError("Kernel client is not available.")

        res = ExecutionResult()

        # Trigger before-execute hooks
        kernel_hooks.trigger_before_execute_hooks(code)

        def output_hook(msg):
            # Call all registered output hooks
            kernel_hooks.trigger_output_hooks(msg)
            # Default result parsing logic
            msg_type = msg["header"]["msg_type"]
            content = msg.get("content", {})
            if msg_type == "execute_input":
                res.execution_count = content.get("execution_count", res.execution_count)
            elif msg_type == "stream":
                name = content.get("name")
                text = content.get("text", "")
                if name == "stdout":
                    res.stdout += text
                elif name == "stderr":
                    res.stderr += text
                else:
                    res.stderr += text
            elif msg_type in ("display_data", "execute_result"):
                data = content.get("data", {}) or {}
                res.result_data = data or res.result_data
                if "execution_count" in content:
                    res.execution_count = content.get("execution_count", res.execution_count)
                output = {"output_type": msg_type, "data": data, "metadata": content.get("metadata", {})}
                if msg_type == "execute_result":
                    output["execution_count"] = res.execution_count
                res.outputs.append(output)
            elif msg_type == "clear_output":
                res.outputs.clear()
                res.stdout = ""
                res.stderr = ""
            elif msg_type == "error":
                res.status = "error"
                res.ename = content.get("ename")
                res.evalue = content.get("evalue")
                res.traceback = content.get("traceback", [])

        try:
            reply = await kc.execute_interactive(
                code,
                silent=False,
                store_history=store_history,
                allow_stdin=allow_stdin,
                stop_on_error=stop_on_error,
                timeout=timeout,
                output_hook=output_hook,
            )
            if res.status not in ("error", "timeout"):
                res.status = reply.get("content", {}).get("status", "ok")
            if "execution_count" in reply.get("content", {}):
                res.execution_count = reply["content"]["execution_count"]
            # Trigger after-execute hooks
            kernel_hooks.trigger_after_execute_hooks(res)
        except TimeoutError as te:
            res.status = "timeout"
            if auto_interrupt_on_timeout:
                try:
                    await km._km.interrupt_kernel()
                    res.interrupted = True
                except Exception:
                    pass
            # Trigger on-error hooks
            kernel_hooks.trigger_on_error_hooks(te)
        except Exception as e:
            res.status = "error"
            res.evalue = str(e)
            # Trigger on-error hooks
            kernel_hooks.trigger_on_error_hooks(e)
        return res
