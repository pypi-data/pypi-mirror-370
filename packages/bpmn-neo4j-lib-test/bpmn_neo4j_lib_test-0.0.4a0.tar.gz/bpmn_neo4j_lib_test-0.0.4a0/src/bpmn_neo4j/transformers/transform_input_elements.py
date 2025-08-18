import uuid
import json

def map_flows_to_source_target(elements):
    flow_map = {}

    for el in elements:
        el_id = el.get("id")
        el_name = el.get("name", "")
        el_type = el.get("type", "").lower()

        # ✅ Penanganan khusus untuk messageFlow
        if "messageflow" in el_type:
            for src in el.get("incoming", []):
                if el_id not in flow_map:
                    flow_map[el_id] = {}
                flow_map[el_id]["source"] = src
                flow_map[el_id]["source_name"] = ""  # Optional: bisa diisi nama node
            for tgt in el.get("outgoing", []):
                if el_id not in flow_map:
                    flow_map[el_id] = {}
                flow_map[el_id]["target"] = tgt
                flow_map[el_id]["target_name"] = ""  # Optional
            continue

        # 🔁 Default untuk node biasa
        for out_flow in el.get("outgoing", []):
            if out_flow not in flow_map:
                flow_map[out_flow] = {}
            flow_map[out_flow]["source"] = el_id
            flow_map[out_flow]["source_name"] = el_name

        for in_flow in el.get("incoming", []):
            if in_flow not in flow_map:
                flow_map[in_flow] = {}
            flow_map[in_flow]["target"] = el_id
            flow_map[in_flow]["target_name"] = el_name

    return flow_map


def normalize_flow_elements(data, process_id=None):
    elements = data.get("flowElements", [])

    # ✅ Tambahkan messageFlows (khusus edge, bukan node)
    message_flows = data.get("messageFlows", [])
    elements += message_flows

    # 🔧 Generate process_id jika belum ada
    process_id = process_id or data.get("process_id") or str(uuid.uuid4())

    # 🔍 Buat index elemen berdasarkan ID untuk lookup pool/lane nanti
    element_by_id = {el.get("id"): el for el in elements}
    flow_map = map_flows_to_source_target(elements)

    result = {
        "activities": [],
        "events": [],
        "gateways": [],
        "flows": [],
        "pools": data.get("pools", []),
        "lanes": data.get("lanes", []),
    }

    for el in elements:
        raw_type = el.get("type", "")
        el_type = raw_type.lower()
        sub_type = (el.get("subType") or "").lower()

        # 🩹 Auto-detect sub_type if missing
        if not sub_type:
            if "startevent" in el_type:
                sub_type = "startEvent"
            elif "endevent" in el_type:
                sub_type = "endEvent"
            elif "intermediate" in el_type:
                sub_type = "intermediateEvent"
            elif "exclusivegateway" in el_type:
                sub_type = "exclusiveGateway"
            elif "parallelgateway" in el_type:
                sub_type = "parallelGateway"
            elif "inclusivegateway" in el_type:
                sub_type = "inclusiveGateway"
            elif "eventbasedgateway" in el_type:
                sub_type = "eventBasedGateway"

        element_id = el.get("id")
        name = el.get("name", "")
        props = el.get("properties", {}) or {}

        pool_id = props.get("pool_id")
        lane_id = props.get("lane_id")

        # ✅ Flow (sequence/message) → bukan node, hanya relationship
        if "flow" in el_type:
            flow_id = element_id
            flow_info = flow_map.get(flow_id, {})

            source_id = flow_info.get("source")
            target_id = flow_info.get("target")

            source_el = element_by_id.get(source_id, {})
            target_el = element_by_id.get(target_id, {})

            source_props = source_el.get("properties", {}) or {}
            target_props = target_el.get("properties", {}) or {}

            result["flows"].append({
                "id": flow_id,
                "name": name,
                "type": sub_type or el_type,
                "source": source_id,
                "target": target_id,
                "source_name": flow_info.get("source_name", ""),
                "target_name": flow_info.get("target_name", ""),
                "source_pool": source_props.get("pool_id"),
                "source_lane": source_props.get("lane_id"),
                "target_pool": target_props.get("pool_id"),
                "target_lane": target_props.get("lane_id"),
                "process_id": process_id
            })
            continue

        if "task" in el_type:
            result["activities"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "pool_id": pool_id,
                "lane_id": lane_id,
                "process_id": process_id
            })

        elif any(x in el_type for x in ["event", "startevent", "endevent"]):
            result["events"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "event_type": sub_type or el_type,
                "pool_id": pool_id,
                "lane_id": lane_id,
                "process_id": process_id
            })

        elif "gateway" in el_type:
            result["gateways"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "gateway_type": sub_type,
                "pool_id": pool_id,
                "lane_id": lane_id,
                "process_id": process_id
            })

    # 🔧 Normalize pool and lane to prevent KeyError
    normalized_pools = []
    for pool in result["pools"]:
        normalized_pools.append({
            "id": pool.get("id"),
            "name": pool.get("name", ""),
            "type": pool.get("type", "Pool"),
            "process_ref": pool.get("process_ref", "")
        })

    normalized_lanes = []
    for lane in result["lanes"]:
        normalized_lanes.append({
            "id": lane.get("id"),
            "name": lane.get("name", ""),
            "type": lane.get("type", "Lane"),
            "pool_id": lane.get("pool_id", "")
        })

    result["pools"] = normalized_pools
    result["lanes"] = normalized_lanes
    result["process_id"] = process_id

    return result
