# py2gds

WIP.

Library to build Neo4j's queries with special attention on Graph Data Science library calls.

It provides a DSL to write queries inspired in IGQL.

## Example

```python
from py2gds.connection import GraphConnection
from py2gds.dsl import Query
from py2gds.algorithms.algorithm import AlgorithmType

graph_connection = GraphConnection.to_py2neo(
        uri=f"{app_config.neo4j.scheme}://{app_config.neo4j.host}:{app_config.neo4j.port}",
        password=app_config.neo4j.password,
    )

pages_rank = (Query.using(graph_connection)
.rank(algorithm=AlgorithmType.ArticleRank)
.projected_by(labels=("Page",), relationships=("LINKS",))
.run(log=True)
)
print(pages_rank)

```

## Install

    pip install neo4j-gds
    
