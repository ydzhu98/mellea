"""Graph database backend implementations."""

from mellea.contribs.kg.graph_dbs.base import GraphBackend
from mellea.contribs.kg.graph_dbs.mock import MockGraphBackend

try:
    from mellea.contribs.kg.graph_dbs.neo4j import Neo4jBackend

    __all__ = [
        "GraphBackend",
        "Neo4jBackend",
        "MockGraphBackend",
    ]
except ImportError:
    # Neo4j driver not installed
    __all__ = [
        "GraphBackend",
        "MockGraphBackend",
    ]
