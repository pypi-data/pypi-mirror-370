# BPMN → Neo4j Graph Transformation Library

A Python library for converting **BPMN JSON** into a **Neo4j graph database**.  
It provides parsing, schema validation, semantic validation, transformation to Cypher, and execution in Neo4j.  

---

## 📂 Project Structure
```
bpmn-neo4j-lib/
 ├── parsers/            # JSON parsing
 ├── validators/         # Schema + semantic validation
 ├── transformers/       # GraphTransformer, node/edge builders
 ├── neo4j/              # Neo4j executor
 ├── utils/              # Logger
 └── exceptions/         # Custom error handling
```

---

## 📦 Installation

```bash
pip install bpmn-neo4j-lib
```

### Requirements:
- Python 3.10+
- Neo4j 5.x (local or remote)

---

## 🚀 Usage

You can use the library step by step, or orchestrate the whole process with your own wrapper.

---

### 🔹 Step-by-step Example

#### 1. Load a JSON file
```python
from bpmn_neo4j.parsers.json_parser import load_json

data = load_json("examples/sample_bpmn.json")
```
✅ Reads a BPMN JSON file.  
If the file is broken (invalid JSON), the parser attempts auto-repair and saves a `_fixed_by_<method>.json` file.

---

#### 2. Validate schema
```python
from bpmn_neo4j.validators.schema_validator import validate_schema

validated = validate_schema(data, auto_fix=True)
```
✅ Ensures JSON follows the official BPMN schema.  
`auto_fix=True` automatically assigns missing IDs, removes duplicates, and fills required fields.

---

#### 3. Validate semantics
```python
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics

validate_semantics(validated)
```
✅ Checks BPMN Method & Style rules:
- All flows have valid source/target.  
- Start/End events are consistent.  
- Activities and gateways follow BPMN rules.  
- Detects orphan nodes or invalid boundary/message flows.

---

#### 4. Transform JSON into Cypher
```python
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()
```
✅ Converts BPMN nodes & flows into Cypher queries:
- Creates nodes: Activities, Events, Pools, Lanes.  
- Creates edges: Sequence Flows.  
- Keeps track of process_id, node_count, and edge_count.  

---

#### 5. Connect to Neo4j
```python
from bpmn_neo4j.neo4j.neo4j_repositories import Neo4jExecutor

executor = Neo4jExecutor(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678"
)
```
✅ Manages Neo4j connection.  
Supports health checks, index creation, and batch execution of queries.

---

#### 6. Setup indexes
```python
executor.setup_indexes()
```
✅ Ensures Neo4j has indexes for efficient querying:
- `(Activity {id})`  
- `(Event {id})`  
- `(Pool {id})`  
- `(Lane {id})`  

---

#### 7. Run batch Cypher queries
```python
executor.run_batch(
    cypher_lines,
    reset=True,          # clears database first
    batch_size=20,       # queries per transaction
    process_id=transformer.process_id
)
```
✅ Executes generated Cypher queries in Neo4j:
- Resets DB if `reset=True`.  
- Uses batching for efficiency.  
- Associates nodes with process_id.  

---

#### 8. Get graph metrics
```python
print(executor.get_metrics(transformer.process_id))
executor.close()
```
✅ Retrieves graph statistics:
- Node counts (activities, events, start/end).  
- Path count and average path length.  
- Useful for analysis and validation.  

---

### 🔹 Output Example
```json
{
  "total_nodes": 7,
  "activities": 5,
  "events": 2,
  "start_events": 1,
  "end_events": 1,
  "paths": 1,
  "avg_path_length": 7.0
}
```

---

### 🔹 Full Example
```python
from bpmn_neo4j.parsers.json_parser import load_json
from bpmn_neo4j.validators.schema_validator import validate_schema
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
from bpmn_neo4j.neo4j.neo4j_repositories import Neo4jExecutor

# 1. Load BPMN JSON
data = load_json("examples/sample_bpmn.json")

# 2. Schema validation
validated = validate_schema(data, auto_fix=True)

# 3. Semantic validation
validate_semantics(validated)

# 4. Transform to Cypher
transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()

# 5. Execute in Neo4j
executor = Neo4jExecutor("bolt://localhost:7687", "neo4j", "12345678")
executor.setup_indexes()
executor.run_batch(cypher_lines, reset=True, batch_size=20, process_id=transformer.process_id)

# 6. Metrics
print(executor.get_metrics(transformer.process_id))

executor.close()
```

---

## 🧪 Running Tests
```bash
pytest tests/
```

---

## 📜 License
MIT
