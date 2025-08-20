"""# UCAV (unmanned combat aerial vehicle) preliminary design process.

The graph contains 14 preliminary design activities. Each phase consists of an initial
activity to define design several disciplines-such as aerodynamics, propulsion,
stability and control (S&C), distribute a design configuration (a design concept
proposed to satisfy the DR&O). Then, requirements and objectives (DR&O), followed by a
couple of activities to create and mechanical and electrical, weights, and performance -
each evaluate the configuration from their own perspective.

The nodes contain a minimum, mean and max weight for both duration and cost, as well as
an improvement curve value. The improvement curve determines the savings in work for
each successive iteration of an activity. The edges contain a binary weight and rework
probability and rework impact annotations.

When an activity is performed before all activities with edges to that activity has been
succesfully executed, there is a rework probability that the activity needs to be
redone, the impact then indicates the percentage that needs to be redone and the
improvement curve decreases this in successive iterations.

Reference:
    Eppinger, S. D., & Browning, T. R. (2012). Design Structure Matrix - Methods and Applications.
"""

node_weights = [
    "min_duration",
    "mean_duration",
    "max_duration",
    "min_cost",
    "mean_cost",
    "max_cost",
    "improvement_curve",
]
edge_weights = ["binary", "probability", "impact"]
