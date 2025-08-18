"""
imuBias submodule
"""
from __future__ import annotations
import numpy
import typing
__all__: list[str] = ['ConstantBias']
M = typing.TypeVar("M", bound=int)
class ConstantBias:
    @staticmethod
    def Identity() -> ConstantBias:
        """
        identity for group operation
        """
    def __add__(self, arg0: ConstantBias) -> ConstantBias:
        ...
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, biasAcc: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], biasGyro: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    def __neg__(self) -> ConstantBias:
        ...
    def __repr__(self, s: str = '') -> str:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def __sub__(self, arg0: ConstantBias) -> ConstantBias:
        ...
    def accelerometer(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        get accelerometer bias
        """
    def correctAccelerometer(self, measurement: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Correct an accelerometer measurement using this bias model, and optionally compute Jacobians.
        """
    def correctGyroscope(self, measurement: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Correct a gyroscope measurement using this bias model, and optionally compute Jacobians.
        """
    def deserialize(self, serialized: str) -> None:
        ...
    def equals(self, expected: ConstantBias, tol: float) -> bool:
        """
        equality up to tolerance
        """
    def gyroscope(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        get gyroscope bias
        """
    def localCoordinates(self, b: ConstantBias) -> numpy.ndarray[tuple[typing.Literal[6], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
    def print(self, s: str = '') -> None:
        """
        print with optional string
        """
    def retract(self, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> ConstantBias:
        """
        The retract function.
        """
    def serialize(self) -> str:
        ...
    def vector(self) -> numpy.ndarray[tuple[typing.Literal[6], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        return the accelerometer and gyro biases in a single vector
        """
