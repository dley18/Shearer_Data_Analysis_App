"""Module for managing a Bokeh plot."""

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import numpy as np

from config.chart_config import LINE_WIDTH, ASTERICK_SIZE


class PlotPoint:
    """Manages operations for a Bokeh plot."""

    def __init__(
        self,
        name: str,
        figure: figure,
        x_values: np.array,
        y_values: np.array,
        color: str,
    ):
        self.name = name
        self.figure = figure
        self.x_values = x_values
        self.y_values = y_values
        self.color = color

        self.source = ColumnDataSource(data={"x": x_values, "y": y_values})

        self.line = None
        self.asterick = None

        self.plot()

    def plot(self):
        """Plot a point on the figure."""
        self.line = self.figure.line(
            "x",
            "y",
            source=self.source,
            legend_label=self.name,
            color=self.color,
            line_width=LINE_WIDTH,
            name=self.name,
        )

        self.asterick = self.figure.scatter(
            "x",
            "y",
            source=self.source,
            legend_label=self.name,
            color=self.color,
            marker="asterisk",
            size=ASTERICK_SIZE,
            visible=False,
        )

    def get_line(self):
        """Get the line plotted."""
        return self.line

    def get_asterick(self):
        """Get the astericks plotted."""
        return self.asterick
