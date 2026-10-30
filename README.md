# Student Management System

A beginner-friendly command-line application for managing student records. It supports the basic student record operations and stores data in a local JSON file so records are available the next time the program runs.

## Features

- Add a student with a unique ID, name, age, and course
- View all saved students
- Search for a student by ID
- Update a student's name, age, and course
- Delete a student by ID
- Save changes to `students.json` automatically
- Create the data file when it is missing
- Handle invalid JSON or invalid records by warning and skipping unusable data

## Technologies Used

- Python 3.9 or later
- Python standard library: `dataclasses`, `json`, `pathlib`, `tempfile`, and `warnings`
- JSON for local data storage

No third-party packages are required.

## Project Folder Structure

```text
copilot-student-management/
├── main.py             # Command-line menu and user interaction
├── student.py          # Student data model and validation
├── student_manager.py  # Student operations and JSON persistence
├── students.json       # Student records (created automatically if missing)
└── README.md           # Project documentation
```

`students.json` is stored in the same folder as `student_manager.py`. It is created automatically the first time the program runs if it does not already exist.

## Installation

1. Install Python 3.9 or later. To check your Python version, run:

   ```text
   python --version
   ```

2. Download or clone this project and open a terminal in the project folder.

3. No dependency installation is needed; the project uses only Python's standard library.

## How to Run

From the project folder, run:

```text
python main.py
```

On some systems, the Python command may be `python3` instead:

```text
python3 main.py
```

## Usage

When the program starts, choose an option from the menu:

```text
Student Management System
1. Add Student
2. View All Students
3. Search Student by ID
4. Update Student
5. Delete Student
6. Exit
```

- **Add Student:** Enter a unique student ID, name, positive whole-number age, and course.
- **View All Students:** Display all records currently saved.
- **Search Student by ID:** Enter the ID of the student to find.
- **Update Student:** Enter the existing ID, then the student's new name, age, and course.
- **Delete Student:** Enter the ID of the student to remove.
- **Exit:** Close the application.

Changes made by adding, updating, or deleting a student are saved to `students.json`. The file is loaded automatically the next time the program starts. Student IDs must be unique. If the JSON file is malformed, the program issues a warning and starts without loading student records; valid records are otherwise loaded from the file.

## Future Improvements

- Add unit tests for the student model, manager, and command-line flows
- Add sorting and filtering by name, course, or age
- Allow updating one field at a time
- Add a graphical or web-based user interface
- Move to a database such as SQLite for larger datasets and more robust querying
- Add export and import options for CSV files
