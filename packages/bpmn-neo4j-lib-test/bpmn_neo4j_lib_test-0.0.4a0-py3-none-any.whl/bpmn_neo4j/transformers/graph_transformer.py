import logging
import uuid

from bpmn_neo4j.transformers.nodes import generate_nodes
from bpmn_neo4j.transformers.edges import generate_edges
from bpmn_neo4j.transformers.pool_lanes import generate_pools_lanes
from bpmn_neo4j.transformers.transform_input_elements import normalize_flow_elements


class GraphTransformer:
    def __init__(self, json_data):
        self.data = json_data
        self.process_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # 🔍 Deteksi apakah JSON sudah terstruktur atau mentah
        if all(k in json_data for k in ["activities", "events", "gateways", "flows"]):
            self.logger.info("📄 Detected structured BPMN JSON → using as-is")
            self.elements = json_data
        elif "flowElements" in json_data:
            self.logger.info("🔍 Detected raw BPMN JSON → applying normalization")
            self.elements = normalize_flow_elements(json_data)
        else:
            self.logger.warning("⚠️ Unsupported JSON structure → No elements will be processed")
            self.elements = {
                "activities": [], "events": [], "gateways": [],
                "flows": [], "pools": [], "lanes": []
            }

        self.cypher_queries = []
        self.node_count = 0
        self.edge_count = 0

    def transform(self):
        self.logger.info(f"🔧 Starting BPMN to Neo4j transformation | process_id={self.process_id}")

        self.process_pools_and_lanes()
        self.logger.info(f"✅ Processed pools and lanes | pools={len(self.elements.get('pools', []))}, lanes={len(self.elements.get('lanes', []))}")

        self.process_nodes()
        self.logger.info(f"✅ Processed nodes | activities={len(self.elements.get('activities', []))}, events={len(self.elements.get('events', []))}")

        self.process_edges()
        self.logger.info(f"✅ Processed edges | flows={len(self.elements.get('flows', []))}")

        self.logger.info(f"📊 Transformation complete: {self.node_count} nodes, {self.edge_count} edges")
        return self.cypher_queries

    def process_pools_and_lanes(self):
        queries = generate_pools_lanes(self.elements, process_id=self.process_id)
        self.cypher_queries += queries

        self.node_count += sum(1 for q in queries if "CREATE (:" in q and ")-[" not in q)
        self.edge_count += sum(1 for q in queries if "CREATE (" in q and ")-[" in q)

    def process_nodes(self):
        queries = generate_nodes(self.elements, process_id=self.process_id)
        self.cypher_queries += queries

        self.node_count += sum(1 for q in queries if "CREATE (" in q and ")-[" not in q)

    def process_edges(self):
        queries = generate_edges(self.elements, process_id=self.process_id)
        self.cypher_queries += queries

        self.edge_count += len(queries)

    def batch_output(self, batch_size=50):
        for i in range(0, len(self.cypher_queries), batch_size):
            yield self.cypher_queries[i:i + batch_size]

    def write_to_file(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            for query in self.cypher_queries:
                f.write(query + "\n")

    def execute_on_neo4j(self, executor):
        for batch in self.batch_output():
            if not batch:
                self.logger.warning("⚠️ Skipping empty Cypher batch.")
                continue
            executor.run_batch(batch)
            self.logger.info(f"🚀 Executed batch of {len(batch)} queries")
