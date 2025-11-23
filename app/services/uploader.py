import json
from typing import Any, Dict, Optional
from .db_manager import AcatDatabase

class AcatUploader:
    """
    Uploads JSON data to the AcatDatabase after verifying its schema.
    """

    def __init__(self, db_name: str = "acat_database.db"):
        self.db = AcatDatabase(db_name)

    def validate_exam_json(self, data: Dict[str, Any]) -> bool:
        # Required top-level fields
        required_top_keys = {"University", "Course", "Semester", "Examination", "Student", "Subjects", "Result", "Date"}
        # Check top-level keys
        if not isinstance(data, dict) or not required_top_keys.issubset(data.keys()):
            return False

        # Validate Student sub-object
        student_keys = {"Name", "RegNo", "RollNo", "SerialNo", "FatherName", "MotherName"}
        student = data["Student"]
        if not isinstance(student, dict) or not student_keys.issubset(student.keys()):
            return False
        # RegNo, RollNo, SerialNo must be ints (or convertible to int)
        for key in ["RegNo", "RollNo", "SerialNo"]:
            if not isinstance(student[key], int):
                return False

        # Validate Subjects
        subjects = data["Subjects"]
        if not isinstance(subjects, list) or len(subjects) == 0:
            return False

        subject_keys = {"Code", "Name", "Theory", "Practical"}
        theory_keys = {"Max", "Min", "Secured"}
        practical_keys = {"Max", "Min", "Secured"}

        for subj in subjects:
            if not isinstance(subj, dict) or not subject_keys.issubset(subj):
                return False
            # Theory validation
            theory = subj["Theory"]
            if not isinstance(theory, dict) or not theory_keys.issubset(theory):
                return False
            for tfield in theory_keys:
                if not isinstance(theory[tfield], int):
                    return False
            # Practical validation (can be None or dict)
            practical = subj["Practical"]
            if practical is not None:
                if not isinstance(practical, dict) or not practical_keys.issubset(practical):
                    return False
                for pfield in practical_keys:
                    if not isinstance(practical[pfield], int):
                        return False

        # Validate Result
        result = data["Result"]
        if not isinstance(result, dict) or not {"Status", "TotalMarksObtained"}.issubset(result.keys()):
            return False
        if not isinstance(result["TotalMarksObtained"], int):
            return False

        # Date validation (just checks for string presence, not format)
        if not isinstance(data["Date"], str):
            return False

        return True

    def upload(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.validate_exam_json(data):
            print("Invalid exam JSON data structure.")
            return None
        exam_id = self.db.save_exam_data(data)
        print(f"Exam data uploaded. Exam ID: {exam_id}")
        return exam_id

    def close(self):
        self.db.close()

# # Example usage:
# if __name__ == "__main__":
#     uploader = ExamDataUploader()
#     # Assume json_data is a variable with the structure you described (Python dict)
#     # exam_id = uploader.upload(json_data)
#     uploader.close()
