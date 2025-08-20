"""# Modular architecture example

Graph describing a design problem using objects that need to be designed based on certain aspects.
It is part of a set of three design problem graphs, each ideally solved with a different approach --
being a **modular**, integral or mixed architecture.

This particular graph describes a design problem which is ideally solved using a **modular object
architecture**. That means that the objects are best put into modules. Modules on different aspect
domains can then be mixed and matched so achieve a solution for it's combined members. Each module
should be designed based on all aspects that the objects members posess combined, while taking into
account the shared dependencies with other domains. A module's design solution should be applicable
to every member.

Nodes are of kind "object" or "aspect_1", "aspect_2", and "aspect_3". The numbers represent
different aspect domains. An "incidence" kind edge from an object to an aspect means that it
posesses that aspect.

Authors:
    Tim Wilschut and Tiemen Schuijbroek, October 2019.
"""
