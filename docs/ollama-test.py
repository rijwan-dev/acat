import requests
import json

url = "http://172.20.213.4:11500/api/chat"

# Define the JSON schema instruction
json_schema = """
You are to output ONLY valid JSON.
Do not include explanations, comments, or extra text.
there may be some error which you have to guess and fix.
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
}"""

ocr_text = """
Maharshi Dayanand University, Rohtak
BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE & DESIGN)
Statement of Marks/Grade 1ST SEMESTER
DECEMBER 2024 Examination
Reg No.: 2412201869
Name: SHIV PANDIT
Father's Name: RAMESHWAR PANDIT
Mother's Name: MEENA KUMARI
Serial No.: 34382872
Roll No.: 8049571
S.N. Sub Code/Course Subjects/Papers mheory Practical
ID Max | Min | Sec | Max | Min | Sec
1. BSC-CH101G |CHEMISTRY-1 75 30 38
2. BSC-CH102G |CHEMISTRY LAB-I 75 30 47 | 25 | 10 | 24
3. BSC-CH103G |MATHEMATICS-I 75 30 58
4. BSC-CH104G = |PROGRAMMING 75 30 46
3. BSC-CH105G = |PROGRAMMING LAB-I 75 30 68 | 25 |} 10 | 23
6. BSC-CH106G |WORKSHOP TECHNOLOGY | 75 30 49
7. BSC-CH107G |MANUFACTURING LAB-I 75 30 56 | 25 | 10 | 23
8. BSC-CH108G |ENGLISH 75 30 70
RESULT : PASSED AND HAS OBTAINED FOUR HUNDRED NINETY FOUR MARK
Dated: 24/03/2025
THIS [IS FOR DEMONSTRATION PURPOSE ONLY
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
