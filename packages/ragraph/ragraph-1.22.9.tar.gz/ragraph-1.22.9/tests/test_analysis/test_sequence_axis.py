from ragraph import datasets
from ragraph.analysis import sequence


def test_axis_sequencing_climate_control_mg():
    g = datasets.get("climate_control_mg")

    g, seq = sequence.axis(g, nodes=g.leafs, names=True)

    assert seq == [
        "Compressor",
        "Air Controls",
        "Command Distribution",
        "Evaporator Case",
        "Evaporator Core",
        "Blower Motor",
        "Engine Fan",
        "Radiator",
        "Condenser",
        "Heater Core",
        "Heater Hoses",
        "Accumulator",
        "Refrigeration Controls",
        "Actuators",
        "Blower Controller",
        "Sensors",
    ]
