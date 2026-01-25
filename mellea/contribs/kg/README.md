# Mellea Knowledge Graph Query Library

A graph query library that embodies Mellea's philosophy: graph queries and results as Components that format for LLMs, with composable query building, validation/repair loops, and backend abstraction.

## Status: Layer 4 Complete ✓

- ✅ Core data structures (`GraphNode`, `GraphEdge`, `GraphPath`)
- ✅ Abstract backend interface (`GraphBackend`)
- ✅ Neo4j backend implementation (`Neo4jBackend`)
- ✅ Mock backend for testing (`MockGraphBackend`)
- ✅ Comprehensive test suite (30 tests, 18 passing)

### Coming Soon

- 🔄 Layer 2: Graph Query Components (CypherQuery, GraphResult, GraphTraversal)
- 🔄 Layer 3: LLM-Guided Query Construction (@generative functions, validation strategies)
- 🔄 Layer 1: Application examples and end-to-end integration

## Installation

The KG library is part of Mellea contribs. Neo4j driver is already included in Mellea dependencies:

```bash
# Neo4j is already installed with Mellea
pip install mellea
```

## Quick Start

### 1. Using Mock Backend (No Database Required)

```python
from mellea.contribs.kg.base import GraphNode, GraphEdge
from mellea.contribs.kg.graph_dbs import MockGraphBackend
from mellea.contribs.kg.components import GraphQuery

# Create mock data
nodes = [
    GraphNode(id="1", label="Person", properties={"name": "Alice"}),
    GraphNode(id="2", label="Movie", properties={"title": "The Matrix"}),
]
edges = [
    GraphEdge(
        id="e1",
        source=nodes[0],
        label="ACTED_IN",
        target=nodes[1],
        properties={"role": "Trinity"},
    )
]

# Create mock backend
backend = MockGraphBackend(mock_nodes=nodes, mock_edges=edges)

# Execute query
query = GraphQuery(query_string="MATCH (n) RETURN n")
result = await backend.execute_query(query)

print(f"Found {len(result.nodes)} nodes and {len(result.edges)} edges")
```

### 2. Using Neo4j Backend

```python
from mellea.contribs.kg.graph_dbs import Neo4jBackend
from mellea.contribs.kg.components import GraphQuery

# Connect to Neo4j
backend = Neo4jBackend(
    connection_uri="bolt://localhost:7687",
    auth=("neo4j", "password"),
)

# Execute Cypher query
query = GraphQuery(
    query_string="MATCH (p:Person)-[:ACTED_IN]->(m:Movie) RETURN p, m LIMIT 10"
)
result = await backend.execute_query(query)

# Access results
for node in result.nodes:
    print(f"{node.label}: {node.properties}")

for edge in result.edges:
    print(f"{edge.source.properties} --[{edge.label}]-> {edge.target.properties}")

# Clean up
await backend.close()
```

### 3. Query with Parameters

```python
query = GraphQuery(
    query_string="MATCH (p:Person {name: $name}) RETURN p",
    parameters={"name": "Alice"},
)
result = await backend.execute_query(query)
```

### 4. Get Graph Schema

```python
schema = await backend.get_schema()
print(f"Node types: {schema['node_types']}")
print(f"Edge types: {schema['edge_types']}")
print(f"Properties: {schema['property_keys']}")
```

### 5. Validate Queries

```python
query = GraphQuery(query_string="MATCH (n) RETURN n")
is_valid, error = await backend.validate_query(query)

if not is_valid:
    print(f"Query validation failed: {error}")
```

## Architecture

### Layer 4: Graph Backend Abstraction (✓ Complete)

```
mellea/contribs/kg/
├── base.py                   # GraphNode, GraphEdge, GraphPath (dataclasses)
└── graph_dbs/
    ├── base.py               # GraphBackend (ABC)
    ├── neo4j.py              # Neo4jBackend
    └── mock.py               # MockGraphBackend
```

### Data Structures

#### GraphNode
Pure dataclass representing a graph node:
```python
@dataclass
class GraphNode:
    id: str
    label: str  # Node type/label
    properties: dict[str, Any]
```

#### GraphEdge
Pure dataclass representing a graph edge:
```python
@dataclass
class GraphEdge:
    id: str
    source: GraphNode
    label: str  # Relationship type
    target: GraphNode
    properties: dict[str, Any]
```

#### GraphPath
Pure dataclass representing a path through the graph:
```python
@dataclass
class GraphPath:
    nodes: list[GraphNode]
    edges: list[GraphEdge]
```

