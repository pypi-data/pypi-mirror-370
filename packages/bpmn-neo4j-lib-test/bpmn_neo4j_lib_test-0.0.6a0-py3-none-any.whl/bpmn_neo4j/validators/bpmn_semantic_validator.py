def validate_semantics(bpmn_json, strict=False):
    elements = bpmn_json.get("elements", {})
    flows = elements.get("flows", [])
    events = elements.get("events", [])
    gateways = elements.get("gateways", [])
    activities = elements.get("activities", [])
    message_flows = elements.get("message_flows", [])


    errors = []
    warnings = []

    outgoing = {}
    incoming = {}

    # Build incoming and outgoing map
    for flow in flows:
        source = flow.get("source")
        target = flow.get("target")
        outgoing.setdefault(source, []).append(target)
        incoming.setdefault(target, []).append(source)

    # 1. Valid IDs
    valid_ids = set(obj.get("id") for obj in activities + events + gateways)
    
    # 2. Flow reference validation
    for flow in flows:
        source, target, fid = flow.get("source"), flow.get("target"), flow.get("id")
        if source not in valid_ids:
            errors.append(f"[BPMN 0101] Flow '{fid}' has invalid source: '{source}' not found.")
        if target not in valid_ids:
            errors.append(f"[BPMN 0102] Flow '{fid}' has invalid target: '{target}' not found.")
        if flow.get("type") == "sequenceFlow":
            src_pool = get_pool(elements, source)
            tgt_pool = get_pool(elements, target)
            if src_pool != tgt_pool:
                errors.append(f"[BPMN 0202] Sequence flow '{fid}' crosses pool boundary.")

    # 3. Event Validation
    errors += validate_events(events, incoming, outgoing)

    # 4. Activity Validation
    errors += validate_activities(activities, incoming, outgoing)

    # 5. Gateway Validation
    errors += validate_gateways(gateways, incoming, outgoing, events)

    # 6. Orphan node
    errors += validate_orphan_nodes(activities, events, gateways, incoming, outgoing)

    # 7. Pool/lane validation
    warnings += validate_pool_lane(activities + events + gateways)

    # 8. Message flow validation
    msg_errors, msg_warnings = validate_message_flows(message_flows, elements)
    errors += msg_errors
    warnings += msg_warnings

    # 9. Boundary event matching
    boundary_errors, boundary_warnings = validate_boundary_event_matching(events)
    errors += boundary_errors
    warnings += boundary_warnings

    # 10. Event label validation
    label_warnings = validate_event_labels(events)
    warnings += label_warnings

    # 11. Conditional sequence flow validation
    # Note: This function is commented out in the original code, so we will not call
    cond_errors = validate_conditional_sequence_flows(flows, gateways, events, activities)
    errors += cond_errors

    # 12. Gateway label validation
    gateway_label_warnings = validate_gateway_labels(gateways, flows)
    warnings += gateway_label_warnings


    connected_nodes = len(set(incoming.keys()) | set(outgoing.keys()))
    total_nodes = len(activities) + len(events) + len(gateways)
    conn_pct = (connected_nodes / total_nodes * 100) if total_nodes > 0 else 0
    print(f"📊 Graph connectivity: {conn_pct:.2f}% of nodes are connected.\n")

    message_flows = elements.get("message_flows", [])

    # 9. Report
    if warnings:
        for w in warnings:
            print("⚠️", w)
    if errors:
        print("❌ BPMN semantic rule violations found:")
        for e in errors:
            print("❌", e)
        print(f"❌ Total {len(errors)} violations.\n")
        if strict:
            raise ValueError(f"{len(errors)} BPMN semantic violations found.")
    else:
        print("✅ All BPMN semantic rules are satisfied.\n")


