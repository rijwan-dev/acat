from flask import Blueprint, render_template, request, jsonify

import requests
import json

from .services.ocr import extract_document_text, extract_fields
from .services.ai import analyze_document

main = Blueprint("main", __name__)
url = "http://192.168.0.118:11500/api/chat"

json_schema = """
You are to output ONLY valid JSON.
Do not include explanations, comments, or extra text.
The JSON must follow this structure:

{
  "serial_no": "",
  "aadhaar_no": "",
  "enrolment_no": "",
  "roll_no": "",
  "board": "",
  "certification": "",
  "exam": "",
  "certificate_type": "",
  "student": {
    "name": "",
    "father_name": "",
    "mother_name": "",
    "date_of_birth": "",
    "school": ""
  },
  "exam_details": {
    "month_year": "",
    "location": ""
  },
  "marks": [
    {
      "subject": "",
      "marks_obtained": 0,
      "minimum_pass_marks": 0,
      "maximum_marks": 0,
      "grade": "",
      "grade_point": 0
    }
  ],
  "total_marks_obtained": 0,
  "total_maximum_marks": 0,
  "gpa": 0.0,
  "general_awareness_life_skills_grade": "",
  "co_curricular_activity_grade": "",
  "date_issued": "",
  "date_dated": ""
}
"""

@main.route("/")
def index():
    return render_template("index.html")

def parse_document(text):
    payload = {
        "model": "llama3.1",
        "messages": [
            {"role": "system", "content": json_schema},
            {"role": "user", "content": text}
        ],
        "stream": False
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    output = result.get("message", {}).get("content", "").strip()
    print("response:")
    print(output)
    if output.startswith("```"):
        output = output.strip("`")
        output = output.replace("json", "").strip()
    final = json.loads(output)
    print("json output:")
    print("final")
    return json.loads(output)

@main.route("/api/scan", methods=["POST"])
def scan_document():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file uploaded"}), 400
    text = extract_document_text(f)
    parsed = parse_document(text)
    return jsonify(parsed)

