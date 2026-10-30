from dataclasses import dataclass


@dataclass
class Student:
    """Represents one student in the system."""

    student_id: str
    name: str
    age: int
    course: str

    def __post_init__(self) -> None:
        self.student_id = self.student_id.strip()
        self.name = self.name.strip()
        self.course = self.course.strip()

        if not self.student_id:
            raise ValueError("Student ID cannot be empty.")
        if not self.name:
            raise ValueError("Student name cannot be empty.")
        if self.age <= 0:
            raise ValueError("Age must be a positive number.")
        if not self.course:
            raise ValueError("Course cannot be empty.")
