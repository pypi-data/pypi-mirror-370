from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.domain import compute_multidomain, expand_domain
from replan2eplus.subsurfaces.utils import filter_subsurfaces
from replan2eplus.visuals.calcs import (
    domain_to_line,
    domain_to_mpl_patch,
    subsurface_connection,
)


expansion_factor = 1.3
# line
edge_color = "black"
alpha = 0.2

# annotations
annotation_font_size = "x-small"
alignment = {
    "horizontalalignment": "center",
    "verticalalignment": "center",
}

# sufaces: list[Surface]
# subsurface: list[Subsurface]


@dataclass
class BasePlot:
    zones: list[Zone]
    axes: Axes = plt.subplot()
    cardinal_expansion_factor: float = expansion_factor
    extents_expansion_factor: float = expansion_factor

    def __post_init__(self):
        if not self.axes:
            self.axes = plt.subplot()
        self.total_domain = compute_multidomain([i.domain for i in self.zones])

        self.cardinal_domain = expand_domain(
            self.total_domain, self.cardinal_expansion_factor
        )
        self.extents = expand_domain(
            self.cardinal_domain, self.extents_expansion_factor
        )

    def plot_zones(self, edge_color=edge_color, alpha=alpha):
        patches = [domain_to_mpl_patch(i.domain) for i in self.zones]
        for p in patches:
            p.set(color=edge_color, alpha=alpha)
            self.axes.add_artist(p)
        return self

    def plot_zone_names(
        self,
        fontsize=annotation_font_size,
    ):
        for zone in self.zones:
            self.axes.text(
                *zone.domain.centroid,
                s=f"{zone.room_name}",
                fontsize=fontsize,
                **alignment,
            )
        return self

    def plot_cardinal(
        self,
        fontsize=annotation_font_size,
    ):
        for key, value in self.cardinal_domain.cardinal.dict_.items():
            self.axes.text(*value, s=key, fontsize=fontsize, **alignment)
        return self

    def plot_surfaces(self, surfaces: list[Surface], fontsize=annotation_font_size):
        for surface in surfaces:
            line = domain_to_line(surface.domain)
            self.axes.add_artist(line.to_line2D)
            self.axes.text(
                *line.centroid,
                s=surface.display_name,
                fontsize=fontsize,
            )  # type: ignore
        return self

    def plot_subsurfaces(
        self, subsurfaces: list[Subsurface], fontsize=annotation_font_size
    ):
        ss = filter_subsurfaces(subsurfaces)
        for subsurf in ss:
            line = domain_to_line(subsurf.domain)
            self.axes.add_artist(line.to_line2D)
            self.axes.text(
                *line.centroid,
                s=subsurf.display_name,
                **line.alignment,
                fontsize=fontsize,
            )  # type: ignore
            # TODO add legend
        return self

    def plot_connections(self, subsurfaces: list[Subsurface]):
        for ss in subsurfaces:
            line = subsurface_connection(ss, self.zones, self.cardinal_domain.cardinal)
            self.axes.add_artist(line)

        return self

    def show(self):
        assert self.extents, (
            "Extents has not been initialized!"
        )  # TODO: handle this better..
        self.axes.set_xlim(self.extents.horz_range.as_tuple)
        self.axes.set_ylim(self.extents.vert_range.as_tuple)

        plt.show()
