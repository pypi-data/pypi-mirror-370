# Changelog

## [1.22.9] - 2025-08-12

### Changed

- The [`from_grip`][ragraph.io.grip.from_grip] and [`to_grip`][ragraph.io.grip.to_grip]  functions to include meta-information attached to requirements.
- The [`from_grip`][ragraph.io.grip.from_grip] and [`to_grip`][ragraph.io.grip.to_grip]  functions to include activities.

## [1.22.8] - 2025-04-15

### Changed

- Switched the chord plot backend from `openchord` to our own `RaChord` fork of the project.
  - This solves installation and dependency management issues since the original `openchord` is not actively released to PyPI.

## [1.22.7] - 2025-02-05

### Changed

User-facing changes:

- Bumped `numpy` requirement to latest version 2.x.

Internal changes:

- Adopted a `src/` layout for the project and moved from `poetry` to `uv` as the environment manager.
- Added a `justfile` to abstract over underlying commands.
- Adopted using an OIDC for publishing in pipelines.

### Fixed

- Some broken internal references in documentation files.
- Some formatting according to the latest `ruff` and `black`.

## [1.22.6] - 2025-01-15

### Changed

- Changed the GRIP warnings to use a package [`logger`][ragraph.logger] instead of `warnings.warn`.

## [1.22.5] - 2025-01-15

### Fixed

- The [`from_grip`][ragraph.io.grip.from_grip] function no longer fails on references to
  objects that are not part of the XML.

### Changed

- The [`from_grip`][ragraph.io.grip.from_grip] now derives and attaches annotations and
  labels to [`Edges`][ragraph.graph.Edge].
- The [`to_grip`][ragraph.io.grip.to_grip] has been modified such that functions are exported
  aswell.

## [1.22.4] - 2025-01-15

### Fixed

- The [`chord`][ragraph.plot.chord] function is now imported lazily and no longer breaks all plotting
  functionality when not available.

### Changed

- Updated ratio-genetic-py to 0.4.0, adding MacOS as well as aarch64 support for all three platforms (Linux, MacOS, Windows).

## [1.22.3] - 2024-11-25

### Changed

- Fixed some code formatting that upset the pipeline checks.
- Removed some obsolete code from the GRIP I/O.

## [1.22.2] - 2024-11-25

### Changed

- Updated dependencies.

## [1.22.1] - 2024-11-06

### Changed

- Updated [`from_grip`][ragraph.io.grip.from_grip] and
  [`to_grip`][ragraph.io.grip.from_grip] following changes in GRIP. GRIP is project
  management software used by Rijkswaterstaat, the executive branch of the Dutch Ministry
  of Infrastructure and Water management.

## [1.22.0] - 2024-09-24

### Added

