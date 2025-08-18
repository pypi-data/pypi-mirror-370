
"""
Output hooks and event callbacks for kernel subsystem.
"""

from typing import Callable, List


class KernelHooks:
    """Register and trigger output/callback hooks for kernel execution lifecycle."""

    def __init__(self):
        self._output_hooks: List[Callable[[dict], None]] = []
        self._before_execute_hooks: List[Callable[[str], None]] = []
        self._after_execute_hooks: List[Callable[[object], None]] = []
        self._on_error_hooks: List[Callable[[Exception], None]] = []

    # Output hooks
    def register_output_hook(self, hook: Callable[[dict], None]):
        self._output_hooks.append(hook)
    def unregister_output_hook(self, hook: Callable[[dict], None]):
        self._output_hooks.remove(hook)
    def trigger_output_hooks(self, msg: dict):
        for hook in self._output_hooks:
            try:
                hook(msg)
            except Exception:
                pass

    # Before-execute hooks
    def register_before_execute_hook(self, hook: Callable[[str], None]):
        self._before_execute_hooks.append(hook)
    def unregister_before_execute_hook(self, hook: Callable[[str], None]):
        self._before_execute_hooks.remove(hook)
    def trigger_before_execute_hooks(self, code: str):
        for hook in self._before_execute_hooks:
            try:
                hook(code)
            except Exception:
                pass

    # After-execute hooks
    def register_after_execute_hook(self, hook: Callable[[object], None]):
        self._after_execute_hooks.append(hook)
    def unregister_after_execute_hook(self, hook: Callable[[object], None]):
        self._after_execute_hooks.remove(hook)
    def trigger_after_execute_hooks(self, result: object):
        for hook in self._after_execute_hooks:
            try:
                hook(result)
            except Exception:
                pass

    # On-error hooks
    def register_on_error_hook(self, hook: Callable[[Exception], None]):
        self._on_error_hooks.append(hook)
    def unregister_on_error_hook(self, hook: Callable[[Exception], None]):
        self._on_error_hooks.remove(hook)
    def trigger_on_error_hooks(self, error: Exception):
        for hook in self._on_error_hooks:
            try:
                hook(error)
            except Exception:
                pass

# Singleton instance for global use
kernel_hooks = KernelHooks()
