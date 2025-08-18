from abc import ABC, abstractmethod


class LazyLLMHook(ABC):
    """Abstract base class for LazyLLM's hook system, used to insert custom logic before and after function or method execution.

This class is an abstract base class (ABC) that defines the basic interface for the hook system. By inheriting from this class and implementing its abstract methods, you can create custom hooks to monitor, log, or modify function execution processes.

Args:
    obj: The object to monitor (usually a function or method). This object will be stored in the hook instance for use by other methods.

**Note**: This class is an abstract base class and cannot be instantiated directly. You must inherit from this class and implement all abstract methods to use it.
"""

    @abstractmethod
    def __init__(self, obj):
        pass

    @abstractmethod
    def pre_hook(self, *args, **kwargs):
        """Pre-hook method, called before function execution.

Args:
    *args: Arguments passed to the monitored function
    **kwargs: Keyword arguments passed to the monitored function
"""
        pass

    @abstractmethod
    def post_hook(self, output):
        """Post-hook method, called after function execution.

Args:
    output: The return value of the monitored function

**Returns:**

- The processed output value. Usually returns the original output, but can also modify or wrap the output.
"""
        pass

    @abstractmethod
    def report():
        """Generate a report of hook execution.

**Returns:**

- Relevant information or statistics about hook execution.
"""
        pass
