# Datasets

RaGraph has several [`Graph`][ragraph.graph.Graph] ready to use datasets built-in. These datasets
serve as an excellent starting point when designing and testing your analysis scripts. The basic
method of retrieval of the [`ragraph.datasets` module][ragraph.datasets] are discussed, which
includes ways to obtain more background information on each of them.

## What's available?

Let's start off by importing the datasets module and listing what's available.

```python
from ragraph import datasets

names = datasets.enum()
assert names == [
    "aircraft_engine",
    "architecture_integral",
    "architecture_mix",
    "architecture_modular",
    "climate_control",
    "climate_control_mg",
    "compatibility",
    "design",
    "elevator175",
    "elevator45",
    "ford_hood",
    "kodak3d",
    "ledsip",
    "localbus",
    "mww_lock_aspect",
    "mww_lock_eefde",
    "mww_lock_hansweert",
    "mww_lock_sambeek",
    "mww_lock_sluis15",
    "mww_lock_volkerak",
    "overlap",
    "pathfinder",
    "shaja8",
    "similarity",
    "tarjans8",
    "tss_electric",
    "tss_front",
    "tss_hydraulic",
    "ucav",
]
```

So that's a merry band of different datasets, with names that might leave you wondering. Luckily,
all datasets come with some info for you. That info is retrievable from the
[`ragraph.datasets`][ragraph.datasets] sub-module descriptions, as well as by calling the
[`ragraph.datasets.info` method][ragraph.datasets.info]:

```python
from ragraph import datasets

print(datasets.info("aircraft_engine"))
"""
# Pratt & Whitney Aircraft Engine

A directed graph describing the Pratt & Whitney PW4098 commercial high bypass-ratio turbofan engine.
The graph describes a combination of the actual hardware dependencies of the engine and those of the
development teams involved with them. It is a weighted and directed graph featuring 60 elements,
four of which are sometimes left out as they represent the integration teams and no individual
hardware components. Weak and strong dependencies are distinguished using weights of 1 and 2,
respectively.

Reference:
    Rowles, C. M. (1999). System integration analysis of a large commercial aircraft engine.
"""
```

## Getting a dataset

Getting a [`Graph`][ragraph.graph.Graph] from the datasets is as easy as calling the
[`ragraph.datasets.get` method][ragraph.datasets.get]:

```python
from ragraph import datasets

g = datasets.get("climate_control")
print(g.get_ascii_art())
"""
                      ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
              Radiator┥ ■ │ X │   │   │ X │   │   │   │   │   │   │   │   │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
            Engine Fan┥ X │ ■ │   │   │ X │   │   │   │   │   │   │   │ X │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
           Heater Core┥   │   │ ■ │ X │   │   │ X │ X │   │   │   │   │   │   │   │ X │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
          Heater Hoses┥   │   │ X │ ■ │   │   │   │   │ X │   │   │   │   │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
             Condenser┥ X │ X │   │   │ ■ │ X │   │ X │   │   │   │   │   │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
            Compressor┥   │   │   │   │ X │ ■ │   │ X │ X │ X │ X │   │ X │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
       Evaporator Case┥   │   │ X │   │   │   │ ■ │ X │   │   │   │   │   │ X │ X │ X │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
       Evaporator Core┥   │   │ X │   │ X │ X │ X │ ■ │ X │   │   │   │   │   │   │ X │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
           Accumulator┥   │   │   │ X │   │ X │   │ X │ ■ │ X │   │   │   │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Refrigeration Controls┥   │   │   │   │   │ X │   │   │ X │ ■ │ X │   │ X │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
          Air Controls┥   │   │   │   │   │ X │   │   │   │ X │ ■ │ X │ X │ X │ X │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
               Sensors┥   │   │   │   │   │   │   │   │   │   │ X │ ■ │ X │   │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
  Command Distribution┥   │ X │   │   │   │ X │   │   │   │ X │ X │ X │ ■ │ X │ X │ X │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
             Actuators┥   │   │   │   │   │   │ X │   │   │   │ X │   │ X │ ■ │   │   │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
     Blower Controller┥   │   │   │   │   │   │ X │   │   │   │ X │   │ X │   │ ■ │ X │
                      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
          Blower Motor┥   │   │ X │   │   │   │ X │ X │   │   │   │   │ X │   │ X │ ■ │
                      └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
"""
```
