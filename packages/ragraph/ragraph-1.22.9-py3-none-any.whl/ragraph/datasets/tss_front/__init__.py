"""Truck Steering System (TSS) [Front]

The TSS is the subject of the industry workshop of the DSM Conference of 2023. It represents the
steering system and related assemblies of a truck. Multiple datasets have been given that describe
both technological solutions to the steering problem (product DSMs), as well as technology risk
factors, process dependencies and organizational mappings.

The available datasets are:

- `tss_front`: Product DSM for the "front axle only" solution with "risk" weights, as well as a
  process and organizational mapping.
- `tss_electric`: Product DSM for the "electric" solution with "risk" weights.
- `tss_hydraulic`: Product DSM for the "hydraulic" solution with "risk" weights.

The associated "risk" weights have been copied/assumed from the "front axle only" example.

The truck's intended operating area is Sweden, which imposes harsh (cold) conditions. The following
risks have been identified:

- Sudden loss of tire pressure can result in reduced steering control, potentially leading to a loss
  of vehicle control. This can strain other steering system components, such as the hub, steering
  knuckle, and tie rod.
- Bearing failure can cause excessive friction and heat generation, affecting the hub's structural
  integrity. This can lead to further damage to the wheel, steering knuckle, and tie rod.
- Cracking of the steering knuckle can weaken the axle assembly and may lead to a loss of steering
  control. It can also damage the hub and tie rod.
- Bending of the knuckle arm can disrupt the steering geometry, affecting the steering system's
  overall performance. It can also cause excessive wear on the steering knuckle and tie rod.
- Cracks in the frame can weaken the structural integrity of the entire front axle assembly,
  potentially leading to catastrophic failure. It can adversely affect all connected components and
  overall vehicle stability.
- Fluid leaks can result in reduced hydraulic pressure, causing a loss of steering power and
  control. It may also affect the servo valve and hydraulic pump.
- Bending or breaking of the tie rod can lead to loss of steering control, affecting wheel alignment
  and potentially causing damage to the steering knuckle and other components.
- A malfunctioning angle sensor can lead to inaccurate steering data, potentially causing the ECU to
  make incorrect steering adjustments, impacting steering performance.
- Valve issues can lead to erratic or delayed steering response, affecting overall steering system
  performance and potentially causing strain on the steering pump and hydraulic oil reservoir.
- Cold start problems can affect the engine's ability to provide power for the hydraulic pump,
  reducing hydraulic pressure and steering assistance.
- Speedometer malfunction doesn't directly impact steering but can affect the driver's ability to
  monitor vehicle speed, potentially leading to unsafe driving conditions. ECU malfunction can lead
  to incorrect steering commands, impacting steering performance and potentially straining other
  hydraulic system components.
- Thickening or freezing of hydraulic oil can reduce the effectiveness of the hydraulic system,
  potentially leading to reduced steering control and increased strain on the hydraulic pump.
- Pump malfunction can lead to reduced hydraulic pressure, affecting steering performance and
  potentially straining other hydraulic components.
- A clogged filter can reduce hydraulic flow, potentially leading to reduced steering power and
  increased load on the hydraulic pump and other components.
- A malfunctioning cooler can result in overheating of the hydraulic fluid, potentially reducing
  system efficiency and impacting other hydraulic components' performance.
"""

edge_weights = [
    "default",
    "labor_cost",
    "max_duration",
    "min_duration",
    "most_likely_duration",
    "risk",
]
