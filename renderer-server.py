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
        temp_svg_path = INPUTS_DIR + "/temp_" + timestamp + ".svg"
        with open(temp_svg_path, "w") as f:
            f.write(svg_content)
        svg_path = temp_svg_path

    if not os.path.exists(svg_path):
        return jsonify({"error": "File not found"}), 404

    if output_format != "png" and output_format != "pdf":
        return jsonify({"error": "Format must be png or pdf"}), 400

    output_filename = "render_" + timestamp + "." + output_format
    output_path = OUTPUTS_DIR + "/" + output_filename

    cmd = ["inkscape", svg_path, "--export-filename=" + output_path]

    if output_format == "png":
        cmd.append("--export-type=png")
        if width:
            cmd.append("--export-width=" + str(width))
        if height:
            cmd.append("--export-height=" + str(height))
    else:
        cmd.append("--export-type=pdf")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return jsonify({"error": "Inkscape render failed", "details": result.stderr}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Render timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not os.path.exists(output_path):
        return jsonify({"error": "Output file was not created"}), 500

    return jsonify({
        "status": "success",
        "output_file": output_filename,
        "output_path": output_path,
        "format": output_format,
        "engine": "inkscape"
    })

@app.route("/outputs", methods=["GET"])
def list_outputs():
    outputs = os.listdir(OUTPUTS_DIR)
    return jsonify({"outputs": outputs})

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    file_path = OUTPUTS_DIR + "/" + filename
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8766)
