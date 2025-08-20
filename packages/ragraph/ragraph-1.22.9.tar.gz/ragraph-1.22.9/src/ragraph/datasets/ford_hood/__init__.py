"""Ford Motor Company Hood Development Process.

This DSM application was made to test the effectiveness of a DSM analysis to improve a highly
developed iterative design process in terms of:

- Reduction of product development lead time
- Reduction of product development lead-time variation

As it is a process DSM, the nodes represent tasks in the design process. The edges represent
dependencies between them. Each task in the design process was assigned a task volatility value,
which is an indication of the probability of rework.

Node (task) weights:

- EC(i) and EC(r) represent the initial and rework costs
- ED(i) and ED(r) represent the initial and rework durations
- Information variability (likelihood of input changing)


Edge weights:

- volatility: an indication of the probability of rework when the dependent task is executed without
  properly waiting for its input to finish. It's value was determined using the information
  variability of the source (depended on) task and the sensitivity of the target (dependent) task.

Reference:
    Browning, Tyson R., and Steven D. Eppinger. 2002, November. Modeling Impacts of Process
    Architecture on Cost and Schedule Risk in Product Development. IEEE Transactions on Engineering
    Management 49 (4):428-442.

Reference:
    Krishnan, Viswanathan, Steven D. Eppinger, and Daniel E. Whitney. 1997, April. A Model-Based
    Framework to Overlap Product Development Activities. Management Science 43 (4):437-451.

Reference:
    Yassine, Ali A., Daniel E. Whitney, and Tony P. Zambito. 2001. Assessment of Rework
    Probabilities for Simulating Product Development Processes Using the Design Structure Matrix
    (DSM). ASME Design Engineering Technical Conferences, DTM-21693.
"""

node_weights = [
    "EC(i) ($000)",
    "EC(r) ($000)",
    "ED(i) (days)",
    "ED(r) (% of ED (i))",
    "information variability",
]
edge_weights = ["volatility"]
