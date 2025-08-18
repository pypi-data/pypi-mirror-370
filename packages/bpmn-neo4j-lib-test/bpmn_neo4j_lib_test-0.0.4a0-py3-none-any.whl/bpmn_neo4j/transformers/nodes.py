import json

def generate_nodes(elements, process_id=None):
    cypher = []

    def to_cypher_value(val):
        return 'null' if val is None else json.dumps(val)

    # ACTIVITY NODES
    for act in elements.get("activities", []):
        pool_id = to_cypher_value(act.get("pool_id"))
        lane_id = to_cypher_value(act.get("lane_id"))

        cypher.append(
            f"CREATE (a:Activity {{id: '{act['id']}', name: '{act['name']}', type: '{act['type']}', "
            f"pool_id: {pool_id}, lane_id: {lane_id}, process_id: '{process_id}'}});"
        )

    # EVENT NODES
    for evt in elements.get("events", []):
        name = evt.get("name", "")
        event_type = evt.get("event_type") or evt.get("type") or ""  # 🟢 fallback jika event_type kosong/null
        if not name.strip():
            if "start" in event_type.lower():
                name = "Start"
            elif "end" in event_type.lower():
                name = "End"

        pool_id = to_cypher_value(evt.get("pool_id"))
        lane_id = to_cypher_value(evt.get("lane_id"))

        cypher.append(
            f"CREATE (e:Event {{id: '{evt['id']}', name: '{name}', type: '{evt['type']}', "
            f"event_type: '{event_type}', bpmn_type: '{event_type}', "
            f"pool_id: {pool_id}, lane_id: {lane_id}, process_id: '{process_id}'}});"
        )

    return cypher
