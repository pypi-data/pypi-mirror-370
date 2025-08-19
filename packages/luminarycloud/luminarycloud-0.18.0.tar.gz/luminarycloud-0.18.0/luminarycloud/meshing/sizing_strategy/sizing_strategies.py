from dataclasses import dataclass

from luminarycloud._helpers.warnings.deprecated import deprecated
from ...pipeline_util.dictable import PipelineDictable


@dataclass
class SizingStrategy(PipelineDictable):
    """Sizing strategy parameters."""

    pass


@deprecated(
    "Use luminarycloud.meshing.sizing_strategy.Minimal instead.",
    "0.10.2",
)
@dataclass
class MinimalCount(SizingStrategy):
    """
    Minimal sizing strategy parameters.

    If this is used, all other meshing parameters are ignored.

    .. deprecated:: 0.10.2
        Use [`Minimal()`](#luminarycloud.meshing.sizing_strategy.Minimal) instead.
    """

    pass


@dataclass
class Minimal(SizingStrategy):
    """
    Minimal sizing strategy parameters.

    If this is used, all other meshing parameters are ignored.
    """

    pass


@dataclass
class TargetCount(SizingStrategy):
    """
    Sizing strategy based on a target number of cells.

    To reach a target number of cells, the edge length specifications will be proportionally scaled
    throughout the mesh. Requested boundary layer profiles will be maintained.
    """

    target_count: int = 10000000
    "The target number of cells in the mesh"


@dataclass
class MaxCount(SizingStrategy):
    """
    Sizing strategy based on a maximum number of cells.

    If the mesh becomes larger than the max cell count, the mesh will be scaled.
    Requested boundary layer profiles will be maintained.
    """

    max_count: int = 10000000
    "The maximum number of cells in the mesh"
