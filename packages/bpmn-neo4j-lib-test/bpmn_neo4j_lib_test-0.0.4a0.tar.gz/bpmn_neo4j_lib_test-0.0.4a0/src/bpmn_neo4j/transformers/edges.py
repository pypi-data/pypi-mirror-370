import json

def build_gateway_map(elements):
    return {gw["id"]: gw["gateway_type"] for gw in elements.get("gateways", [])}

def generate_edges(elements, process_id=None):
    cypher = []
    gateway_map = build_gateway_map(elements)

    all_flows = elements.get("flows", []) + elements.get("flows_by_type", {}).get("message_flows", [])

    incoming = {}
    outgoing = {}
    for flow in all_flows:
        src = flow["source"]
        tgt = flow["target"]
        outgoing.setdefault(src, []).append((flow, tgt))
        incoming.setdefault(tgt, []).append((flow, src))

    real_nodes = {el["id"] for el in elements.get("activities", []) + elements.get("events", [])}
    seen_edges = set()

    for flow in all_flows:
        src = flow["source"]
        tgt = flow["target"]
        flow_type = flow.get("type", "SEQUENCE").upper()
        label_raw = flow.get("label") or gateway_map.get(src) or gateway_map.get(tgt) or "SEQUENCE_FLOW"

        rel_name = label_raw.upper().replace(" ", "_").replace("-", "_")
        if not rel_name.isidentifier():
            rel_name = "FLOW"

        props = (
            f"id: '{flow['id']}', name: '{flow.get('name', '')}', "
            f"type: '{label_raw}', flow_type: '{flow_type}', "
            f"source_name: '{flow.get('source_name', '')}', target_name: '{flow.get('target_name', '')}', "
            f"source_pool: {json.dumps(flow.get('source_pool'))}, source_lane: {json.dumps(flow.get('source_lane'))}, "
            f"target_pool: {json.dumps(flow.get('target_pool'))}, target_lane: {json.dumps(flow.get('target_lane'))}, "
            f"process_id: '{process_id}'"
        )

        def add_edge(real_src, real_tgt):
            key = (real_src, real_tgt)
            if key not in seen_edges:
                seen_edges.add(key)
                cypher.append(
                    f"MATCH (a {{id: '{real_src}'}}) "
                    f"WITH a MATCH (b {{id: '{real_tgt}'}}) "
                    f"CREATE (a)-[:{rel_name} {{{props}}}]->(b); "
                )

        # Jika gateway di tengah (bukan real node), sambungkan hanya jika 1:1 (menghindari kombinasi eksplosif)
        if src not in real_nodes and tgt in real_nodes:
            in_links = incoming.get(src, [])
            if len(in_links) == 1:
                real_src = in_links[0][1]
                add_edge(real_src, tgt)
            continue

        if src in real_nodes and tgt not in real_nodes:
            out_links = outgoing.get(tgt, [])
            if len(out_links) == 1:
                real_tgt = out_links[0][1]
                add_edge(src, real_tgt)
            continue

        if src in real_nodes and tgt in real_nodes:
            add_edge(src, tgt)

    return cypher