def validate_events(events, incoming, outgoing):
    errors = []
    start_count = 0
    for event in events:
        eid = event.get("id")
        etype = event.get("event_type", "")
        trigger = event.get("trigger", None)
        is_catch = event.get("catching", True)

        # BPMN 0105
        if etype == "startEvent":
            start_count += 1
            if eid in incoming:
                errors.append(f"[BPMN 0105] Start event '{eid}' must not have incoming flow.")
            if trigger == "Error":
                errors.append(f"[BPMN 0109] Start event '{eid}' cannot have Error trigger.")
            if trigger and not trigger.startswith("Message") and "message" in event:
                errors.append(f"[BPMN 0107] Message Start event '{eid}' must have Message trigger.")
        elif etype == "endEvent":
            if eid in outgoing:
                errors.append(f"[BPMN 0124] End event '{eid}' must not have outgoing flow.")
        elif etype == "intermediateThrowEvent":
            if eid not in outgoing:
                errors.append(f"[BPMN 0114] Throwing intermediate event '{eid}' has no outgoing flow.")
            if trigger not in ["Message", "Signal", "Escalation", "Link", "Compensation"]:
                errors.append(f"[BPMN 01151] Invalid trigger '{trigger}' for throwing intermediate event '{eid}'.")
        elif etype == "intermediateCatchEvent":
            if eid not in incoming:
                errors.append(f"[BPMN 0113] Catching intermediate event '{eid}' has no incoming flow.")
            if trigger not in ["Message", "Signal", "Timer", "Link", "Conditional"]:
                errors.append(f"[BPMN 01161] Invalid trigger '{trigger}' for catching intermediate event '{eid}'.")
        elif etype == "boundaryEvent":
            if eid not in outgoing:
                errors.append(f"[BPMN 0112] Boundary event '{eid}' has no outgoing flow.")
            if eid in incoming:
                errors.append(f"[BPMN 01123] Boundary event '{eid}' must not have incoming flow.")
            if trigger not in ["Message", "Timer", "Signal", "Error", "Escalation", "Conditional", "Cancel", "Compensation"]:
                errors.append(f"[BPMN 01122] Invalid trigger '{trigger}' for boundary event '{eid}'.")
    if start_count > 1:
        errors.append(f"[Style 01106] Only one start event allowed in subprocess.")
    return errors

def validate_activities(activities, incoming, outgoing):
    errors = []
    seen_names = set()

    for task in activities:
        tid = task.get("id")
        tname = task.get("name", "").strip()

        # BPMN 0101 - Incoming
        if tid not in incoming:
            errors.append(f"[BPMN 0101] Task '{tname or tid}' has no incoming flow.")

        # BPMN 0102 - Outgoing
        if tid not in outgoing:
            errors.append(f"[BPMN 0102] Task '{tname or tid}' has no outgoing flow.")

        # Style 0103 - Label presence
        if not tname:
            errors.append(f"[Style 0103] Task '{tid}' should have a label.")

        # Style 0104 - Unique name
        if tname and tname in seen_names:
            errors.append(f"[Style 0104] Duplicate task name: '{tname}'.")
        seen_names.add(tname)

    return errors


def validate_gateways(gateways, incoming, outgoing, events):
    errors = []

    for gw in gateways:
        gid = gw.get("id")
        gtype = gw.get("gateway_type")

        in_count = len(incoming.get(gid, []))
        out_count = len(outgoing.get(gid, []))

        # BPMN 0132 & 0133 — tidak boleh ada message flow (asumsikan tidak tersedia di JSON kamu)
        if gtype in ["exclusiveGateway", "inclusiveGateway"]:
            if out_count < 2:
                errors.append(f"[BPMN 0134] Gateway '{gid}' of type {gtype} should have at least 2 outgoing flows.")

        elif gtype == "parallelGateway":
            if in_count < 2 and out_count < 2:
                errors.append(f"[BPMN 0134] Parallel gateway '{gid}' should have at least 2 incoming or 2 outgoing flows.")

        elif gtype == "eventBasedGateway":
            for target_id in outgoing.get(gid, []):
                is_valid = any(
                    e.get("id") == target_id and e.get("event_type") == "intermediateCatchEvent"
                    for e in events
                )
                if not is_valid:
                    errors.append(f"[BPMN 0138] Event-based gateway '{gid}' must connect to an intermediateCatchEvent.")

    return errors


def validate_orphan_nodes(activities, events, gateways, incoming, outgoing):
    errors = []
    all_nodes = activities + events + gateways

    for node in all_nodes:
        nid = node.get("id")
        ntype = node.get("type", node.get("event_type", "unknown"))

        if nid not in incoming and nid not in outgoing:
            errors.append(f"[Style] Node '{nid}' ({ntype}) is orphaned — no incoming or outgoing flow.")
    
    return errors


