"""
so3 submodule
"""
from __future__ import annotations
import numpy
import typing
__all__: list[str] = ['DexpFunctor', 'ExpmapFunctor']
class DexpFunctor(ExpmapFunctor):
    @typing.overload
    def __init__(self, omega: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def __init__(self, omega: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]], nearZeroThresholdSq: float, nearPiThresholdSq: float) -> None:
        ...
    def applyLeftJacobian(self, v: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Multiplies with leftJacobian(), with optional derivatives.
        """
    def applyLeftJacobianInverse(self, v: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Multiplies withleftJacobianInverse(), with optional derivatives.
        """
    def applyRightJacobian(self, v: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Multiplies with rightJacobian(), with optional derivatives.
        """
    def applyRightJacobianInverse(self, v: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Multiplies with rightJacobian().inverse(), with optional derivatives.
        """
    def leftJacobian(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        ...
    def leftJacobianInverse(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        """
        For |omega|>pi uses leftJacobian().inverse(), as unstable beyond pi!
        """
    def rightJacobian(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        ...
    def rightJacobianInverse(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        """
        Inverse of right Jacobian For |omega|>pi uses rightJacobian().inverse(), as unstable beyond pi!
        """
    @property
    def C(self) -> float:
        ...
    @property
    def D(self) -> float:
        ...
    @property
    def omega(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]:
        ...
class ExpmapFunctor:
    A: float
    B: float
    @typing.overload
    def __init__(self, omega: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def __init__(self, nearZeroThresholdSq: float, axis: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
        ...
    @typing.overload
    def __init__(self, axis: numpy.ndarray[tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]], angle: float) -> None:
        ...
    def expmap(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        """
        Rodrigues formula.
        """
    @property
    def W(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        ...
    @property
    def WW(self) -> numpy.ndarray[tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]]:
        ...
    @property
    def nearZero(self) -> bool:
        ...
    @property
    def theta(self) -> float:
        ...
    @property
    def theta2(self) -> float:
        ...
