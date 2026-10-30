from student import Student
from student_manager import StudentManager


def display_menu() -> None:
    print("\nStudent Management System")
    print("1. Add Student")
    print("2. View All Students")
    print("3. Search Student by ID")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")


def read_student_details() -> tuple[str, int, str]:
    name = input("Enter student name: ").strip()
    age = int(input("Enter student age: "))
    course = input("Enter student course: ").strip()
    return name, age, course


def add_student(manager: StudentManager) -> None:
    student_id = input("Enter student ID: ").strip()
    name, age, course = read_student_details()
    manager.add_student(Student(student_id, name, age, course))
    print("Student added successfully.")


def view_all_students(manager: StudentManager) -> None:
    students = manager.get_all_students()
    if not students:
        print("No students found.")
        return

    for student in students:
        print(
            f"ID: {student.student_id} | Name: {student.name} | "
            f"Age: {student.age} | Course: {student.course}"
        )


def search_student(manager: StudentManager) -> None:
    student_id = input("Enter student ID to search: ")
    student = manager.search_student(student_id)
    if student is None:
        print("Student not found.")
        return

    print(
        f"ID: {student.student_id} | Name: {student.name} | "
        f"Age: {student.age} | Course: {student.course}"
    )


def update_student(manager: StudentManager) -> None:
    student_id = input("Enter student ID to update: ")
    name, age, course = read_student_details()
    if manager.update_student(student_id, name, age, course):
        print("Student updated successfully.")
    else:
        print("Student not found.")


def delete_student(manager: StudentManager) -> None:
    student_id = input("Enter student ID to delete: ")
    if manager.delete_student(student_id):
        print("Student deleted successfully.")
    else:
        print("Student not found.")


def main() -> None:
    manager = StudentManager()

    while True:
        display_menu()
        try:
            choice = input("Choose an option (1-6): ").strip()
        except EOFError:
            print("\nExiting Student Management System.")
            break

        if choice == "6":
            print("Exiting Student Management System.")
            break

        actions = {
            "1": add_student,
            "2": view_all_students,
            "3": search_student,
            "4": update_student,
            "5": delete_student,
        }
        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please enter a number from 1 to 6.")
            continue

        try:
            action(manager)
        except ValueError as error:
            print(f"Invalid input: {error}")
        except EOFError:
            print("\nInput ended. Exiting Student Management System.")
            break


if __name__ == "__main__":
    main()