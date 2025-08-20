"""# Integral architecture example

Graph describing a design problem using objects that need to be designed based on
certain aspects. It is part of a set of three design problem graphs, each ideally solved
with a different approach -- being a modular, **integral** or mixed architecture.

This particular graph describes a design problem which is ideally solved using a
**integral object architecture**. That the architecture consists vertically integrated
modules. That is, each module in one domain integrates with only one (or very few) in
the next and there is no crossover (mixing and matching across domains like with a
modular approach). This means that interfaces between modules in different domains are
relatively few. A module's design solution should be applicable to every member.

Nodes are of kind "object" or "aspect_1", "aspect_2", and "aspect_3". The numbers
represent different aspect domains. An "incidence" kind edge from an object to an aspect
means that it possesses that aspect.

Authors:
    Tim Wilschut and Tiemen Schuijbroek, October 2019.
"""
