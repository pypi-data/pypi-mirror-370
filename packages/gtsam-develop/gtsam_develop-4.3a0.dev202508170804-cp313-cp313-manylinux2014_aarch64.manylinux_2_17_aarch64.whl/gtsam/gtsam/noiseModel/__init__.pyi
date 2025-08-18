"""
noiseModel submodule
"""
from __future__ import annotations
import numpy
import typing
from . import mEstimator
__all__: list[str] = ['Base', 'Constrained', 'Diagonal', 'Gaussian', 'Isotropic', 'Robust', 'Unit', 'mEstimator']
class Base:
    def __repr__(self, s: str = '') -> str:
        ...
    def print(self, s: str = '') -> None:
        ...
class Constrained(Diagonal):
    @staticmethod
    @typing.overload
    def All(dim: int) -> Constrained:
        """
        Fully constrained variations.
        """
    @staticmethod
    @typing.overload
    def All(dim: int, mu: float) -> Constrained:
        """
        Fully constrained variations.
        """
    @staticmethod
    @typing.overload
    def MixedPrecisions(mu: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], precisions: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        """
        A diagonal noise model created by specifying a Vector of precisions, some of which might be inf.
        """
    @staticmethod
    @typing.overload
    def MixedPrecisions(precisions: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        ...
    @staticmethod
    @typing.overload
    def MixedSigmas(mu: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], sigmas: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        """
        A diagonal noise model created by specifying a Vector of standard devations, some of which might be zero.
        """
    @staticmethod
    @typing.overload
    def MixedSigmas(m: float, sigmas: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        """
        A diagonal noise model created by specifying a Vector of standard devations, some of which might be zero.
        """
    @staticmethod
    @typing.overload
    def MixedVariances(mu: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], variances: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        """
        A diagonal noise model created by specifying a Vector of standard devations, some of which might be zero.
        """
    @staticmethod
    @typing.overload
    def MixedVariances(variances: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> Constrained:
        ...
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def deserialize(self, serialized: str) -> None:
        ...
    def serialize(self) -> str:
        ...
    def unit(self) -> Constrained:
        """
        Returns aUnitversion of a constrained noisemodel in which constrained sigmas remain constrained and the rest are unit scaled.
        """
class Diagonal(Gaussian):
    @staticmethod
    def Precisions(precisions: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], smart: bool = True) -> Diagonal:
        """
        A diagonal noise model created by specifying a Vector of precisions, i.e.
        
        i.e. the diagonal of the information matrix, i.e., weights
        """
    @staticmethod
    def Sigmas(sigmas: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], smart: bool = True) -> Diagonal:
        """
        A diagonal noise model created by specifying a Vector of sigmas, i.e.
        
        standard deviations, the diagonal of the square root covariance matrix.
        """
    @staticmethod
    def Variances(variances: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]], smart: bool = True) -> Diagonal:
        """
        A diagonal noise model created by specifying a Vector of variances, i.e.
        
        Args:
        variances: A vector containing the variances of this noise model
        smart: check if can be simplified to derived class
        """
    def R(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        """
        Return R itself, but note that Whiten(H) is cheaper than R*H.
        """
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def deserialize(self, serialized: str) -> None:
        ...
    def invsigmas(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Return sqrt precisions.
        """
    def precisions(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Return precisions.
        """
    def serialize(self) -> str:
        ...
    def sigmas(self) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Calculate standard deviations.
        """
class Gaussian(Base):
    @staticmethod
    def Covariance(R: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], smart: bool = True) -> Gaussian:
        ...
    @staticmethod
    def Information(R: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], smart: bool = True) -> Gaussian:
        ...
    @staticmethod
    def SqrtInformation(R: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]], smart: bool = True) -> Gaussian:
        """
        AGaussiannoise model created by specifying a square root information matrix.
        
        Args:
        R: The (upper-triangular) square root information matrix
        smart: check if can be simplified to derived class
        """
    def R(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        """
        Return R itself, but note that Whiten(H) is cheaper than R*H.
        """
    def Whiten(self, H: numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        """
        Multiply a derivative with R (derivative of whiten) Equivalent to whitening each column of the input matrix.
        """
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def covariance(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        """
        Compute covariance matrix.
        """
    def deserialize(self, serialized: str) -> None:
        ...
    def equals(self, expected: Base, tol: float) -> bool:
        ...
    def information(self) -> numpy.ndarray[tuple[M, N], numpy.dtype[numpy.float64]]:
        """
        Compute information matrix.
        """
    def negLogConstant(self) -> float:
        """
        Compute the negative log of the normalization constant for aGaussiannoise model k = 1/(|2πΣ|).
        
        Returns: double
        """
    def serialize(self) -> str:
        ...
    def unwhiten(self, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Unwhiten an error vector.
        """
    def whiten(self, v: numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]) -> numpy.ndarray[tuple[M, typing.Literal[1]], numpy.dtype[numpy.float64]]:
        """
        Whiten an error vector.
        """
class Isotropic(Diagonal):
    @staticmethod
    def Precision(dim: int, precision: float, smart: bool = True) -> Isotropic:
        """
        An isotropic noise model created by specifying a precision.
        """
    @staticmethod
    def Sigma(dim: int, sigma: float, smart: bool = True) -> Isotropic:
        """
        An isotropic noise model created by specifying a standard devation sigma.
        """
    @staticmethod
    def Variance(dim: int, varianace: float, smart: bool = True) -> Isotropic:
        ...
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def deserialize(self, serialized: str) -> None:
        ...
    def serialize(self) -> str:
        ...
    def sigma(self) -> float:
        """
        Return standard deviation.
        """
class Robust(Base):
    @staticmethod
    def Create(robust: mEstimator.Base, noise: Base) -> Robust:
        ...
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, robust: mEstimator.Base, noise: Base) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def deserialize(self, serialized: str) -> None:
        ...
    def serialize(self) -> str:
        ...
class Unit(Isotropic):
    @staticmethod
    def Create(dim: int) -> Unit:
        """
        Create a unit covariance noise model.
        """
    def __getstate__(self) -> tuple:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def deserialize(self, serialized: str) -> None:
        ...
    def serialize(self) -> str:
        ...
