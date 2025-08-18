import json
import subprocess
import sys

def load_json(path):
    # 1. Baca file sebagai teks mentah
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ File not found: {path}")

    # 2. Coba parser standar JSON
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"❌ Standard JSON parsing failed: {e}")
        print("🛠️ Attempting to repair using dirtyjson...")

    # 3. dirtyjson
    try:
        import dirtyjson
    except ImportError:
        print("📦 'dirtyjson' not found. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dirtyjson"])
        import dirtyjson

    try:
        repaired = dirtyjson.loads(raw_text)
        print("✅ JSON repaired using dirtyjson.")
        save_fixed_json(repaired, path, method="dirtyjson")
        return repaired
    except Exception as e2:
        print(f"❌ dirtyjson failed: {e2}")
        print("🔁 Trying demjson3...")

    # 4. demjson3
    try:
        import demjson3
    except ImportError:
        print("📦 'demjson3' not found. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "demjson3"])
        import demjson3

    try:
        repaired = demjson3.decode(raw_text)
        print("✅ JSON repaired using demjson3.")
        save_fixed_json(repaired, path, method="demjson3")
        return repaired
    except Exception as e3:
        print(f"❌ demjson3 failed: {e3}")
        print("🧪 Trying manual heuristic repair...")

    # 5. Heuristic repair
    try:
        repaired_text = heuristic_repair(raw_text)
        repaired = json.loads(repaired_text)
        print("✅ JSON repaired using heuristic method.")
        save_fixed_json(repaired, path, method="heuristic")
        return repaired
    except Exception as e4:
        print(f"❌ Heuristic repair failed: {e4}")

    # 6. Fallback terakhir
    print("⚠️ All repair attempts failed. Using minimal fallback structure.")
    return {
        "elements": {
            "activities": [],
            "events": [],
            "flows": [],
            "gateways": []
        }
    }

def heuristic_repair(raw_text):
    lines = raw_text.splitlines()
    repaired = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if i > 0 and ':' in line_stripped and not lines[i - 1].strip().endswith(','):
            if not line_stripped.startswith('}') and not line_stripped.startswith(']'):
                repaired[-1] = repaired[-1] + ','  # tambahkan koma
        repaired.append(line)

    # Tambahkan penutup kurung jika hilang
    repaired_text = '\n'.join(repaired)
    if repaired_text.count('{') > repaired_text.count('}'):
        repaired_text += '\n}'
    if repaired_text.count('[') > repaired_text.count(']'):
        repaired_text += '\n]'

    return repaired_text

def save_fixed_json(data, original_path, method=""):
    fixed_path = original_path.replace(".json", f"_fixed_by_{method}.json")
    try:
        with open(fixed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            print(f"📝 Repaired JSON saved to: {fixed_path}")
    except Exception as e:
        print(f"⚠️ Failed to save repaired JSON: {e}")