def validate_pool_lane(nodes):
    warnings = []

    for node in nodes:
        nid = node.get("id", "<unknown>")
        ntype = node.get("type", node.get("event_type", "unknown"))

        if node.get("pool_id") is None:
            warnings.append(f"[Style] Node '{nid}' ({ntype}) is not assigned to any pool.")
        if node.get("lane_id") is None:
            warnings.append(f"[Style] Node '{nid}' ({ntype}) is not assigned to any lane.")

    return warnings

def get_pool(elements, node_id):
    for node in elements.get("activities", []) + elements.get("events", []) + elements.get("gateways", []):
        if node.get("id") == node_id:
            return node.get("pool_id")
    return None


def validate_message_flows(message_flows, elements):
    errors = []
    warnings = []

    activities = elements.get("activities", [])
    events = elements.get("events", [])
    gateways = elements.get("gateways", [])

    nodes = {n["id"]: n for n in activities + events + gateways}

    for mf in message_flows:
        mid = mf.get("id")
        source = mf.get("source")
        target = mf.get("target")
        label = mf.get("label", "").strip()

        src_node = nodes.get(source)
        tgt_node = nodes.get(target)

        if not src_node:
            errors.append(f"[BPMN 0302] Message flow '{mid}' has invalid source '{source}'.")
            continue
        if not tgt_node:
            errors.append(f"[BPMN 0303] Message flow '{mid}' has invalid target '{target}'.")
            continue

        src_type = src_node.get("type", src_node.get("event_type", "unknown"))
        tgt_type = tgt_node.get("type", tgt_node.get("event_type", "unknown"))
        src_pool = src_node.get("pool_id")
        tgt_pool = tgt_node.get("pool_id")

        # BPMN 0301 — tidak boleh antar node dalam pool yang sama
        if src_pool is not None and src_pool == tgt_pool:
            errors.append(f"[BPMN 0301] Message flow '{mid}' connects nodes in the same pool '{src_pool}'.")

        # BPMN 0302 — validasi sumber message flow
        if src_type not in ["endEvent", "intermediateThrowEvent", "sendTask", "userTask", "serviceTask", "subProcess"]:
            errors.append(f"[BPMN 0302] Invalid source type '{src_type}' for message flow '{mid}'.")

        # BPMN 0303 — validasi tujuan message flow
        if tgt_type not in ["startEvent", "intermediateCatchEvent", "receiveTask", "userTask", "serviceTask", "subProcess"]:
            errors.append(f"[BPMN 0303] Invalid target type '{tgt_type}' for message flow '{mid}'.")

        # Style 0304 — Message flow harus diberi label
        if not label:
            warnings.append(f"[Style 0304] Message flow '{mid}' should be labeled with the message name.")

    return errors, warnings

def validate_boundary_event_matching(events):
    errors = []
    warnings = []

    boundary_events = [e for e in events if e.get("event_type") == "boundaryEvent"]
    throw_events = [e for e in events if e.get("event_type") in ["endEvent", "intermediateThrowEvent"]]

    # Index throw events by type and ref (e.g., error_ref)
    error_throws = {e.get("error_ref"): e for e in throw_events if e.get("trigger") == "Error"}
    escalation_throws = {e.get("escalation_ref"): e for e in throw_events if e.get("trigger") == "Escalation"}

    for be in boundary_events:
        bid = be.get("id")
        trigger = be.get("trigger")
        ref = be.get("error_ref") if trigger == "Error" else be.get("escalation_ref")

        # BPMN 01124 and 01127
        if trigger == "Error":
            if ref not in error_throws:
                errors.append(f"[BPMN 01124] Error boundary event '{bid}' has no matching error throw event for ref '{ref}'.")
            else:
                # Style 01125
                tlabel = error_throws[ref].get("label", "")
                blabel = be.get("label", "")
                if tlabel and blabel and tlabel != blabel:
                    warnings.append(f"[Style 01125] Error boundary event '{bid}' label '{blabel}' does not match throw event label '{tlabel}'.")
        elif trigger == "Escalation":
            if ref not in escalation_throws:
                errors.append(f"[BPMN 01127] Escalation boundary event '{bid}' has no matching escalation throw event for ref '{ref}'.")
            else:
                # Style 01128
                tlabel = escalation_throws[ref].get("label", "")
                blabel = be.get("label", "")
                if tlabel and blabel and tlabel != blabel:
                    warnings.append(f"[Style 01128] Escalation boundary event '{bid}' label '{blabel}' does not match throw event label '{tlabel}'.")

    return errors, warnings


