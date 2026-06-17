from flask import Flask, request, jsonify, send_file
import os
import cairosvg
from datetime import datetime

app = Flask(__name__)

OUTPUTS_DIR = "/app/outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "svg-renderer"})

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

    if svg_path:
        if not os.path.exists(svg_path):
            return jsonify({"error": f"File not found: {svg_path}"}), 404
        with open(svg_path, "r") as f:
            svg_content = f.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"render_{timestamp}.{output_format}"
    output_path = f"{OUTPUTS_DIR}/{output_filename}"

    try:
        if output_format == "png":
            cairosvg.svg2png(
                bytestring=svg_content.encode(),
                write_to=output_path,
                output_width=width,
                output_height=height
            )
        elif output_format == "pdf":
            cairosvg.svg2pdf(
                bytestring=svg_content.encode(),
                write_to=output_path
            )
        else:
            return jsonify({"error": "Format must be 'png' or 'pdf'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "status": "success",
        "output_file": output_filename,
        "output_path": output_path,
        "format": output_format
    })

@app.route("/outputs", methods=["GET"])
def list_outputs():
    outputs = os.listdir(OUTPUTS_DIR)
    return jsonify({"outputs": outputs})

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    file_path = f"{OUTPUTS_DIR}/{filename}"
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8766)
