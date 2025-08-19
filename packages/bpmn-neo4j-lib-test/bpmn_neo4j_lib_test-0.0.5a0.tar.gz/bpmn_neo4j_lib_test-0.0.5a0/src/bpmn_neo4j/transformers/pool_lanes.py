def generate_pools_lanes(elements, process_id=None):
    cypher = []

    for pool in elements.get("pools", []):
        cypher.append(
            f"CREATE (:Pool {{id: '{pool['id']}', name: '{pool['name']}', type: '{pool['type']}', "
            f"process_ref: '{pool['process_ref']}', process_id: '{process_id}'}});"
        )

    for lane in elements.get("lanes", []):
        cypher.append(
            f"CREATE (:Lane {{id: '{lane['id']}', name: '{lane['name']}', type: '{lane['type']}', "
            f"pool_id: '{lane['pool_id']}', process_id: '{process_id}'}});"
        )
        cypher.append(
            f"MATCH (l:Lane {{id: '{lane['id']}'}}) WITH l MATCH (p:Pool {{id: '{lane['pool_id']}'}}) "
            f"CREATE (l)-[:BELONGS_TO]->(p);"
        )

    return cypher
