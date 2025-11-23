from db_manager import AcatDatabase

# Example JSON input
#data = {} # jason data here

data = {
  "University": "Maharshi Dayanand University, Rohtak",
  "Course": "BACHELOR OF TECHNOLOGY (COMPUTER SCIENCE & DESIGN)",
  "Semester": "1ST SEMESTER",
  "Examination": "DECEMBER 2024 Examination",
  "Student": {
    "Name": "SHIV PANDIT",
    "RegNo": 2412201869,
    "RollNo": 8049571,
    "SerialNo": 34382872,
    "FatherName": "RAMESHWAR PANDIT",
    "MotherName": "MEENA KUMARI"
  },
  "Subjects": [
    {
      "Code": "BSC-CH101G",
      "Name": "CHEMISTRY-1",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 38
      }
    },
    {
      "Code": "BSC-CH102G",
      "Name": "CHEMISTRY LAB-I",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 47
      },
      "Practical": {
        "Max": 25,
        "Min": 10,
        "Secured": 24
      }
    },
    {
      "Code": "BSC-CH103G",
      "Name": "MATHEMATICS-I",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 58
      }
    },
    {
      "Code": "BSC-CH104G",
      "Name": "PROGRAMMING",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 46
      }
    },
    {
      "Code": "BSC-CH105G",
      "Name": "PROGRAMMING LAB-I",
      "Theory": '',
      "Practical": {
        "Max": 25,
        "Min": 10,
        "Secured": 23
      }
    },
    {
      "Code": "BSC-CH106G",
      "Name": "WORKSHOP TECHNOLOGY",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 49
      }
    },
    {
      "Code": "BSC-CH107G",
      "Name": "MANUFACTURING LAB-I",
      "Theory": '',
      "Practical": {
        "Max": 25,
        "Min": 10,
        "Secured": 23
      }
    },
    {
      "Code": "BSC-CH108G",
      "Name": "ENGLISH",
      "Theory": {
        "Max": 75,
        "Min": 30,
        "Secured": 70
      }
    }
  ],
  "Result": {
    "Status": "PASSED AND HAS OBTAINED FOUR HUNDRED NINETY FOUR MARKS",
    "TotalMarksObtained": 494
  },
  "Date": "24/03/2025"
}

# Use the class
db = AcatDatabase()
db.save_exam_data(data)

reg_no = 2412201869
roll_no = 8049571

result = db.get_json(reg_no, roll_no)

if result:
    import json
    print(json.dumps(result, indent=2))
else:
    print("No exam data found for this Reg No. and Roll No.")

db.close()

