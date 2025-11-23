import sqlite3
from typing import Dict, Any, Optional

def _to_int(value) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (ValueError, TypeError):
        return None

class AcatDatabase:
    def __init__(self, db_name: str = "acat_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            RegNo INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            RollNo INTEGER,
            SerialNo INTEGER,
            FatherName TEXT,
            MotherName TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Exams (
            ExamID INTEGER PRIMARY KEY AUTOINCREMENT,
            RegNo INTEGER NOT NULL,
            University TEXT,
            Course TEXT,
            Semester TEXT,
            Examination TEXT,
            Date TEXT,
            ResultStatus TEXT,
            TotalMarksObtained INTEGER,
            FOREIGN KEY (RegNo) REFERENCES Students(RegNo) ON DELETE CASCADE
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            SubjectID INTEGER PRIMARY KEY AUTOINCREMENT,
            ExamID INTEGER NOT NULL,
            Code TEXT,
            Name TEXT,
            TheoryMax INTEGER,
            TheoryMin INTEGER,
            TheorySecured INTEGER,
            PracticalMax INTEGER,
            PracticalMin INTEGER,
            PracticalSecured INTEGER,
            FOREIGN KEY (ExamID) REFERENCES Exams(ExamID) ON DELETE CASCADE
        )
        """)

        self.conn.commit()

    def _upsert_student(self, student: Dict[str, Any]) -> None:
        reg_no = _to_int(student.get("RegNo"))
        name = student.get("Name", "") or ""
        roll = _to_int(student.get("RollNo"))
        serial = _to_int(student.get("SerialNo"))
        father = student.get("FatherName", "") or ""
        mother = student.get("MotherName", "") or ""

        # Try update first
        self.cur.execute("""
            UPDATE Students
            SET Name=?, RollNo=?, SerialNo=?, FatherName=?, MotherName=?
            WHERE RegNo=?
        """, (name, roll, serial, father, mother, reg_no))
        # If no row updated, insert
        if self.cur.rowcount == 0:
            self.cur.execute("""
                INSERT INTO Students (RegNo, Name, RollNo, SerialNo, FatherName, MotherName)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (reg_no, name, roll, serial, father, mother))
        self.conn.commit()

    def save_exam_data(self, data: Dict[str, Any]) -> int:
        if "Student" not in data or "Subjects" not in data or "Result" not in data:
            raise ValueError("JSON must include 'Student', 'Subjects', and 'Result' keys.")

        student = data["Student"]
        self._upsert_student(student)

        reg_no = _to_int(student.get("RegNo"))
        university = data.get("University", "") or ""
        course = data.get("Course", "") or ""
        semester = data.get("Semester", "") or ""
        examination = data.get("Examination", "") or ""
        date = data.get("Date", "") or ""
        result_status = data.get("Result", {}).get("Status", "") or ""
        total_marks = _to_int(data.get("Result", {}).get("TotalMarksObtained"))

        self.cur.execute("""
            INSERT INTO Exams (RegNo, University, Course, Semester, Examination, Date, ResultStatus, TotalMarksObtained)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (reg_no, university, course, semester, examination, date, result_status, total_marks))
        exam_id = self.cur.lastrowid
        if exam_id is None:
            self.conn.rollback()
            raise Exception("Failed to insert exam record: No exam_id returned.")

        for subj in data["Subjects"]:
            code = subj.get("Code", "") or ""
            sname = subj.get("Name", "") or ""
            theory = subj.get("Theory") or {}
            th_max = _to_int(theory.get("Max"))
            th_min = _to_int(theory.get("Min"))
            th_sec = _to_int(theory.get("Secured"))

            practical = subj.get("Practical")
            if isinstance(practical, dict):
                pr_max = _to_int(practical.get("Max"))
                pr_min = _to_int(practical.get("Min"))
                pr_sec = _to_int(practical.get("Secured"))
            else:
                pr_max = pr_min = pr_sec = None

            self.cur.execute("""
                INSERT INTO Subjects (
                    ExamID, Code, Name,
                    TheoryMax, TheoryMin, TheorySecured,
                    PracticalMax, PracticalMin, PracticalSecured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (exam_id, code, sname, th_max, th_min, th_sec, pr_max, pr_min, pr_sec))

        self.conn.commit()
        return exam_id

    def get_exam_json(self, exam_id: int) -> Optional[Dict[str, Any]]:
        self.cur.execute("""
            SELECT RegNo, University, Course, Semester, Examination, Date, ResultStatus, TotalMarksObtained
            FROM Exams WHERE ExamID=?
        """, (exam_id,))
        exam_row = self.cur.fetchone()
        if not exam_row:
            return None

        reg_no, university, course, semester, examination, date, result_status, total_marks = exam_row

        self.cur.execute("""
            SELECT Name, RollNo, SerialNo, FatherName, MotherName
            FROM Students WHERE RegNo=?
        """, (reg_no,))
        srow = self.cur.fetchone()
        if not srow:
            return None

        name, roll, serial, father, mother = srow

        self.cur.execute("""
            SELECT Code, Name, TheoryMax, TheoryMin, TheorySecured,
                   PracticalMax, PracticalMin, PracticalSecured
            FROM Subjects WHERE ExamID=?
        """, (exam_id,))
        subjects_rows = self.cur.fetchall()

        subjects = []
        for code, sname, th_max, th_min, th_sec, pr_max, pr_min, pr_sec in subjects_rows:
            subjects.append({
                "Code": code or "",
                "Name": sname or "",
                "Theory": {"Max": th_max, "Min": th_min, "Secured": th_sec},
                "Practical": (
                    {"Max": pr_max, "Min": pr_min, "Secured": pr_sec}
                    if any(v is not None for v in (pr_max, pr_min, pr_sec))
                    else None
                )
            })

        return {
            "University": university or "",
            "Course": course or "",
            "Semester": semester or "",
            "Examination": examination or "",
            "Student": {
                "Name": name or "",
                "RegNo": reg_no,
                "RollNo": roll,
                "SerialNo": serial,
                "FatherName": father or "",
                "MotherName": mother or ""
            },
            "Subjects": subjects,
            "Result": {
                "Status": result_status or "",
                "TotalMarksObtained": total_marks
            },
            "Date": date or ""
        }

    def close(self):
        self.conn.close()


    def get_json(self, reg_no: int, roll_no: int) -> Optional[Dict[str, Any]]:
        self.cur.execute("""
            SELECT ExamID
            FROM Exams
            WHERE RegNo = ?
            AND RegNo IN (SELECT RegNo FROM Students WHERE RegNo = ? AND RollNo = ?)
            ORDER BY Date DESC, ExamID DESC
            LIMIT 1
        """, (reg_no, reg_no, roll_no))
        row = self.cur.fetchone()
        if not row:
            return None
        exam_id = row[0]
        return self.get_exam_json(exam_id)
