"""# Blank plot component"""

import plotly.graph_objs as go

from ragraph.plot.generic import Component, Style


class Blank(Component):
    """Blank plot component.

    Arguments:
        style: Plot style mapping.
    """

    def __init__(self, style: Style = Style()):
        trace = go.Scatter(
            x=[0.5 * style.xstep],
            y=[0.5 * style.ystep],
            mode="markers",
            marker=dict(
                line=dict(
                    color="#FFFFFF",
                ),
                color="#FFFFFF",
            ),
            showlegend=False,
            hoverinfo="skip",
        )

        xaxis = go.layout.XAxis(
            automargin=False,
            autorange=False,
            scaleanchor="y",
            scaleratio=1.0,
            range=(0, 1),
            showticklabels=False,
        )
        yaxis = go.layout.YAxis(
            automargin=False,
            autorange=False,
            showticklabels=False,
            range=(0, 1),
        )

        super().__init__(
            width=style.xstep * style.boxsize,
            height=style.ystep * style.boxsize,
            traces=[trace],
            xaxis=xaxis,
            yaxis=yaxis,
        )
