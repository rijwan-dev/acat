import requests
import json

url = "http://192.168.0.118:11500/api/chat"

# Define the JSON schema instruction
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

ocr_text = """
AX-416667
AADHAAR XXXX XXXX 7758
Enrolment No: 22-1-RO-627-0069
Roll No: 1023365178
Board of School Education Haryana
ISO 9001:2015 CERTIFIED
Secondary Examination
Certificate of Qualification cum Mark Sheet
Name: RAJAT
Father: RAGHBIR
Mother: SUMAN
DOB: 01/05/2007
School: RADHA KRISHAN MEMORIAL SCHOOL, FARMANA (ROHTAK)
Exam: MARCH - 2023, Bhiwani
Subjects:
Hindi 86/100 Grade A+ GP 9
English 68/100 Grade B++ GP 7
Mathematics 98/100 Grade A++ GP 10
Social Science 80/100 Grade A GP 8
Science 82/100 Grade A GP 8
Sanskrit 87/100 Grade A GP 8
Total: 433/500 GPA 8.60
General Awareness Life Skills: VERY GOOD
Co-Curricular Activity: A+
Issued: 07/06/2023
Dated: 16/05/2023
"""

payload = {
    "model": "llama3.1",   #  model selection
    "messages": [
        {"role": "system", "content": json_schema},
        {"role": "user", "content": ocr_text}
    ],
    "stream": False  # disable streaming so we get one complete JSON response
}

# Send request
response = requests.post(url, json=payload)
response.raise_for_status()  # Ensure HTTP errors are raised

# Extract JSON output reliably
try:
    result = response.json()
except Exception as e:
    raise Exception(f"Invalid response from Ollama: {e}\nRaw response: {response.text}")

# Get the model's message content
output = result.get("message", {}).get("content", "").strip()

# Handle possible presence of code block markers (common in LLM responses)
if output.startswith("```json"):
    output = output.lstrip("`json").strip()
    output = output.rstrip("`").strip()
elif output.startswith("```"):
    output = output.lstrip("`").strip()
    output = output.rstrip("`").strip()

# Try parsing to ensure it's valid JSON
try:
    parsed = json.loads(output)
except Exception as e:
    print("Raw LLM output for debugging:", output)
    raise Exception(f"Failed to parse JSON from model output: {e}")

# Pretty print the structured JSON
print(json.dumps(parsed, indent=2))
