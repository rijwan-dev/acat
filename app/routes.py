from flask import Blueprint, render_template, request, jsonify, current_app

import requests
import os
import json
import uuid

from werkzeug.utils import secure_filename

from .services.ai import analyze_document
from .services.ocr import extract_document_text, extract_fields

main = Blueprint("main", __name__)
url = "http://172.20.213.4:11500/api/chat"

json_schema = """
You are to output ONLY valid JSON.
Do not include explanations, comments, or extra text.
The JSON must follow this structure:


{
  "University": "",
  "Course": "",
  "Semester": "",
  "Examination": "",
  "Student": {
    "Name": "",
    "RegNo": int,
    "RollNo": int,
    "SerialNo": int,
    "FatherName": "",
    "MotherName": ""
  },
  "Subjects": [
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": null
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": { "Max": int, "Min": int, "Secured": int }
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": null
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": null
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": { "Max": int, "Min": int, "Secured": int }
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": null
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": { "Max": int, "Min": int, "Secured": int }
    },
    {
      "Code": "",
      "Name": "",
      "Theory": { "Max": int, "Min": int, "Secured": int },
      "Practical": null
    }
  ],
  "Result": {
    "Status": "",
    "TotalMarksObtained": int
  },
  "Date": "DD/MM/YYYY",
}
"""

# json_schema = """
# You are to output ONLY valid JSON.
# Do not include explanations, comments, or extra text.
# The JSON must follow this structure:

# {
#   "serial_no": "",
#   "aadhaar_no": "",
#   "enrolment_no": "",
#   "roll_no": "",
#   "board": "",
#   "certification": "",
#   "exam": "",
#   "certificate_type": "",
#   "student": {
#     "name": "",
#     "father_name": "",
#     "mother_name": "",
#     "date_of_birth": "",
#     "school": ""
#   },
#   "exam_details": {
#     "month_year": "",
#     "location": ""
#   },
#   "marks": [
#     {
#       "subject": "",
#       "marks_obtained": 0,
#       "minimum_pass_marks": 0,
#       "maximum_marks": 0,
#       "grade": "",
#       "grade_point": 0
#     }
#   ],
#   "total_marks_obtained": 0,
#   "total_maximum_marks": 0,
#   "gpa": 0.0,
#   "general_awareness_life_skills_grade": "",
#   "co_curricular_activity_grade": "",
#   "date_issued": "",
#   "date_dated": ""
# }
# """

def unique_filename(original_name: str):
    ext = original_name.split(".")[-1]
    return f"{uuid.uuid4().hex}.{ext}"

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
    return json.loads(output)

@main.route("/api/scan", methods=["POST"])
def scan_document():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file uploaded"}), 400
    
    save_path = os.path.join(current_app.config["directory_upload"], f.filename)
    f.seek(0)
    f.save(save_path)

    with open(save_path, "rb") as stored_file:
        text = extract_document_text(stored_file)
    parsed = parse_document(text)
    return jsonify(parsed)

@main.route("/api/upload_doc", methods=["POST"])
def upload_doc():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    safe_original = secure_filename(f.filename)
    new_name = unique_filename(safe_original)
    save_path = os.path.join(current_app.config["directory_upload"], new_name)
    f.save(save_path)

    with open(save_path, "rb") as src:
        text = extract_document_text(src)
    parsed_json = parse_document(text)
    json_path = save_path + ".json"
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(parsed_json, fp, indent=2)

    return jsonify({
        "status": "success",
        "filename": new_name,
        "parsed": parsed_json
    })

@main.route("/api/verify_doc", methods=["POST"])
def verify_doc():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    safe_original = secure_filename(f.filename)
    temp_path = os.path.join(current_app.config["directory_temp"], safe_original)
    f.save(temp_path)

    with open(temp_path, "rb") as src:
        text = extract_document_text(src)
    parsed_json = parse_document(text)
    matches = []
    db_folder = current_app.config["directory_upload"]

    for filename in os.listdir(db_folder):
        if filename.endswith(".json"):
            stored_data = json.load(open(os.path.join(db_folder, filename)))
            if stored_data == parsed_json:
                matches.append(filename)

    return jsonify({
        "verified": len(matches) > 0,
        "matches": matches,
        "parsed": parsed_json
    })

@main.route("/")
def index():
    return render_template("index.html")
    
@main.route("/verify")
def verify():
    return render_template("verify.html")

@main.route("/login")
def login():
    return render_template("login.html")
@main.route("/upload")
def upload():
    return render_template("upload.html")



