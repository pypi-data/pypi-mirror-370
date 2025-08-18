"""

Test fixtures

"""
# ruff: noqa: ARG001
from typing import Any
import numpy
from numpy.typing import NDArray

import pytest       # type: ignore


FixtureRequest = Any
PRNG = numpy.random.RandomState(12345)


@pytest.fixture(scope='module',
                params=[(5, 5, 1),
                        (5, 1, 5),
                        (5, 5, 5),
                        # (7, 7, 7),
                       ])
def shape(request: FixtureRequest) -> tuple[int, ...]:
    return (3, *request.param)


@pytest.fixture(scope='module', params=[1.0, 1.5])
def epsilon_bg(request: FixtureRequest) -> float:
    return request.param

