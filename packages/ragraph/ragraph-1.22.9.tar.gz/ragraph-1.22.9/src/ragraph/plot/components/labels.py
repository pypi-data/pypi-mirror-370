"""# Labels list plot component"""

from copy import deepcopy
from typing import List

from ragraph.node import Node
from ragraph.plot.generic import Component, Style


class Labels(Component):
    """Labels list plot component.

    Arguments:
        leafs: List of leaf nodes.
        style: Plot style mapping.
    """

    def __init__(self, leafs: List[Node], style: Style = Style()):
        labels = [node.name for node in leafs]
        if style.labels.shorten is True:
            short_labels = [label.split(".")[-1] for label in labels]
        elif style.labels.shorten:
            short_labels = [style.labels.shorten(label) for label in labels]
        else:
            short_labels = labels

        label_length = max([len(label) for label in short_labels], default=0)
        fontsize = (
            int(0.6 * style.boxsize) if style.labels.fontsize is None else style.labels.fontsize
        )

        if style.labels.textorientation == "vertical":
            height = (
                label_length * fontsize * style.labels.fontaspectratio + 0.3 * style.boxsize
            )  # Text width plus 0.3 boxsize as margin.

            num = len(leafs)
            xmax = num * style.xstep
            width = xmax * style.boxsize

            xdata = [(i + 0.5) * style.xstep for i in range(num)]
            ydata = num * [-0.5 * height / style.boxsize]

            annotations = [
                dict(
                    x=x,
                    y=y,
                    text=text,
                    showarrow=False,
                    yshift=0,
                    textangle=-90,
                    yanchor="bottom",
                    font=dict(
                        color=style.labels.fontcolor,
                        family=style.labels.fontfamily,
                        size=fontsize,
                    ),
                )
                for x, y, text in zip(xdata, ydata, short_labels)
            ]

            xaxis, yaxis = deepcopy(style.labels.xaxis), deepcopy(style.labels.yaxis)
            xaxis.update(range=[0, num])
            yaxis.update(
                range=[-0.5 * height / style.boxsize, 0.5 * height / style.boxsize],
                scaleanchor="x",
                scaleratio=1.0,
            )
        else:
            # Default option.
            width = (
                label_length * fontsize * style.labels.fontaspectratio + 0.5 * style.boxsize
            )  # Text width plus 0.3 boxsize as margin.

            num = len(leafs)
            ymax = num * style.ystep
            height = ymax * style.boxsize

            xdata = num * [0.5 * width / style.boxsize]
            ydata = [ymax - (i + 0.5) * style.ystep for i in range(num)]

            annotations = [
                dict(
                    x=x,
                    y=y,
                    text=text,
                    showarrow=False,
                    yshift=0,
                    textangle=0,
                    xanchor="right",
                    font=dict(
                        color=style.labels.fontcolor,
                        family=style.labels.fontfamily,
                        size=fontsize,
                    ),
                )
                for x, y, text in zip(xdata, ydata, short_labels)
            ]

            xaxis, yaxis = deepcopy(style.labels.xaxis), deepcopy(style.labels.yaxis)
            xaxis.update(
                range=[-0.5 * width / style.boxsize, 0.5 * width / style.boxsize],
                scaleanchor="y",
                scaleratio=1.0,
            )
            yaxis.update(range=[0, num])

        super().__init__(
            width=width,
            height=height,
            traces=[],
            annotations=annotations,
            shapes=None,
            xaxis=xaxis,
            yaxis=yaxis,
        )
