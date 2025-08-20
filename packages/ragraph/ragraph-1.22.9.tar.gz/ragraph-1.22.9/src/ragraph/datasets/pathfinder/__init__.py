"""# NASA Mars Pathfinder Technology Risk DSM

The technology risk DSM (TR-DSM) helps to identify where most of the design effort
should go if one wants to mitigate technological failures and improve robustness of a
system. All components of a system are assigned with a technology risk factor,
which indicates the probability of failure, unprovenness, or uncertainty in design.
The technology risk factor at NASA is loosely defined as the inverse of the technology
readiness level:

| TRF | NASA Technology Readiness Level Definition                                           | TRL |
|-----|--------------------------------------------------------------------------------------|-----|
|  1  | Actual system "flight proven" through successful mission operations                  |  9  |
|  2  | Actual system completed and "flight qualified" through test and demonstration        |  8  |
|  2  | System prototype in a space environment                                              |  7  |
|  3  | System/subsystem model or prototype demonstration in a relevant environment          |  6  |
|  4  | Component and/or breadboard validation in relevant environment                       |  5  |
|  4  | Component and/or breadboard validation in laboratory environment                     |  4  |
|  5  | Analytical and experimental critical function and/or characteristic proof-of-concept |  3  |
|  5  | Technology concept and/or application formulated                                     |  2  |
|  5  | Basic principles observed and reported                                               |  1  |


The dataset includes both an adjacency value as if the DSM were a regular product DSM
with interface strength values and the technology risk value which is computed using:

    TR = TRF-source * TRF-target * adjacency

Reference:
    Brady, Timothy K. 2002. Utilization of Dependency Structure Matrix Analysis to
    Assess Complex Project Designs. Proceedings of ASME Design Engineering Technical
    Conferences, no. DETCZ002/DTM-34031, Montreal, Canada.
"""

node_weights = ["technology risk factor"]
edge_weights = ["adjacency", "technology risk"]
