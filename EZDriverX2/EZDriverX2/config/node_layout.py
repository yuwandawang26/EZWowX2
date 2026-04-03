"""Node layout configuration.

Defines the grid layout for pixel node extraction from the game UI.
"""

from dataclasses import dataclass, field
from typing import Final


GRID_WIDTH: Final[int] = 8
GRID_HEIGHT: Final[int] = 8


@dataclass(frozen=True, slots=True)
class RegionSlice:
    """Defines a rectangular slice of the pixel grid.

    All coordinates are in pixel units (1 unit = 1 pixel).
    """
    slice_x: tuple[int, int]
    slice_y: tuple[int, int]

    def __post_init__(self) -> None:
        if self.slice_x[0] >= self.slice_x[1]:
            raise ValueError(f"slice_x must be (min, max) with min < max, got {self.slice_x}")
        if self.slice_y[0] >= self.slice_y[1]:
            raise ValueError(f"slice_y must be (min, max) with min < max, got {self.slice_y}")
        if self.slice_x[0] < 0 or self.slice_y[0] < 0:
            raise ValueError(f"Slice coordinates must be non-negative, got x={self.slice_x}, y={self.slice_y}")

    @property
    def width(self) -> int:
        return self.slice_x[1] - self.slice_x[0]

    @property
    def height(self) -> int:
        return self.slice_y[1] - self.slice_y[0]

    @property
    def x_start(self) -> int:
        return self.slice_x[0]

    @property
    def x_end(self) -> int:
        return self.slice_x[1]

    @property
    def y_start(self) -> int:
        return self.slice_y[0]

    @property
    def y_end(self) -> int:
        return self.slice_y[1]


@dataclass(frozen=True)
class NodeRegion:
    """Defines a named region in the pixel grid.

    A region is a rectangular area identified by a name.
    """
    name: str
    slice: RegionSlice
    required: bool = True


@dataclass(frozen=True)
class NodeLayout:
    """Complete node layout configuration.

    Defines all regions for a specific game UI configuration.
    """
    regions: tuple[NodeRegion, ...]
    grid_width: int = GRID_WIDTH
    grid_height: int = GRID_HEIGHT

    def get_region(self, name: str) -> NodeRegion | None:
        """Get a region by name.

        Args:
            name: Region name.

        Returns:
            NodeRegion if found, None otherwise.
        """
        for region in self.regions:
            if region.name == name:
                return region
        return None

    def get_required_regions(self) -> tuple[NodeRegion, ...]:
        """Get all required regions.

        Returns:
            Tuple of required regions.
        """
        return tuple(r for r in self.regions if r.required)


DEFAULT_NODE_LAYOUT = NodeLayout(
    regions=(
        NodeRegion(
            name="player_health",
            slice=RegionSlice(slice_x=(0, 8), slice_y=(0, 8)),
            required=True,
        ),
        NodeRegion(
            name="player_power",
            slice=RegionSlice(slice_x=(8, 16), slice_y=(0, 8)),
            required=True,
        ),
        NodeRegion(
            name="target_health",
            slice=RegionSlice(slice_x=(16, 24), slice_y=(0, 8)),
            required=True,
        ),
        NodeRegion(
            name="target_power",
            slice=RegionSlice(slice_x=(24, 32), slice_y=(0, 8)),
            required=True,
        ),
        NodeRegion(
            name="focus_health",
            slice=RegionSlice(slice_x=(0, 8), slice_y=(8, 16)),
            required=False,
        ),
        NodeRegion(
            name="focus_power",
            slice=RegionSlice(slice_x=(8, 16), slice_y=(8, 16)),
            required=False,
        ),
    ),
    grid_width=GRID_WIDTH,
    grid_height=GRID_HEIGHT,
)


def validate_layout(layout: NodeLayout) -> list[str]:
    """Validate a node layout configuration.

    Args:
        layout: The layout to validate.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    if layout.grid_width <= 0 or layout.grid_height <= 0:
        errors.append(f"Grid dimensions must be positive, got {layout.grid_width}x{layout.grid_height}")

    for region in layout.regions:
        if region.slice.x_end > layout.grid_width:
            errors.append(f"Region '{region.name}' x_end={region.slice.x_end} exceeds grid_width={layout.grid_width}")
        if region.slice.y_end > layout.grid_height:
            errors.append(f"Region '{region.name}' y_end={region.slice.y_end} exceeds grid_height={layout.grid_height}")

    return errors


def load_layout_from_dict(data: dict) -> NodeLayout:
    """Load a node layout from a dictionary.

    Args:
        data: Dictionary with 'regions' and optional 'grid_width', 'grid_height'.

    Returns:
        NodeLayout instance.

    Raises:
        ValueError: If the data is invalid.
    """
    try:
        grid_width = data.get("grid_width", GRID_WIDTH)
        grid_height = data.get("grid_height", GRID_HEIGHT)

        regions = []
        for region_data in data.get("regions", []):
            regions.append(NodeRegion(
                name=region_data["name"],
                slice=RegionSlice(
                    slice_x=tuple(region_data["slice_x"]),
                    slice_y=tuple(region_data["slice_y"]),
                ),
                required=region_data.get("required", True),
            ))

        return NodeLayout(
            regions=tuple(regions),
            grid_width=grid_width,
            grid_height=grid_height,
        )
    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")


__all__ = [
    "GRID_WIDTH",
    "GRID_HEIGHT",
    "RegionSlice",
    "NodeRegion",
    "NodeLayout",
    "DEFAULT_NODE_LAYOUT",
    "validate_layout",
    "load_layout_from_dict",
]
