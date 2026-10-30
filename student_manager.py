import json
import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import List, Optional

from student import Student


class StudentManager:
    """Manage students and store them in a JSON file."""

    def __init__(self) -> None:
        if getattr(sys, "frozen", False):
            app_data = os.environ.get("LOCALAPPDATA")
            if not app_data:
                raise RuntimeError(
                    "LOCALAPPDATA is not set; student data cannot be stored."
                )
            data_directory = Path(app_data) / "StudentManagementSystem"
            self._data_file = data_directory / "students.json"
        else:
            self._data_file = Path(__file__).with_name("students.json")

        self._students: List[Student] = []
        self._load_students()

    def _load_students(self) -> None:
        """Load valid student records from the JSON file."""
        try:
            with self._data_file.open("r", encoding="utf-8") as file:
                records = json.load(file)
        except FileNotFoundError:
            self._save_students()
            return
        except (json.JSONDecodeError, UnicodeDecodeError):
            warnings.warn(
                f"{self._data_file} contains invalid JSON; starting with no students.",
                RuntimeWarning,
            )
            return

        if not isinstance(records, list):
            warnings.warn(
                f"{self._data_file} must contain a JSON list; starting with no students.",
                RuntimeWarning,
            )
            return

        for record in records:
            if not isinstance(record, dict):
                warnings.warn("Skipping an invalid student record.", RuntimeWarning)
                continue

            student_id = record.get("student_id")
            name = record.get("name")
            age = record.get("age")
            course = record.get("course")
            if (
                not isinstance(student_id, str)
                or not isinstance(name, str)
                or type(age) is not int
                or not isinstance(course, str)
            ):
                warnings.warn("Skipping an invalid student record.", RuntimeWarning)
                continue

            try:
                student = Student(student_id, name, age, course)
            except ValueError:
                warnings.warn("Skipping an invalid student record.", RuntimeWarning)
                continue

            if self.search_student(student.student_id) is not None:
                warnings.warn(
                    f"Skipping duplicate student ID '{student.student_id}' in the JSON file.",
                    RuntimeWarning,
                )
                continue
            self._students.append(student)

    def _save_students(self) -> None:
        """Write all students to JSON, replacing the file only after a full write."""
        records = [
            {
                "student_id": student.student_id,
                "name": student.name,
                "age": student.age,
                "course": student.course,
            }
            for student in self._students
        ]
        temporary_path: Optional[Path] = None

        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._data_file.parent,
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(records, file, indent=4)
                file.write("\n")
            os.replace(temporary_path, self._data_file)
        except OSError:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
            raise

    def add_student(self, student: Student) -> None:
        """Add a student, rejecting IDs that are already in use."""
        if not isinstance(student, Student):
            raise TypeError("student must be a Student instance.")

        if self.search_student(student.student_id) is not None:
            raise ValueError(f"A student with ID '{student.student_id}' already exists.")

        self._students.append(student)
        try:
            self._save_students()
        except OSError:
            self._students.pop()
            raise

    def get_all_students(self) -> List[Student]:
        """Return a copy of the current student list."""
        return self._students.copy()

    def search_student(self, student_id: str) -> Optional[Student]:
        """Return the matching student, or None if the ID is not found."""
        normalized_id = student_id.strip()
        for student in self._students:
            if student.student_id == normalized_id:
                return student
        return None

    def update_student(
        self, student_id: str, name: str, age: int, course: str
    ) -> bool:
        """Update a student's details; return False if the ID is not found."""
        student = self.search_student(student_id)
        if student is None:
            return False

        updated_student = Student(
            student_id=student.student_id,
            name=name,
            age=age,
            course=course,
        )
        original_details = (student.name, student.age, student.course)
        student.name = updated_student.name
        student.age = updated_student.age
        student.course = updated_student.course
        try:
            self._save_students()
        except OSError:
            student.name, student.age, student.course = original_details
            raise
        return True

    def delete_student(self, student_id: str) -> bool:
        """Delete a student by ID; return False if the ID is not found."""
        student = self.search_student(student_id)
        if student is None:
            return False

        index = self._students.index(student)
        self._students.pop(index)
        try:
            self._save_students()
        except OSError:
            self._students.insert(index, student)
            raise
        return True
