"""# Kodak Single-Use Camera product commonality

This DSM dataset was actually proposed as a "3D DSM" as it was featured in the reference
papers in a 3D layered fashion. Relationships between components in a product family for
different family members were shown in a 3D layered fashion. Common interfaces and
unique interfaces were color coded accordingly for three family members: The "Fun
Saver", "Outdoor", and "Plus Digital" single-use cameras.

This dataset contains all unique product family components as nodes, where each node is
labeled with the family members it is used in. E.g. the node labels can be any
combination of at least one of the camera type.

Edges indicate an interface between components, which is therefore modeled using an
"adjacency" edge weight. Once again, they are labeled with the camera typename when that
dependency occurs in the corresponding camera type.

Available labels for nodes or edges:

- Fun Saver
- Outdoor
- Plus Digital

Reference:
    Alizon, Fabrice. 2009, February. Module-Based Design Management-Synerg'. Symposium on
    Product Family & Product Platform Design, Helsinki University of Technology (TKK),
    Helsinki, Finland.

Reference:
    Alizon, Fabrice, Seung K. Moon, Steven B. Shooter, and Timothy W. Simpson. 2007,
    September 4--7. Three Dimensional Design Structure Matrix-DSM3D. ASME Design Engineering
    Technical Conferences, DETCZ007-34510, Las Vegas, NV, pp. 941-948.
"""

edge_weights = ["adjacency"]