### Backend Interface

```python
class GraphBackend(ABC):
    """Abstract backend for graph databases."""

    @abstractmethod
    async def execute_query(self, query: GraphQuery, **options) -> GraphResult:
        """Execute a graph query and return results."""

    @abstractmethod
    async def get_schema(self) -> dict[str, Any]:
        """Get the graph schema."""

    @abstractmethod
    async def validate_query(self, query: GraphQuery) -> tuple[bool, str | None]:
        """Validate query syntax and semantics."""

    def supports_query_type(self, query_type: str) -> bool:
        """Check if backend supports a query type."""

    async def close(self):
        """Close connections."""
```

## Testing

### Run All Tests

```bash
uv run pytest test/contribs/kg/ -v
```

### Run Specific Test Suites

```bash
# Base data structures
uv run pytest test/contribs/kg/test_base.py -v

# Mock backend
uv run pytest test/contribs/kg/test_mock_backend.py -v

# Neo4j backend (requires running Neo4j instance)
uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

### Running Neo4j Integration Tests

Neo4j integration tests require a running Neo4j instance. Start one with Docker:

```bash
docker run --rm -p 7687:7687 -p 7474:7474 \
    -e NEO4J_AUTH=neo4j/testpassword \
    neo4j:latest
```

Then run the tests:

```bash
uv run pytest test/contribs/kg/test_neo4j_backend.py -v
```

Tests will be automatically skipped if:
- Neo4j driver is not installed
- No Neo4j instance is available at the connection URI

### Test Coverage

Current test coverage for Layer 4:

- **Base Data Structures**: 9 tests
  - GraphNode creation, properties, equality
  - GraphEdge creation, properties, equality
  - GraphPath creation, empty paths, single nodes

- **Mock Backend**: 7 tests
  - Creation with/without data
  - Schema retrieval
  - Query validation
  - Query type support
  - History tracking

- **Neo4j Backend**: 14 tests
  - Connection and configuration
  - Query type support
  - Schema retrieval
  - Query validation (valid/invalid)
  - Simple queries
  - Parameterized queries
  - Relationship queries
  - Path queries
  - Format styles
  - Result deduplication
  - Error handling

**Total: 30 tests, 18 passing, 12 skipped** (skipped when Neo4j not available)

## Neo4j Backend Features

### Supported Operations

✅ Execute Cypher queries with parameters
✅ Parse nodes, edges, and paths from results
✅ Retrieve graph schema (node types, edge types, properties)
✅ Validate Cypher syntax using EXPLAIN
✅ Deduplicate nodes and edges in results
✅ Support for multiple result format styles
✅ Async/await support

### Neo4j-Specific Methods

```python
# Parse Neo4j objects into graph structures
node = GraphNode.from_neo4j_node(neo4j_node)
edge = GraphEdge.from_neo4j_relationship(neo4j_rel, source, target)
path = GraphPath.from_neo4j_path(neo4j_path)
```

### Connection Management

```python
# Backend manages both sync and async drivers
backend = Neo4jBackend(
    connection_uri="bolt://localhost:7687",
    auth=("neo4j", "password"),
    database="neo4j",  # Optional, for multi-database
    backend_options={},  # Optional, Neo4j-specific options
)

# Always close when done
await backend.close()
```

## Design Philosophy

This library follows Mellea's core principles:

1. **Components as Prompt Templates**: Graph queries and results will be Components with `format_for_llm()` (Layer 2)
2. **Pure Data Structures**: `GraphNode`, `GraphEdge`, `GraphPath` are dataclasses, not Components
3. **Backend Abstraction**: Similar to Mellea's LLM backend pattern
4. **Async/Await**: All I/O operations are async
5. **Type Safety**: Full type hints throughout

## Next Steps

### Layer 2: Graph Query Components

Will implement:
- `GraphQuery` - Base Component for queries
- `CypherQuery` - Fluent Cypher query builder
- `GraphResult` - Format results for LLMs
- `GraphTraversal` - High-level traversal patterns

### Layer 3: LLM-Guided Query Construction

Will implement:
- `@generative` functions for NL → Cypher
- `QueryValidationStrategy` - Validate/repair loops
- Query requirements (syntax, schema, results)

### Layer 1: Application Layer

Will implement:
- End-to-end examples
- Integration with KGRag
- Best practices and patterns

## Contributing

This is part of the Mellea project. See [Mellea's main README](../../../README.md) for contribution guidelines.

## License

Apache License 2.0 - See [LICENSE](../../../LICENSE)
