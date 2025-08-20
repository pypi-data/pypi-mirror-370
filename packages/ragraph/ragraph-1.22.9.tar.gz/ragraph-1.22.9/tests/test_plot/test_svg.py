"""Tests for the SVG class."""

from ragraph.plot import svg


def test_line():
    line = svg.Line()

    assert line.width == 2


def test_svg():
    s = svg.SVG()
    assert s.as_dict() == dict()


def test_gets():
    assert svg.get_line(x0=0.0, x1=1.0, y0=2.0, y1=3.0).as_dict() == dict(
        type="line", x0=0.0, x1=1.0, y0=2.0, y1=3.0
    )

    assert svg.get_curvedline(x0=0.0, x1=1.0, x2=2.0, y0=3.0, y1=4.0, y2=5.0).as_dict() == dict(
        type="path", path="M 0.0 3.0 Q 1.0 4.0 2.0 5.0"
    )

    assert svg.get_rectangle(x0=0.0, x1=1.0, y0=2.0, y1=3.0).as_dict() == dict(
        type="rect", x0=0.0, x1=1.0, y0=2.0, y1=3.0
    )

    assert svg.get_wedge(
        x=-1.0, y=0.0, r=1.0, start_angle=0.0, end_angle=svg.pi / 3
    ).as_dict() == dict(
        type="path",
        path="M -1.0 0.0 L 0.0 0.0 Q 0.0 0.414 -0.293 0.707 Q -0.386 0.8 -0.5 0.866 Z",
    )
