from typing import Protocol, Final
from dataclasses import dataclass


class Logger(Protocol):
    def __call__(self, message: str) -> None:
        """Logs a message. This method will be invoked when some verification fails."""
        ...


class Debugger(Protocol):
    def __call__(self) -> None:
        """Starts the debugger. This method will be invoked when some verification fails."""
        ...


class NoLogger:
    """A no-op logger that does nothing when called."""

    def __call__(self, message: str) -> None:
        """Does nothing. This is used when logging is disabled."""
        pass


class NoDebugger:
    """A no-op debugger that does nothing when called."""

    def __call__(self) -> None:
        """Does nothing. This is used when debugging is disabled."""
        pass


@dataclass
class GlobalTypingConfig:
    logger: Logger = NoLogger()
    debugger: Debugger = NoDebugger()

    def configure(
        self, *, logger: Logger | None = None, debugger: Debugger | None = None
    ) -> None:
        """Configures the global typing settings.

        Args:
            logger: The logger to be used for logging messages when a verification fails.
                If None, the logging configuration will not be changed.
            debugger: The debugger to be triggered when a verification fails. This can be used,
                for example, to configure `ipdb` to be started, or another debugging tool.
                If None, the debugging configuration will not be changed.
        """
        if logger is not None:
            self.logger = logger

        if debugger is not None:
            self.debugger = debugger


config: Final[GlobalTypingConfig] = GlobalTypingConfig()
"""
The global typing configuration for numtypes can be modified/accessed via this variable.

Example:
    You can configure `ipdb` to be the debugger that is started whenever the shape of an array
    is not as expected.

    ```python
    >>> from numtypes.debug import config
    >>> import ipdb
    >>> config.configure(debugger=ipdb.set_trace)
    ```
"""


def verify(condition: bool, message: str) -> None:
    """Verifies that the given condition is True. If not, logs a message and starts the debugger.

    Args:
        condition: The condition to verify.
        message: The message to log if the condition is False.

    Raises:
        AssertionError: If the condition is False.
    """
    if condition:
        return

    config.debugger()
    config.logger(message)

    assert condition, message
