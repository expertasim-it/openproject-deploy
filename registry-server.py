from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

TARGETS_DIR = "/app/targets"
os.makedirs(TARGETS_DIR, exist_ok=True)


def safe_name(value):
    return "".join(c for c in str(value) if c.isalnum() or c in ("_", "-"))


def get_target_path(target_key):
    return TARGETS_DIR + "/" + safe_name(target_key) + ".json"


def create_sample_targets():
    sample = {
        "target_key": "facebook_page1_post",
        "platform": "facebook",
        "task_type": "post",
        "canonical_url": "https://facebook.com/groups/example",
        "profile_key": "facebook_page1",
        "selectors": {
            "compose_button": "[aria-label='Create a post']",
            "text_input": "[role='textbox']",
            "media_upload_button": "[aria-label='Photo/video']",
            "submit_button": "[aria-label='Post']"
        },
        "wait_rules": {
            "after_open_ms": 2000,
            "after_fill_ms": 500,
            "after_submit_ms": 3000
        },
        "extraction_schema": None,
        "flags": {
            "approve_first": True,
            "requires_media": False
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    path = get_target_path(sample["target_key"])
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(sample, f, indent=2)


create_sample_targets()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "target-registry"})


@app.route("/targets", methods=["GET"])
def list_targets():
    files = os.listdir(TARGETS_DIR)
    targets = [f.replace(".json", "") for f in files if f.endswith(".json")]
    return jsonify({"targets": targets})


@app.route("/target/<target_key>", methods=["GET"])
def get_target(target_key):
    path = get_target_path(target_key)
    if not os.path.exists(path):
        return jsonify({"error": "Target not found", "target_key": target_key}), 404

    with open(path, "r") as f:
        config = json.load(f)

    return jsonify({"status": "found", "config": config})


@app.route("/target/<target_key>", methods=["POST"])
def save_target(target_key):
    data = request.json

    required_fields = ["platform", "task_type", "canonical_url", "profile_key"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 400

    path = get_target_path(target_key)

    existing_created_at = datetime.now().isoformat()
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = json.load(f)
        existing_created_at = existing.get("created_at", existing_created_at)

    config = {
        "target_key": target_key,
        "platform": data.get("platform"),
        "task_type": data.get("task_type"),
        "canonical_url": data.get("canonical_url"),
        "profile_key": data.get("profile_key"),
        "selectors": data.get("selectors", {}),
        "wait_rules": data.get("wait_rules", {}),
        "extraction_schema": data.get("extraction_schema"),
        "flags": data.get("flags", {}),
        "created_at": existing_created_at,
        "updated_at": datetime.now().isoformat()
    }

    with open(path, "w") as f:
        json.dump(config, f, indent=2)

    return jsonify({"status": "success", "target_key": target_key, "config": config})


@app.route("/target/<target_key>", methods=["DELETE"])
def delete_target(target_key):
    path = get_target_path(target_key)
    if not os.path.exists(path):
        return jsonify({"error": "Target not found"}), 404

    os.remove(path)
    return jsonify({"status": "deleted", "target_key": target_key})


@app.route("/targets/by_platform/<platform>", methods=["GET"])
def get_targets_by_platform(platform):
    files = os.listdir(TARGETS_DIR)
    matches = []
    for f in files:
        if f.endswith(".json"):
            with open(TARGETS_DIR + "/" + f, "r") as fh:
                config = json.load(fh)
            if config.get("platform") == platform:
                matches.append(config)
    return jsonify({"platform": platform, "targets": matches})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8769)
