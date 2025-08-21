from dataclasses import dataclass

from numtypes import config, shape_of

import numpy as np
from pytest import fixture


@dataclass
class StubDebugger:
    called: bool = False

    def __call__(self) -> None:
        self.called = True


@dataclass
class StubLogger:
    message: str | None = None

    def __call__(self, message: str) -> None:
        self.message = message


@fixture(scope="function")
def debugger() -> StubDebugger:
    return StubDebugger()


@fixture(scope="function")
def logger() -> StubLogger:
    return StubLogger()


def test_that_configured_debugger_is_not_called_when_shape_is_as_expected(
    debugger: StubDebugger,
) -> None:
    config.configure(debugger=debugger)

    assert not debugger.called

    assert shape_of(np.array([1, 2, 3]), matches=(3,))

    assert not debugger.called


def test_that_configured_debugger_is_called_when_shape_is_not_as_expected(
    debugger: StubDebugger,
) -> None:
    config.configure(debugger=debugger)

    assert not debugger.called

    try:
        assert shape_of(np.array([1, 2, 3]), matches=(4,))
    except AssertionError:
        pass

    assert debugger.called


def test_that_configured_logger_is_not_called_when_shape_is_as_expected(
    logger: StubLogger,
) -> None:
    config.configure(logger=logger)

    assert logger.message is None

    assert shape_of(np.array([1, 2, 3]), matches=(3,))

    assert logger.message is None


def test_that_configured_logger_is_called_when_shape_is_not_as_expected(
    logger: StubLogger,
) -> None:
    config.configure(logger=logger)

    assert logger.message is None

    try:
        assert shape_of(np.array([1, 2, 3]), matches=(4,))
    except AssertionError:
        pass

    assert logger.message is not None
