from quart import Quart, jsonify
import json
from pathlib import Path

app = Quart(__name__)

@app.route("/meta")
async def meta():
    meta_path = Path("mms/meta.json")
    if meta_path.exists():
        with open(meta_path) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "meta.json not found"}), 404

if __name__ == "__main__":
    app.run(port=8888, host="0.0.0.0")