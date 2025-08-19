import json
import jsonschema
from jsonschema import validate
import uuid
import copy
import os

def validate_schema(data, schema_path=None, auto_fix=False):
    # ✅ Hitung path absolut berdasarkan lokasi file ini
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), "bpmn_schema.json")

    # Pastikan elemen 'elements' ada
    if "elements" not in data:
        print("❌ The 'elements' property is missing. This is required in BPMN structure.")
        data["elements"] = {}

    # Pastikan minimal struktur utama ada
    for key in ["activities", "events", "flows"]:
        if key not in data["elements"]:
            print(f"⚠️ Warning: The element '{key}' is missing. This does not comply with standard BPMN structure.")
            data["elements"][key] = []

    # Deteksi & Perbaiki ID Duplikat
    if auto_fix:
        fix_missing_ids(data)
        fix_duplicate_ids(data)

    else:
        duplicates = check_duplicate_ids(data)
        if duplicates:
            print(f"❌ Duplicate IDs found: {duplicates}")

    # Deteksi siklus di flow
    flows = data["elements"].get("flows", [])
    if detect_cycle(flows):
        print("⚠️ Warning: Circular reference detected in sequence flows.")
    else:
        print("✅ No circular dependencies in sequence flows.")

    # Validasi terhadap schema JSON
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
        print("✅ JSON structure is valid against the schema.")
        return data
    except jsonschema.exceptions.ValidationError as err:
        print("❌ Invalid structure:", err.message)
        if auto_fix:
            print("🛠️  Attempting to fix the JSON structure...")
            fixed_data = auto_fix_schema(data, schema)
            try:
                validate(instance=fixed_data, schema=schema)
                print("✅ JSON structure has been fixed successfully.")
                return fixed_data
            except jsonschema.exceptions.ValidationError as err2:
                print("❌ Structure fixing failed:", err2.message)
                return fixed_data  # tetap kembalikan hasil perbaikan meskipun belum 100% valid
        else:
            return data

# 🔁 Periksa duplikat ID
def check_duplicate_ids(data):
    id_set = set()
    duplicates = []

    for category in ["activities", "events", "gateways"]:
        for item in data["elements"].get(category, []):
            iid = item.get("id")
            if iid:
                if iid in id_set:
                    duplicates.append(iid)
                id_set.add(iid)
    return duplicates

# ✅ Perbaiki ID Duplikat dengan Suffix
def fix_duplicate_ids(data):
    print("🛠️  Checking and fixing duplicate IDs...")
    id_count = {}
    for category in ["activities", "events", "gateways"]:
        for item in data["elements"].get(category, []):
            iid = item.get("id")
            if not iid:
                continue
            if iid in id_count:
                id_count[iid] += 1
                new_id = f"{iid}_{id_count[iid]}"
                print(f"⚠️ Duplicate ID '{iid}' found. Renaming to '{new_id}'.")
                item["id"] = new_id
            else:
                id_count[iid] = 0

# ✅ Beri ID Default Jika Tidak Ada
def fix_missing_ids(data):
    print("🛠️  Checking for missing IDs...")
    for category in ["activities", "events", "gateways", "pools", "lanes", "artifacts"]:
        for index, item in enumerate(data["elements"].get(category, [])):
            if "id" not in item or not item["id"]:
                default_id = f"{category[:-1]}_{uuid.uuid4().hex[:6]}"
                print(f"⚠️ Missing ID detected in '{category}'. Assigning ID: {default_id}")
                item["id"] = default_id

# 🧠 Auto-fix berdasarkan JSON schema
def auto_fix_schema(data, schema):
    def fix_object(obj, schema_obj, path="root"):
        if not isinstance(obj, dict):
            return

        required_props = schema_obj.get("required", [])
        properties = schema_obj.get("properties", {})

        # Tambahkan properti wajib yang hilang
        for key in required_props:
            if key not in obj:
                prop_schema = properties.get(key, {})
                default_value = generate_default_value(key, prop_schema, path)
                obj[key] = default_value
                print(f"🛠️ Auto-added missing '{key}' at {path}: {default_value}")

        # Rekursif untuk nested objek
        for key, val in obj.items():
            if key in properties:
                prop_schema = properties[key]
                if isinstance(val, dict) and prop_schema.get("type") == "object":
                    fix_object(val, prop_schema, f"{path}.{key}")
                elif isinstance(val, list) and prop_schema.get("type") == "array":
                    item_schema = prop_schema.get("items", {})
                    for idx, item in enumerate(val):
                        if isinstance(item, dict):
                            fix_object(item, item_schema, f"{path}.{key}[{idx}]")

    def generate_default_value(key, prop_schema, path=""):
        # Aturan penetapan default berbasis schema
        if prop_schema.get("enum"):
            return prop_schema["enum"][0]
        if prop_schema.get("type") == "string":
            if key == "id":
                return f"{path.replace('.', '_')}_{uuid.uuid4().hex[:6]}"
            return f"default_{key}"
        if prop_schema.get("type") == "array":
            return []
        if prop_schema.get("type") == "object":
            return {}
        return None  # fallback

    fixed_data = copy.deepcopy(data)
    fix_object(fixed_data, schema, path="root")
    return fixed_data

# 🔁 Deteksi siklus pada flow
def detect_cycle(flows):
    from collections import defaultdict, deque

    graph = defaultdict(list)
    indegree = defaultdict(int)
    nodes = set()

    for f in flows:
        src = f.get("source")
        tgt = f.get("target")
        if src and tgt:
            graph[src].append(tgt)
            indegree[tgt] += 1
            nodes.update([src, tgt])

    queue = deque([n for n in nodes if indegree[n] == 0])
    visited = 0

    while queue:
        current = queue.popleft()
        visited += 1
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited != len(nodes)
