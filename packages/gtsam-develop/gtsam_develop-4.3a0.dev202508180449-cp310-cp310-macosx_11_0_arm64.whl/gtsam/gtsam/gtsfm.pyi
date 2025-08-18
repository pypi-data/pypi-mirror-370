"""
gtsfm submodule
"""
from __future__ import annotations
import gtsam.gtsam
import numpy
import typing
__all__: list[str] = ['Keypoints', 'tracksFromPairwiseMatches']
M = typing.TypeVar("M", bound=int)
N = typing.TypeVar("N", bound=int)
class Keypoints:
    coordinates: numpy.ndarray[tuple[M, typing.Literal[2]], numpy.dtype[numpy.float64]]
    def __init__(self, coordinates: numpy.ndarray[tuple[M, typing.Literal[2]], numpy.dtype[numpy.float64]]) -> None:
        ...
def tracksFromPairwiseMatches(matches_dict: dict[gtsam.gtsam.IndexPair, numpy.ndarray[tuple[M, typing.Literal[2]], numpy.dtype[numpy.int32]]], keypoints_list: list[Keypoints], verbose: bool = False) -> list[gtsam.gtsam.SfmTrack2d]:
    ...
