from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

SESSIONS_DIR = "/app/sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)


def get_session_path(profile_key):
    safe_name = "".join(c for c in profile_key if c.isalnum() or c in ("_", "-"))
    return SESSIONS_DIR + "/" + safe_name + ".json"


def get_meta_path(profile_key):
    safe_name = "".join(c for c in profile_key if c.isalnum() or c in ("_", "-"))
    return SESSIONS_DIR + "/" + safe_name + "_meta.json"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "session-manager"})


@app.route("/profiles", methods=["GET"])
def list_profiles():
    files = os.listdir(SESSIONS_DIR)
    profiles = []
    for f in files:
        if f.endswith(".json") and not f.endswith("_meta.json"):
            profiles.append(f.replace(".json", ""))
    return jsonify({"profiles": profiles})


@app.route("/session/<profile_key>", methods=["GET"])
def get_session(profile_key):
    session_path = get_session_path(profile_key)
    meta_path = get_meta_path(profile_key)

    if not os.path.exists(session_path):
        return jsonify({"error": "Profile not found", "profile_key": profile_key}), 404

    with open(session_path, "r") as f:
        storage_state = json.load(f)

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return jsonify({
        "status": "found",
        "profile_key": profile_key,
        "session_path": session_path,
        "storage_state": storage_state,
        "meta": meta
    })


@app.route("/session/<profile_key>", methods=["POST"])
def save_session(profile_key):
    data = request.json
    storage_state = data.get("storage_state")
    platform = data.get("platform", "unknown")
    account_name = data.get("account_name", profile_key)

    if not storage_state:
        return jsonify({"error": "storage_state is required"}), 400

    session_path = get_session_path(profile_key)
    meta_path = get_meta_path(profile_key)

    with open(session_path, "w") as f:
        json.dump(storage_state, f)

    meta = {
        "profile_key": profile_key,
        "platform": platform,
        "account_name": account_name,
        "last_updated": datetime.now().isoformat(),
        "status": "active"
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f)

    return jsonify({
        "status": "success",
        "profile_key": profile_key,
        "session_path": session_path,
        "meta": meta
    })


@app.route("/session/<profile_key>", methods=["DELETE"])
def delete_session(profile_key):
    session_path = get_session_path(profile_key)
    meta_path = get_meta_path(profile_key)

    deleted = False
    if os.path.exists(session_path):
        os.remove(session_path)
        deleted = True
    if os.path.exists(meta_path):
        os.remove(meta_path)

    if not deleted:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify({"status": "deleted", "profile_key": profile_key})


@app.route("/session/<profile_key>/mark_expired", methods=["POST"])
def mark_expired(profile_key):
    meta_path = get_meta_path(profile_key)
    if not os.path.exists(meta_path):
        return jsonify({"error": "Profile metadata not found"}), 404

    with open(meta_path, "r") as f:
        meta = json.load(f)

    meta["status"] = "expired"
    meta["expired_at"] = datetime.now().isoformat()

    with open(meta_path, "w") as f:
        json.dump(meta, f)

    return jsonify({"status": "marked_expired", "profile_key": profile_key, "meta": meta})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8767)
