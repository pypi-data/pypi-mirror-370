from neo4j import GraphDatabase
import time

class Neo4jExecutor:
    def __init__(self, uri, user, password, max_pool_size=50):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=max_pool_size
        )

    def close(self):
        self.driver.close()

    def run_health_check(self):
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS ok")
                return result.single()["ok"] == 1
        except Exception:
            return False

    def setup_indexes(self):
        index_queries = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Activity) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Event) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Pool) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Lane) ON (n.id)"
        ]
        with self.driver.session() as session:
            for query in index_queries:
                session.run(query)

    def run_batch(self, cypher_lines, reset=False, batch_size=20, retry=3, process_id=None):
        with self.driver.session() as session:
            if reset:
                print("🧹 Resetting database...")
                session.run("MATCH (n) DETACH DELETE n")
                print("✅ Database cleared.")

            filtered_lines = [line for line in cypher_lines if line.strip() and not line.strip().startswith("//")]

            total_executed = 0
            start_time = time.perf_counter()

            for i in range(0, len(filtered_lines), batch_size):
                batch = filtered_lines[i:i + batch_size]

                for attempt in range(retry):
                    try:
                        print(f"\n✅ Executing batch {i // batch_size + 1} ({len(batch)} queries):")
                        for line in batch:
                            if line.strip():
                                session.run(line)
                                print(f"   ➤ {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")
                                total_executed += 1
                        break
                    except Exception as e:
                        print(f"⚠️ Retry {attempt+1}/{retry} failed: {e}")
                        time.sleep(1)
                else:
                    print(f"❌ Final failure executing batch at index {i}")

            end_time = time.perf_counter()

            if not filtered_lines:
                print("⚠️ No Cypher queries to execute in this batch.")
                return

            duration = end_time - start_time
            print(f"✅ Total queries executed: {len(filtered_lines)}")
            print(f"⏱️ Total execution time: {duration:.2f}s → Avg: {duration / len(filtered_lines):.4f}s/query")
            return process_id

    def find_paths(self, process_id, max_depth=20):
        query = f"""
        MATCH (start:Event {{type: 'startevent', process_id: '{process_id}'}})
        MATCH (end:Event {{type: 'endevent', process_id: '{process_id}'}})
        MATCH p = (start)-[r*..{max_depth}]->(end)
        WHERE ALL(rel IN r WHERE rel.type IS NOT NULL AND rel.flow_type IS NOT NULL)
        RETURN [node IN nodes(p) | node.name] AS path
        """
        with self.driver.session() as session:
            result = session.run(query)
            paths = [record["path"] for record in result]
            return paths

    def get_metrics(self, process_id):
        with self.driver.session() as session:
            counts = {}

            def count_query(label):
                result = session.run(f"""
                    MATCH (n:{label} {{process_id: '{process_id}'}})
                    RETURN count(n) AS count
                """)
                return result.single()["count"]

            counts["total_nodes"] = session.run(f"""
                MATCH (n {{process_id: '{process_id}'}})
                RETURN count(n) AS count
            """).single()["count"]

            counts["activities"] = count_query("Activity")
            counts["events"] = count_query("Event")

            # 🔄 Ganti bpmn_type → type
            counts["start_events"] = session.run(f"""
                MATCH (e:Event {{type: 'startevent', process_id: '{process_id}'}})
                RETURN count(e) AS count
            """).single()["count"]

            counts["end_events"] = session.run(f"""
                MATCH (e:Event {{type: 'endevent', process_id: '{process_id}'}})
                RETURN count(e) AS count
            """).single()["count"]

            paths = self.find_paths(process_id)
            counts["paths"] = len(paths)
            counts["avg_path_length"] = round(sum(len(p) for p in paths) / len(paths), 2) if paths else 0

            return counts

    def run_custom_query(self, query: str):
        with self.driver.session() as session:
            result = session.run(query)
            records = []
            for record in result:
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    record_dict[key] = dict(value) if hasattr(value, "items") else value
                records.append(record_dict)
            return records

    def fetch_graph_by_process_id(self, process_id: str):
        query = f"""
        MATCH (n {{process_id: '{process_id}'}})
        OPTIONAL MATCH (n)-[r]->(m {{process_id: '{process_id}'}})
        RETURN n, r, m
        """
        with self.driver.session() as session:
            result = session.run(query)
            records = []
            for record in result:
                n = dict(record["n"]) if record.get("n") else None
                m = dict(record["m"]) if record.get("m") else None
                r = dict(record["r"]) if record.get("r") else None
                records.append({"n": n, "r": r, "m": m})
            return records
