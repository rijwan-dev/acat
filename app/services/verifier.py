import json
from typing import Any, Dict, Optional, Tuple, List
from db_manager import AcatDatabase

class AcatVerifier:
    """
    Checks exam JSON data against existing database entry, tells if it exists,
    if changed or not, and shows what is changed.
    """

    def __init__(self, db_name: str = "exam_results.db"):
        self.db = AcatDatabase(db_name)

    def find_by_identity(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        student = data.get('Student', {})
        reg_no = student.get('RegNo')
        roll_no = student.get('RollNo')
        if not (isinstance(reg_no, int) and isinstance(roll_no, int)):
            return None
        return self.db.get_json(reg_no, roll_no)

    def compare_dicts(self, d1: Any, d2: Any, path: str = "") -> List[str]:
        """
        Recursively compare two dicts/lists, return a list of human-readable change descriptions.
        """
        diffs = []
        if isinstance(d1, dict) and isinstance(d2, dict):
            for key in set(d1.keys()).union(d2.keys()):
                new_path = f"{path}.{key}" if path else key
                if key not in d1:
                    diffs.append(f"{new_path}: Added = {d2[key]}")
                elif key not in d2:
                    diffs.append(f"{new_path}: Removed (was {d1[key]})")
                else:
                    diffs.extend(self.compare_dicts(d1[key], d2[key], path=new_path))
        elif isinstance(d1, list) and isinstance(d2, list):
            # Compare list item by item (unordered matching not implemented)
            min_len = min(len(d1), len(d2))
            for i in range(min_len):
                diffs.extend(self.compare_dicts(d1[i], d2[i], path=f"{path}[{i}]"))
            for i in range(min_len, len(d1)):
                diffs.append(f"{path}[{i}]: Removed (was {d1[i]})")
            for i in range(min_len, len(d2)):
                diffs.append(f"{path}[{i}]: Added = {d2[i]}")
        else:
            if d1 != d2:
                diffs.append(f"{path}: Changed from {d1} to {d2}")
        return diffs

    def check(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a dict indicating if entry exists, if changed, and what has changed.
        """
        db_data = self.find_by_identity(input_data)
        if db_data is None:
            return {
                "exists": False,
                "changed": None,
                "changes": None
            }

        # Strip possible extra fields in db_data that aren't in input_data
        # Or, just compare input_data to db_data directly field by field
        changes = self.compare_dicts(db_data, input_data)
        return {
            "exists": True,
            "changed": bool(changes),
            "changes": changes if changes else None
        }

    def close(self):
        self.db.close()


# Example usage:
#if __name__ == "__main__":
#    checker = ExamDataChecker()
    # Assume input_json is loaded as a dict from somewhere
    # result = checker.check(input_json)
    # print(json.dumps(result, indent=2))
#    checker.close()