- Added a [`chord`][ragraph.plot.chord] plot function.
  See [the Chord plot section](./how-to-guides/plotting.md#chord-plot)
  in the Plotting how-to-guide for an example.

## [1.21.1] - 2024-05-31

### Added

- Objecttype - Systeemeis relations import in [`ragraph.io.grip`][ragraph.io.grip].

## [1.21.0] - 2024-04-29

### Added

- Added a [`Convention`][ragraph.generic.Convention] enumeration for the
  [`ragraph.io.matrix`][ragraph.io.matrix] functions and friends as well as in the `plot` module.
  - For the methods on [`Graph`][ragraph.graph.Graph] instances it's available as a `convention`
    keyword such as on [`get_adjacency_matrix`][ragraph.graph.Graph.get_adjacency_matrix].
  - You can supply the convention to
    [`ragraph.plot.Style.convention`][ragraph.plot.Style.convention].
  - Note that all analysis algorithms and metrics are left untouched and as such the matrices used
    during these analyses will still be in the original IR-FAD convention (inputs in rows, feedback
    above diagonal).
- Objecttype import in [`ragraph.io.grip`][ragraph.io.grip].

### Changed

- The default Canopy export type has been set to a `"graph"` from now on.

## [1.20.3] - 2023-11-21

### Changed

- Updated dependency constraints.

## [1.20.2] - 2023-10-02

### Fixed

- Also improve resilience of CSV imports, since CSV exports now support 'empty' weights. This makes
  for better round-tripping I/O when using CSV.

## [1.20.1] - 2023-10-02

### Added

- Truck Steering System dataset for the DSM conference 2023.

### Fixed

- Improved resilience of the CSV I/O module.

## [1.20.0] - 2023-09-19

### Added

- Graph export functionality in [`ragraph.io.grip`][ragraph.io.grip] for facilitating
  a GRIP round trip for Rijkswaterstaat.

### Fixed

- Graph import functionality for the GRIP exports from Rijkswaterstaat in
  [`ragraph.io.grip`][ragraph.io.grip] such that dependencies between functions and
  requirements are included..

## [1.19.5] - 2023-08-16

### Fixed

- Harden more plotting methods that depend on the length or index of things that might be empty.

## [1.19.4] - 2023-08-16

### Fixed

- Provided all `min()` and `max()` calls with a default value where there was an iterable as an
  argument.
- Fixed a line in XML I/O that directly compared a `type(v) == str` instead of the recommended
  `isinstance(v, str)`.

## [1.19.3] - 2023-08-15

### Fixed

- Handling an edge case where the [`Labels` plot component][ragraph.plot.components.Labels] would
  return an error if it was created with an empty list.

## [1.19.2] - 2023-07-06

### Changed

- Added an `__all__ = [...]` entry to [`ragraph.plot`][ragraph.plot] that includes
  [`Style`][ragraph.plot.Style] so that it's clearer that it can be imported there.
- Changed the default for the reference documentation generation for private module contents
  (function/classes). The [`ragraph.analysis`][ragraph.analysis] module overrides this by including
  their private methods such that tinkerers have full interactive documentation there.

## [1.19.1] - 2023-07-06

### Changed

- Switched documentation from Sphinx to MkDocs. A lot of docstrings were impacted, but code should
  still run fine with minor adjustments, if any at all. Docs should now be way better to navigate
  over at <https://ragraph.ratio-case.nl>.

## [1.19.0] - 2023-05-24

### Changed

- Changed the way one does sigma and delta MDM analysis. These are now offered in simpler,
  functional methods as opposed to the relatively heavy class approach that was taken before. We
  chose for only a minor version increment as this is a rather niche part of our public methods, of
  which a clear example is now included in the [comparison section](./how-to-guides/comparison.md).

## [1.18.0] - 2023-05-12

### Added

- Graph import functionality for the GRIP exports from Rijkswaterstaat in
  [`ragraph.io.grip`][ragraph.io.grip].

## [1.17.1] - 2023-04-05

### Fixed

- Minor tweaks and fixes for formatting.
- Added `ruff` formatting config.

## [1.17.0] - 2023-02-17

### Added

- Genetic sequencing of node sequences built on `ratio-genetic-py`. See
  [`ragraph.analysis.sequence.genetic`][ragraph.analysis.sequence.genetic] and
  `ragraph.analysis.sequence._genetic.genetic_sequencing` for more info.

## [1.16.1] - 2022-10-27

### Added

- A convenient `all` extra to install all extras at once.

## [1.16.0] - 2022-07-27

### Added

- Ways to highlight rows and/or columns in all PieMap plots. See
  [highlighting](./how-to-guides/plotting.md#information-highlighting) in the usage documentation.

## [1.15.1] - 2022-06-14

### Added

- Added an option to the
  [`ragraph.analysis.compatibility.CompatibilityAnalysis`][ragraph.analysis.compatibility.CompatibilityAnalysis]
  `interface_compatibility`that toggles whether interface checking should be a prerequisite for
  checking compatibility. The default is the current behavior (`True`), where compatibility is only
  checked for direct variant interfaces. Any two variants without a direct interface is then assumed
  to be compatible. Toggling that to `False` implies that any two variants should be compatible,
  regardless of the existence of an interface.

## [1.15.0] - 2022-06-08

### Added

- New plot method to
  [`ragraph.analysis.compatibility.CompatibilityAnalysis.plot`][ragraph.analysis.compatibility.CompatibilityAnalysis.plot].
- [`ragraph.plot.generic.LabelsStyle`][ragraph.plot.generic.LabelsStyle] can now toggle the label
  shortening behavior with a `shorten` key that is `True` by default. This is the current behavior
  where each label is shortened by only keeping everything after the last period. You can provide a
  boolean toggle for this, or a custom method that takes a label string and returns the shortened
  label. Also available as `ragraph.plot.generic.Style.labels.shorten`.
- Updated compatibility tests to include new
  [`ragraph.analysis.compatibility.CompatibilityAnalysis`][ragraph.analysis.compatibility.CompatibilityAnalysis]
  plot method.

### Fixed

- Fixed duplicate UUID field in Metadata.

## 1.14.2

- Hotfix to scaling.

## 1.14.1

- Added an extra `scaling_weight` field to the
  [`ragraph.plot.generic.PieMapStyle`][ragraph.plot.generic.PieMapStyle] object that scales the
  piecharts drawn in a piemap plot component according to a specified edge weight. Note that it
  stacks with every edge in a bundle between two displayed nodes by means of the product of the
  available values.

## 1.14.0

- Added `ragraph.analysis.comparison.DeltaAnalysis` class for performing delta analysis on
  [`Graph`][ragraph.graph.Graph] objects.
- Added `ragraph.analysis.comparison.SigmaAnalysis` class for performing sigma analysis on
  [`Graph`][ragraph.graph.Graph] objects.

## 1.13.1

- Switch from a brute-force to a Binary Decision Diagram implementation as the backbone for the
  compatibility module.

## 1.13.0

- Added a compatibility analysis module:
  [`ragraph.analysis.compatibility`][ragraph.analysis.compatibility]. Usage documentation available
  at [the compatibility section](./how-to-guides/compatibility.md).

## 1.12.1

- Added
  [`ragraph.analysis.similarity.SimilarityAnalysis`][ragraph.analysis.similarity.SimilarityAnalysis]
  class for performing a product portfolio similarity analysis.

## 1.12.0

- Updated and reorganized all dependencies into a more simplified structure.
  - Now, the only optional dependencies are RaESL (as extra `esl`) and kaleido (as extra `plot`).
- Removed the obsolete API server with Connexion. It's currently unused and only burdens the package
  with higher maintenance.
  - If we'd ever need it again, we can look back at it later in the Git history.
  - Connexion's development is currently changing a lot as well, so we'd probably be better off
    starting over then.
- Removed CLI as the only supported command was the API server.

## 1.11.4

- Fixup Canopy export schema key for "session" format.

## 1.11.3

- Fixup the export of labels in Canopy (de-duplicate, keep order).

## 1.11.2

- Fixup the export of weights in Canopy (force floats).

## 1.11.1

- Fixup the `$schema` key in Canopy export.

## 1.11.0

- Added methods to import and export graphs from and to <https://canopy.ratio-case.nl> and its
  corresponding JSON schemas: `ragraph.io.canopy.from_canopy` and `ragraph.io.canopy.to_canopy`.

## 1.10.6

- Allow specification of a `symmetrize` parameter to the different Markov **clustering** algorithms
  that adds the transpose of a (potentially asymmetrical) matrix to create a guaranteed symmetrical
  matrix with respect to the diagonal. This should give more consistent clustering results while
  maintaining "stronger" connections between nodes that already had bi-directional edges between
  them. Influences [`ragraph.analysis.cluster.markov`][ragraph.analysis.cluster.markov],
  [`ragraph.analysis.cluster.hierarchical_markov`][ragraph.analysis.cluster.hierarchical_markov],
  and [`ragraph.analysis.heuristics.markov_gamma`][ragraph.analysis.heuristics.markov_gamma]. The
  Markov sequencing is not included, as that would not make sense at all.
- Modified Markov sequencing with a `scale` toggle that modifies the inflow vector to contain the
  sum of the corresponding adjacency matrix's columns. To interpret this in a sequencing context: a
  node doesn't have to "split" its output and divide it over it's successors, but it rather delivers
  something that each target node should acquire fully. It is therefore the new default option
  (`scale = True`). Clustering algorithms have not been adjusted to incorporate this as that would
  stray too far off the original Markov clustering implementation.
- Added rudimentary debugging output to analysis. The output is rather verbose and is sent on a
  [`ragraph.analysis.logger`][ragraph.analysis.logger] named `"ragraph.analysis"`.

## 1.10.5

- Tiny bugfix when axis sort should neither sort by width or bus status (only hierarchy).

## 1.10.4

- Make [`ragraph.analysis.sequence.utils.branchsort`][ragraph.analysis.sequence.utils.branchsort]
  actually respect the inplace argument.

## 1.10.3

- Add `inherit` option to the [`ragraph.plot.generic.PieMapStyle`][ragraph.plot.generic.PieMapStyle]
  options to display edges between descendants of nodes in the figures using PieMap components such
  as [`ragraph.plot.mdm`][ragraph.plot.mdm] and friends.

## 1.10.2

- Add `inherit` and `loops` boolean toggles to any applicable Analysis class and therefore to all
  methods where applicable.

## 1.10.1

- Add an `inherit` option to the SCC algorithm. By default, it is set to `True` and makes sure any
  edges between descendants are taken into account, too.

## 1.10.0

- Added better control of the default sorting behavior in RaGraph MDM plots. See `axis_sort`.
- Updated documentation to reflect color overrides [plotting](./how-to-guides/plotting.md).
- Improved graph slicing to include edge filtering or leaving everything blank for a full deepcopy.
  See [`ragraph.graph.Graph.get_graph_slice`][ragraph.graph.Graph.get_graph_slice].

## 1.9.0

- Allow combined color palette overrides, e.g. both a categorical color override for a field as well
  as a numerical color palette.

## 1.8.9

- Add a SCC tearing sequencing algorithm. See [`scc_tearing`][ragraph.analysis.sequence.scc_tearing]
  for usage.

## 1.8.8

- Add `leafs` argument to
  [`ragraph.analysis.sequence.utils.branchsort`][ragraph.analysis.sequence.utils.branchsort]. The
  nodes given to this argument are treated as leaf nodes and their descendants are therefore exempt
  from being reordered.

## 1.8.7

- Fixup a plotting issue where subplots didn't receive the plotting style options.

## 1.8.6

- Fixup a pre-processing step in branchsort analyses where root lists of length 1 were treated as
  cases where nothing had to be sorted.

## 1.8.4

- Add option to allow CORS.

## 1.8.3

- Refactored `ragraph.colors.get_swatchplot` into
  [`ragraph.plot.utils.get_swatchplot`][ragraph.plot.utils.get_swatchplot].

## 1.8.2

- Fixup cyclic import troubles. Getting a color from a palette in the plot
  [`ragraph.plot.Style.palettes`][ragraph.plot.Style.palettes] is now available under the `palettes`
  field of type
  [`ragraph.plot.generic.Palettes.get_categorical_color`][ragraph.plot.generic.Palettes.get_categorical_color]
  and
  [`ragraph.plot.generic.Palettes.get_continuous_color`][ragraph.plot.generic.Palettes.get_continuous_color]
  methods.

## 1.8.1

- Refactor `ragraph.plot.colors` into [`ragraph.colors`][ragraph.colors]. This allows it to be
  used even if the plotting dependencies aren't present.

## 1.8.0

- Initial merge of API v2.

## 1.7.4

- Added more DSM datasets.

## 1.7.3

- Pipeline and versioning updates.

## 1.7.2

- Dependency updates.

## 1.7.1

- Addition of the
  [`ragraph.plot.generic.PieMapStyle.customhoverkeys`][ragraph.plot.generic.PieMapStyle.customhoverkeys]
  attribute. This attribute allows a user to provide a list of keys that indicate which information
  stored within the [`ragraph.edge.Edge.annotations`][ragraph.edge.Edge.annotations] object is to be
  displayed on hover within a `ragraph.plot.PieMap` plot.

## 1.7.0

- Addition of the [`ragraph.plot.dmm`][ragraph.plot.dmm] plot function for visualizing mapping
  matrices.
- Addition of the `row_col_numbers` argument to the [`ragraph.plot.mdm`][ragraph.plot.mdm] and
  `ragraph.plot.dsm` plot functions for adding row and column numbers to the figures.

## 1.6.1

- Several small bug fixes regarding the scaling of figures when adding custom plot components.
- Added usage docs for [`ragraph.plot`][ragraph.plot] over at
  [plotting](./how-to-guides/plotting.md).

## 1.6.0

- Added a [`ragraph.analysis.sequence.axis`][ragraph.analysis.sequence.axis] sequencing
  'algorithm' that sorts nodes like we typically want them to on matrix axis as a replacement for
  the utils floating around. That means, they get sorted by node kind first (and hierarchy)
  primarily, followed by a sorting of "sibling" nodes where buses and larger clusters (in terms of
  displayed leaf nodes) are put first.

## 1.5.0

- Added UUID generation to the [`ragraph.generic.Metadata`][ragraph.generic.Metadata] class. This
  means that we tag every [`ragraph.node.Node`][ragraph.node.Node],
  [`ragraph.edge.Edge`][ragraph.edge.Edge], or [`ragraph.graph.Graph`][ragraph.graph.Graph]
  instance with a unique code to track them over time. This is especially useful for the API and
  future referencing of identical objects.
  - This change affects the `.json_dict` property of these objects to work with these UUIDs (as
    strings) instead of the object names to reference them.
- UUIDs are now generated as an incrementing integer during test runs such that we generate the same
  identical (and easily identifiable) in each run. Note that they are very much random in
  "real-life" situations.
- Removed soon-to-be-deprecated API v1 tests as bringing them up-to-par would be a waste of time.

## 1.4.5

- Improved scaling of large MDM plots.

## 1.4.4

- Bug fix. [`ragraph.plot.mdm`][ragraph.plot.mdm] now supports plotting graphs with more than ten
  edge labels out of the box.
- Bug fix. [`ragraph.plot.mdm`][ragraph.plot.mdm] legend plotting no longer crashes on empty list
  of edges.

## 1.4.3

- Some convenience fixups to the `ragraph.api` module.
- The CLI now supports arguments via environment variables. They are of the form of
  `RAGRAPH_{COMMAND}_{OPTION}`.

## 1.4.2

- Bug fix of [`ragraph.plot.components.piemap.PieMap`][ragraph.plot.components.piemap.PieMap]
  regarding the visualization of matrices that contain one or more busareas.
- Additon of the `sort` keyword to [`ragraph.plot.mdm`][ragraph.plot.mdm] which defines whether
  the provided leaf list should be sorted according to the hierarchical node structure and different
  node domains. Defaults to `True`.
- Changed the default value of the keyword `show` of [`ragraph.plot.mdm`][ragraph.plot.mdm] to
  `False`.

## 1.4.1

- Bug fix. The type of
  [`ragraph.plot.generic.Palettes.fields`][ragraph.plot.generic.Palettes.fields] is updated to
  `Dict[str, Union[str, List[str]]]`. As such, one can providing a mapping of field names to a
  hex-colorcodes or to a lists of hex-colorcodes:

  - A single colorcode is to be used when one wants to set the color of an edge label.
  - A list of colorcodes is to be used when one wants to provide a colormap for an edge weight.

## 1.4.0

- Added a rudimentary plotting module under [`ragraph.plot`][ragraph.plot]. The only currently
  built-in plot type is the [`ragraph.plot.mdm`][ragraph.plot.mdm], but groundwork is in place
  with re-usable plot components under [`ragraph.plot.components`][ragraph.plot.components] and
  the color palette management under `ragraph.plot.colors`. The usage manual should follow soon.

## 1.3.2

- Changed internal backend of [`ragraph.io.esl.from_esl`][ragraph.io.esl.from_esl] to
  `raesl.compile.to_graph`. This changes calls to
  [`ragraph.io.esl.from_esl`][ragraph.io.esl.from_esl] slightly since it now requires positional
  arguments `*paths` instead of a list of paths.

## 1.3.1

- Fixed an issue where the `ruamel.yaml` dependency is installed as `ruamel_yaml`.

## 1.3.0

- New [`ragraph.generic.Metadata`][ragraph.generic.Metadata] model for generic classes
  - Metadata standardizes name, kind, labels, weights, and annotations.
  - Applied to [`ragraph.node.Node`][ragraph.node.Node],
    [`ragraph.edge.Edge`][ragraph.edge.Edge] and [`ragraph.graph.Graph`][ragraph.graph.Graph]
    classes.
  - Annotations is now a derived Mapping class.
  - Updated all IO classes to support this.
  - Applied a workaround to the API to support this, too.

## 1.2.2

- Fixups to the [`ragraph.generic.Mapping`][ragraph.generic.Mapping] class and its usage in the
  plot module.

## 1.2.1

- Added `ragraph.graph.Graph.get_edge_selection` and
  `ragraph.graph.Graph.get_node_and_edge_selection` methods to select nodes and edges for plotting
  purposes.

## 1.2.0

- Added a [`ragraph.generic.Mapping`][ragraph.generic.Mapping] class that will mainly be featured
  in future endeavours featuring plotting functionality. Works as a dictionary whose keys are also
  properties of the object. Moreover, you can include default values and optional validators for
  certain keys/properties of the object. It's intended as a base class to derive mappings from for a
  specific purpose.

## 1.1.0

- Simplified the use of the `ragraph.analysis._classes.Analysis` classes and their corresponding
  wrappers by moving the latter into the former. The publicly available methods are now the wrapped
  ones that check the parameter input.

## 1.0.1

- Added better analysis descriptions through their `repr` and `str` representations. For help
  regarding an analysis, simply look at its repr or string how to call it.
- Made branchsort more convenient by allowing supplying Analysis instances, too.

## 1.0.0

- Apply new Python project template.
- Set algorithm specific modules as private modules. Regular usage should refer to the category
  specific imported ones. This means that `from ragraph.analyis.bus import gamma` from now on
  undeniably imports the function and not the submodule (which is now named
  `ragraph.analysis.bus._gamma`.)

## 0.3.1

- Fix the Climate Control case to correspond to the reference document by Pimmler. Make sure to use
  it with an edge weight filter set to `"adjacency"` for algorithms that require nonnegative input.
- Tests are updated accordingly and an additional test checks whether relevant datasets are actually
  symmetric.

## 0.3.0

- More sophisticated Archimate3.0 export via an `archimate` dictionary in our Annotations object.
  You can now set the element type and documentation of each element using
  `Annotations.archimate["type"]` and `Annotations.archimate["documentation"]`. For all possible
  types, please refer to
  [https://www.opengroup.org/xsd/archimate](https://www.opengroup.org/xsd/archimate).

## 0.2.0

- Added an Archimate3.0 XML compatible export for Graph objects. See
  [https://www.opengroup.org/xsd/archimate](https://www.opengroup.org/xsd/archimate) for more info.

## 0.1.2

- Fixed loading JSON files with set edge IDs. It now sets the last used edge ID number correctly.

## 0.1.1

- Minor bug fix for edge ID generation.

## 0.1.0

- Added XML I/O support using the XML Metadata Interchange format (XMI) in
  [`ragraph.io.xml`][ragraph.io.xml].

## 0.0.1

Initial version from preceding projects `graph_io`, `graph_analysis`, `ratio_datasets`,
`architecture` and `ratio_backend`.
