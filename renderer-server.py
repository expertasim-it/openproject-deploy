from flask import Flask, request, jsonify, send_file
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

OUTPUTS_DIR = "/app/outputs"
INPUTS_DIR = "/app/inputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "svg-renderer", "engine": "inkscape"})

@app.route("/render", methods=["POST"])
def render():
    data = request.json
    svg_content = data.get("svg_content")
    svg_path = data.get("svg_path")
    output_format = data.get("format", "png").lower()
    width = data.get("width")
    height = data.get("height")

    if not svg_content and not svg_path:
        return jsonify({"error": "Provide either svg_content or svg_path"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if svg_content and not svg_path:
        temp_svg_path = f"{INPUTS_DIR}/temp_{timestamp}.svg"
        with open(temp_svg_path, "w") as f:
            f.write(svg_content)
        svg_path = temp_svg_path

    if not os.path.exists(svg_path):
        return jsonify({"error": f"File not found: {svg_path}"}), 404

    if output_format not in ["png", "pdf"]:
        return jsonify({"error": "Format must be 'png' or 'pdf'"}), 400

    output_filename = f"render_{timestamp}.{output_format}"
    output_path = f"{OUTPUTS_DIR}/{output_filename}"

    cmd = ["inkscape", svg_path, f"--export-filename={output_path}"]

    if output_format == "png":
        cmd.append("--export-type=png")
        if width:
            cmd.append(f"--export-width={width}")
        if height:
            cmd.append(f"--export-height={height}")
    elif output_format == "pdf":
