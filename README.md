# Student Management System

A beginner-friendly application for managing student records. Use the command-line interface or the Tkinter desktop dashboard to work with records stored in a local JSON file.

## Features

- Add a student with a unique ID, name, age, and course
- View all saved students
- Search for a student by ID
- Update a student's name, age, and course
- Delete a student by ID
- Save changes to `students.json` automatically
- Create the data file when it is missing
- Handle invalid JSON or invalid records by warning and skipping unusable data
- Use the desktop GUI with light and dark themes
- Export all student records to CSV or Excel from the Manage Students page
- Require admin sign-in to open the desktop dashboard, with logout and show/hide password controls
- View live student, course, and age analytics with dashboard charts
- Generate all-student or individual-student PDF reports

## Technologies Used

- Python 3.11 or later for the current Matplotlib dependency
- Python standard library: `dataclasses`, `json`, `pathlib`, `tempfile`, and `warnings`
- Tkinter for the desktop GUI and `csv` for CSV export
- `openpyxl` for formatted Excel export
- `matplotlib` for dashboard analytics charts
- `reportlab` for formatted PDF reports
- JSON for local data storage

Excel export requires `openpyxl`, dashboard analytics require `matplotlib`, and PDF reports require `reportlab`. Windows executable packaging uses `PyInstaller`. Install the dependencies with:

```text
python -m pip install -r requirements.txt
```

## Project Folder Structure

```text
copilot-student-management/
├── main.py             # Command-line menu and user interaction
├── gui.py              # Tkinter desktop dashboard
├── student.py          # Student data model and validation
├── student_manager.py  # Student operations and JSON persistence
├── students.json       # Student records (created automatically if missing)
├── requirements.txt    # GUI, export, chart, and packaging dependencies
└── README.md           # Project documentation
```

When running from source, `students.json` is stored beside `student_manager.py`. In a PyInstaller executable, records are stored in `%LOCALAPPDATA%\StudentManagementSystem\students.json`. The file is created automatically when needed, outside the bundled application directory. If `LOCALAPPDATA` is unavailable, the application reports an error instead of writing to a different or potentially read-only location.

## Installation

1. Install Python 3.11 or later. To check your Python version, run:

   ```text
   python --version
   ```

2. Download or clone this project and open a terminal in the project folder.

3. Install the application and packaging dependencies:

   ```text
   python -m pip install -r requirements.txt
   ```

   CSV export and the command-line application do not require these third-party packages; the GUI uses them for Excel export, analytics, PDF reports, and executable packaging.

## How to Run

From the project folder, run:

```text
python main.py
```

On some systems, the Python command may be `python3` instead:

```text
python3 main.py
```

To launch the desktop application, run:

```text
python gui.py
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

In the desktop GUI, the Dashboard displays live student/course totals, average age, course-wise student counts, and charts for course and age distributions. Use **Refresh Analytics** to recalculate manually; successful add, update, and delete operations refresh the values automatically. Use **Manage Students** to search and maintain records. Choose **Export to CSV** or **Export to Excel** to save all current student records to a location of your choice. Choose **Export PDF** to generate a report for all students or the student selected in the table; PDF reports require `reportlab`.

### Admin Login (Development Setup)

The GUI starts at an admin sign-in screen. There are no default credentials. Set both `STUDENT_ADMIN_USERNAME` and `STUDENT_ADMIN_PASSWORD` before starting the GUI. If either variable is missing or empty, sign-in is blocked and the application displays a configuration error. For source development, configure them in PowerShell:

```powershell
$env:STUDENT_ADMIN_USERNAME = "your-admin-username"
$env:STUDENT_ADMIN_PASSWORD = "set-a-private-password"
python gui.py
```

The application reads these values when it starts. Environment variables remain plain text in the local process and this login is not production-grade security. Do not use real or reused passwords.

## Build a Windows Executable

Build on Windows using the same Python environment where the project requirements are installed. From the project folder, run:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --name StudentManagementSystem --collect-all matplotlib --collect-all openpyxl --collect-all reportlab gui.py
```

The executable is created at `dist\StudentManagementSystem\StudentManagementSystem.exe`. This command creates a one-folder distribution, which is generally easier to troubleshoot than a one-file build. Share the complete `dist\StudentManagementSystem` folder.

The build deliberately does not use `--add-data` for `students.json`, credentials, or other local records. The project `.gitignore` also excludes `students.json`. No icon file is currently present, so the build uses the default executable icon. If an `.ico` asset is added later, add `--icon path\to\application.ico` to the build command.

Set admin credentials in the same PowerShell session before running the packaged GUI:

```powershell
$env:STUDENT_ADMIN_USERNAME = "your-admin-username"
$env:STUDENT_ADMIN_PASSWORD = "set-a-private-password"
.\dist\StudentManagementSystem\StudentManagementSystem.exe
```

The executable reads student records from `%LOCALAPPDATA%\StudentManagementSystem\students.json`; it does not need write access to its installation folder.

## Future Improvements

- Add unit tests for the student model, manager, and command-line flows
- Add sorting and filtering by name, course, or age
- Allow updating one field at a time
- Add a graphical or web-based user interface
- Move to a database such as SQLite for larger datasets and more robust querying
- Add CSV import for student records
