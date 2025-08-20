# Explanation and rationale

You might be wondering why RaGraph was even created with the existence of libraries such as
`networkx` or `graph-tool` also populating the landscape. In part, it was the clear need to describe
both hierarchies as well as regular relations between nodes, paired with rich, custom metadata that
we wanted to store. Also, we had quite a palette of custom analysis methods we wanted to implement
and clear access to a Graph's DSM at all times, which would have resulted in fairly custom object
anyways.

Both of these reasons are partly due to the fact that we at Ratio CASE are a Systems Engineering
company. We use our software intensively in that field and have grown to like having a proprietary
implementation that we understand fully. It's a living library, catered to our needs in Systems
Engineering.

For now, RaGraph is a pure Python library, but since we have been re-implementing some of our
software in Rust, some backend parts might be slowly replaced with Rust wrappers. This often comes
with speed benefits and limits chances of "misuse" as only the required parts would be exposed.