def validate_event_labels(events):
    warnings = []

    for event in events:
        eid = event.get("id")
        etype = event.get("event_type")
        trigger = event.get("trigger", "")  # optional
        label = event.get("label", event.get("name", "")).strip()
        is_top_level = not event.get("parent_id")  # diasumsikan jika tidak ada parent_id, maka top-level

        # Style 01105 — Start event di top-level process harus punya label
        if etype == "startEvent" and is_top_level and not label:
            warnings.append(f"[Style 01105] Start event '{eid}' in top-level process should be labeled.")

        # Style 01101 — Message start event: label diawali "Receive ...", hanya jika ada trigger
        if etype == "startEvent" and trigger == "Message":
            if not label.lower().startswith("receive"):
                warnings.append(f"[Style 01101] Message start event '{eid}' should be labeled 'Receive [message name]'.")

        # Style 01102–01104 — Timer, Signal, Conditional start event
        if etype == "startEvent" and trigger in ["Timer", "Signal", "Conditional"]:
            if not label:
                msg = {
                    "Timer": "indicate the process schedule",
                    "Signal": "indicate the Signal name",
                    "Conditional": "indicate the condition"
                }
                rule_suffix = {"Timer": "02", "Signal": "03", "Conditional": "04"}[trigger]
                warnings.append(f"[Style 0110{rule_suffix}] {trigger} start event '{eid}' should be labeled to {msg[trigger]}.")

        # Style 0115 — Throwing intermediate
        if etype == "intermediateThrowEvent" and not label:
            warnings.append(f"[Style 0115] Throwing intermediate event '{eid}' should be labeled.")

        # Style 01161 — Catching intermediate
        if etype == "intermediateCatchEvent" and not label:
            warnings.append(f"[Style 01161] Catching intermediate event '{eid}' should be labeled.")

        # Style 0129 — End event
        if etype == "endEvent" and not label:
            warnings.append(f"[Style 0129] End event '{eid}' should be labeled with the name of the end state.")

    return warnings

def validate_conditional_sequence_flows(flows, gateways, events, activities):
    errors = []

    # Buat lookup untuk tipe node berdasarkan ID
    node_type = {}
    for a in activities:
        node_type[a["id"]] = a.get("type", "activity")
    for e in events:
        node_type[e["id"]] = e.get("event_type", "event")
    for g in gateways:
        node_type[g["id"]] = g.get("gateway_type", "gateway")

    # Buat mapping: node_id → jumlah outgoing
    outgoing_map = {}
    for flow in flows:
        source = flow.get("source")
        outgoing_map.setdefault(source, []).append(flow)

    for flow in flows:
        source = flow.get("source")
        fid = flow.get("id")
        condition = flow.get("condition_expression")
        source_type = node_type.get(source)

        # BPMN 0203: Tidak boleh pakai condition jika hanya 1 outgoing
        if condition and len(outgoing_map.get(source, [])) == 1:
            errors.append(f"[BPMN 0203] Flow '{fid}' has condition but source node '{source}' has only one outgoing flow.")

        # BPMN 0204: Tidak boleh pakai condition dari parallel gateway
        if condition and source_type == "parallelGateway":
            errors.append(f"[BPMN 0204] Flow '{fid}' from parallel gateway '{source}' must not have condition.")

    return errors

def validate_gateway_labels(gateways, flows):
    warnings = []

    # Buat mapping id gateway → flow keluar
    outgoing_map = {}
    for flow in flows:
        source = flow.get("source")
        outgoing_map.setdefault(source, []).append(flow)

    for gw in gateways:
        gid = gw.get("id")
        gtype = gw.get("gateway_type", "")
        if gtype not in ["exclusiveGateway", "inclusiveGateway", "eventBasedGateway"]:
            continue  # hanya gateway jenis ini yang berlaku

        outgoing = outgoing_map.get(gid, [])
        if not outgoing:
            continue

        unlabeled = [f for f in outgoing if not f.get("name", "").strip()]
        if len(unlabeled) > 1:
            warnings.append(f"[Style 0135] Gateway '{gid}' ({gtype}) has multiple unlabeled outgoing gates.")
        elif len(unlabeled) == 1:
            warnings.append(f"[Style 0136] Gateway '{gid}' has an unlabeled gate. Consider labeling it explicitly.")

    return warnings
