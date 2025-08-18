"""
Custom error types for kernel subsystem.
"""

class KernelError(Exception):
    pass

class KernelExecutionError(KernelError):
    pass

class KernelTimeoutError(KernelError):
    pass
