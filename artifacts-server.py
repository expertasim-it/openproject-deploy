from flask import Flask, request, jsonify, send_file
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)

BASE_DIR = "/app/artifacts"
SCREENSHOTS_DIR = BASE_DIR + "/screenshots"
TRACES_DIR = BASE_DIR + "/traces"
EXTRACTIONS_DIR = BASE_DIR + "/extractions"
RUNS_DIR = BASE_DIR + "/runs"

for d in [SCREENSHOTS_DIR, TRACES_DIR, EXTRACTIONS_DIR, RUNS_DIR]:
    os.makedirs(d, exist_ok=True)


def safe_name(value):
    return "".join(c for c in str(value) if c.isalnum() or c in ("_", "-"))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "artifacts-manager"})


@app.route("/run/start", methods=["POST"])
def start_run():
    data = request.json
    target_key = data.get("target_key", "unknown")
    workflow_type = data.get("workflow_type", "unknown")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + safe_name(target_key)

    run_meta = {
        "run_id": run_id,
        "target_key": target_key,
        "workflow_type": workflow_type,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "screenshots": [],
        "extraction": None,
        "trace": None
    }

    run_path = RUNS_DIR + "/" + run_id + ".json"
    with open(run_path, "w") as f:
        json.dump(run_meta, f, indent=2)

    return jsonify({"status": "started", "run_id": run_id, "run_meta": run_meta})


@app.route("/run/<run_id>/screenshot", methods=["POST"])
def save_screenshot(run_id):
    data = request.json
    image_base64 = data.get("image_base64")
    checkpoint = data.get("checkpoint", "unnamed")

    if not image_base64:
        return jsonify({"error": "image_base64 is required"}), 400

    filename = run_id + "_" + safe_name(checkpoint) + ".png"
    filepath = SCREENSHOTS_DIR + "/" + filename

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_base64))

    run_path = RUNS_DIR + "/" + run_id + ".json"
    if os.path.exists(run_path):
        with open(run_path, "r") as f:
            run_meta = json.load(f)
        run_meta["screenshots"].append({
            "checkpoint": checkpoint,
            "filename": filename,
            "path": filepath,
            "saved_at": datetime.now().isoformat()
        })
        with open(run_path, "w") as f:
            json.dump(run_meta, f, indent=2)

    return jsonify({"status": "success", "filename": filename, "path": filepath})


@app.route("/run/<run_id>/extraction", methods=["POST"])
def save_extraction(run_id):
    data = request.json
    extraction_payload = data.get("payload")

    if extraction_payload is None:
        return jsonify({"error": "payload is required"}), 400

    filename = run_id + "_extraction.json"
    filepath = EXTRACTIONS_DIR + "/" + filename

    with open(filepath, "w") as f:
        json.dump(extraction_payload, f, indent=2)

    run_path = RUNS_DIR + "/" + run_id + ".json"
    if os.path.exists(run_path):
        with open(run_path, "r") as f:
            run_meta = json.load(f)
        run_meta["extraction"] = {"filename": filename, "path": filepath}
        with open(run_path, "w") as f:
            json.dump(run_meta, f, indent=2)

    return jsonify({"status": "success", "filename": filename, "path": filepath})


@app.route("/run/<run_id>/trace", methods=["POST"])
def save_trace(run_id):
    data = request.json
    trace_base64 = data.get("trace_base64")

    if not trace_base64:
        return jsonify({"error": "trace_base64 is required"}), 400

    filename = run_id + "_trace.zip"
    filepath = TRACES_DIR + "/" + filename

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(trace_base64))

    run_path = RUNS_DIR + "/" + run_id + ".json"
    if os.path.exists(run_path):
        with open(run_path, "r") as f:
            run_meta = json.load(f)
        run_meta["trace"] = {"filename": filename, "path": filepath}
        with open(run_path, "w") as f:
            json.dump(run_meta, f, indent=2)

    return jsonify({"status": "success", "filename": filename, "path": filepath})


@app.route("/run/<run_id>/finish", methods=["POST"])
def finish_run(run_id):
    data = request.json
    final_status = data.get("status", "completed")

    run_path = RUNS_DIR + "/" + run_id + ".json"
    if not os.path.exists(run_path):
        return jsonify({"error": "Run not found"}), 404

    with open(run_path, "r") as f:
        run_meta = json.load(f)

    run_meta["status"] = final_status
    run_meta["finished_at"] = datetime.now().isoformat()

    with open(run_path, "w") as f:
        json.dump(run_meta, f, indent=2)

    return jsonify({"status": "success", "run_meta": run_meta})


@app.route("/run/<run_id>", methods=["GET"])
def get_run(run_id):
    run_path = RUNS_DIR + "/" + run_id + ".json"
    if not os.path.exists(run_path):
        return jsonify({"error": "Run not found"}), 404

    with open(run_path, "r") as f:
        run_meta = json.load(f)

    return jsonify(run_meta)


@app.route("/runs", methods=["GET"])
def list_runs():
    files = os.listdir(RUNS_DIR)
    run_ids = [f.replace(".json", "") for f in files if f.endswith(".json")]
    return jsonify({"runs": run_ids})


@app.route("/download/screenshot/<filename>", methods=["GET"])
def download_screenshot(filename):
    filepath = SCREENSHOTS_DIR + "/" + filename
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath)


@app.route("/download/trace/<filename>", methods=["GET"])
def download_trace(filename):
    filepath = TRACES_DIR + "/" + filename
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8768)
