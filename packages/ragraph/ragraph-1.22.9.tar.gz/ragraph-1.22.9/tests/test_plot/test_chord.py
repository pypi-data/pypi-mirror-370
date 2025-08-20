from ragraph import datasets
from ragraph.plot import chord


def test_chord(tmpdir, datadir, check_diff):
    g = datasets.get("climate_control")
    fig = chord(g)

    fname = "cc_chord.svg"
    tmp = tmpdir / fname
    fig.save_svg(tmp)
    check_diff(tmp, datadir / "svg" / fname)
