from flask import Flask, request, jsonify
import os
import re
import json
from datetime import datetime
from lxml import etree

app = Flask(__name__)

TEMPLATES_DIR = "/app/templates"
OUTPUTS_DIR = "/app/outputs"

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Create sample templates on startup
def create_sample_templates():
    social_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
  <rect width="1080" height="1080" fill="{{BACKGROUND_COLOR}}"/>
  <rect x="40" y="40" width="1000" height="1000" fill="none" stroke="{{ACCENT_COLOR}}" stroke-width="4"/>
  <text x="540" y="200" font-family="Arial, sans-serif" font-size="72" font-weight="bold" 
        fill="{{TEXT_COLOR}}" text-anchor="middle">{{HEADLINE}}</text>
  <text x="540" y="320" font-family="Arial, sans-serif" font-size="42" 
        fill="{{TEXT_COLOR}}" text-anchor="middle">{{SUBHEAD}}</text>
  <rect x="340" y="800" width="400" height="80" rx="40" fill="{{ACCENT_COLOR}}"/>
  <text x="540" y="852" font-family="Arial, sans-serif" font-size="36" font-weight="bold"
        fill="{{BACKGROUND_COLOR}}" text-anchor="middle">{{CTA}}</text>
  <text x="540" y="980" font-family="Arial, sans-serif" font-size="28"
        fill="{{TEXT_COLOR}}" text-anchor="middle" opacity="0.7">{{DATE}}</text>
</svg>'''

    banner_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="628" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="628" fill="{{BACKGROUND_COLOR}}"/>
  <text x="600" y="250" font-family="Arial, sans-serif" font-size="80" font-weight="bold"
        fill="{{TEXT_COLOR}}" text-anchor="middle">{{HEADLINE}}</text>
  <text x="600" y="350" font-family="Arial, sans-serif" font-size="48"
        fill="{{TEXT_COLOR}}" text-anchor="middle">{{SUBHEAD}}</text>
  <rect x="450" y="430" width="300" height="70" rx="35" fill="{{ACCENT_COLOR}}"/>
  <text x="600" y="477" font-family="Arial, sans-serif" font-size="32" font-weight="bold"
        fill="{{BACKGROUND_COLOR}}" text-anchor="middle">{{CTA}}</text>
  <text x="600" y="590" font-family="Arial, sans-serif" font-size="24"
        fill="{{TEXT_COLOR}}" text-anchor="middle" opacity="0.7">{{DATE}}</text>
</svg>'''

    with open(f"{TEMPLATES_DIR}/social-post.svg", "w") as f:
        f.write(social_template)
    with open(f"{TEMPLATES_DIR}/banner.svg", "w") as f:
        f.write(banner_template)

create_sample_templates()

def replace_placeholders(svg_content, variables):
    for key, value in variables.items():
        placeholder = "{{" + key.upper() + "}}"
        svg_content = svg_content.replace(placeholder, str(value))
    return svg_content

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "svg-templater"})

@app.route("/templates", methods=["GET"])
def list_templates():
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".svg")]
    return jsonify({"templates": templates})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    template_id = data.get("template_id", "social-post")
    variables = data.get("variables", {})

    if "date" not in variables:
        variables["date"] = datetime.now().strftime("%B %d, %Y")
    if "background_color" not in variables:
        variables["background_color"] = "#1a1a2e"
    if "text_color" not in variables:
        variables["text_color"] = "#ffffff"
    if "accent_color" not in variables:
        variables["accent_color"] = "#e94560"

    template_path = f"{TEMPLATES_DIR}/{template_id}.svg"
    if not os.path.exists(template_path):
        return jsonify({"error": f"Template '{template_id}' not found"}), 404

    with open(template_path, "r") as f:
        svg_content = f.read()

    populated_svg = replace_placeholders(svg_content, variables)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{template_id}_{timestamp}.svg"
    output_path = f"{OUTPUTS_DIR}/{output_filename}"

    with open(output_path, "w") as f:
        f.write(populated_svg)

    return jsonify({
        "status": "success",
        "output_file": output_filename,
        "output_path": output_path,
        "template_used": template_id,
        "variables_applied": variables
    })

@app.route("/outputs", methods=["GET"])
def list_outputs():
    outputs = [f for f in os.listdir(OUTPUTS_DIR) if f.endswith(".svg")]
    return jsonify({"outputs": outputs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765)
