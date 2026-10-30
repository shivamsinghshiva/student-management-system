import csv
import hmac
import os
import tkinter as tk
from collections import Counter
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from xml.sax.saxutils import escape

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from student import Student
from student_manager import StudentManager


class StudentManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 650)

        self.manager = StudentManager()
        self.current_theme = "light"
        self.current_page = "Dashboard"
        self.admin_username = os.environ.get("STUDENT_ADMIN_USERNAME", "admin")
        self.admin_password = os.environ.get("STUDENT_ADMIN_PASSWORD", "admin@123")
        self.themes = {
            "light": {
                "background": "#f3f6fb",
                "surface": "#ffffff",
                "sidebar": "#ffffff",
                "foreground": "#172b4d",
                "muted": "#66758a",
                "accent": "#2563eb",
                "accent_active": "#1d4ed8",
                "input": "#ffffff",
                "border": "#dce4ef",
                "selected": "#dbeafe",
                "hover": "#eff6ff",
                "danger": "#dc2626",
            },
            "dark": {
                "background": "#0b1220",
                "surface": "#151f31",
                "sidebar": "#101a2b",
                "foreground": "#edf3fc",
                "muted": "#a7b4c8",
                "accent": "#3b82f6",
                "accent_active": "#60a5fa",
                "input": "#202d42",
                "border": "#2b3a51",
                "selected": "#254d84",
                "hover": "#1b2b43",
                "danger": "#ef4444",
            },
        }

        self.style = ttk.Style(root)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self._build_login()
        self._build_layout()
        self._build_dashboard()
        self._build_add_page()
        self._build_manage_page()
        self.show_page("Dashboard")
        self.refresh_table()
        self.apply_theme()
        self.show_login()

    def _build_login(self):
        self.login_page = ttk.Frame(self.root, style="App.TFrame")
        self.login_page.grid(row=0, column=0, sticky="nsew")
        self.login_page.grid_columnconfigure(0, weight=1)
        self.login_page.grid_rowconfigure(0, weight=1)

        self.login_card = ttk.Frame(
            self.login_page, style="Login.Card.TFrame", padding=(38, 34)
        )
        self.login_card.grid(row=0, column=0, padx=24, pady=24)
        self.login_card.grid_columnconfigure(0, weight=1)

        self.login_theme_button = ttk.Button(
            self.login_page,
            text="Dark Mode",
            style="Secondary.TButton",
            command=self.toggle_theme,
        )
        self.login_theme_button.place(relx=1.0, x=-24, y=22, anchor="ne")

        ttk.Label(
            self.login_card,
            text="STUDENT MANAGEMENT",
            style="Login.Brand.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.login_card,
            text="Admin sign in",
            style="Login.Title.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(18, 5))
        ttk.Label(
            self.login_card,
            text="Sign in to continue to the dashboard.",
            style="Login.Subtitle.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(0, 22))

        ttk.Label(
            self.login_card, text="Username", style="Field.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.login_username = ttk.Entry(
            self.login_card, style="Form.TEntry", width=34
        )
        self.login_username.grid(row=4, column=0, sticky="ew", ipady=5)

        ttk.Label(
            self.login_card, text="Password", style="Field.TLabel"
        ).grid(row=5, column=0, sticky="w", pady=(16, 6))
        self.login_password = ttk.Entry(
            self.login_card, style="Form.TEntry", show="*"
        )
        self.login_password.grid(row=6, column=0, sticky="ew", ipady=5)

        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.login_card,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            style="Login.TCheckbutton",
        ).grid(row=7, column=0, sticky="w", pady=(8, 18))

        self.login_error = ttk.Label(
            self.login_card,
            text="",
            style="Login.Error.TLabel",
            wraplength=320,
        )
        self.login_error.grid(row=8, column=0, sticky="w", pady=(0, 8))
        self.login_button = ttk.Button(
            self.login_card,
            text="Sign In",
            style="Accent.TButton",
            command=self.authenticate,
        )
        self.login_button.grid(row=9, column=0, sticky="ew", ipady=3)
        self.login_password.bind("<Return>", self.authenticate)
        self.login_username.bind("<Return>", lambda _event: self.login_password.focus_set())

    def show_login(self):
        self.dashboard_shell.grid_remove()
        self.login_page.grid()
        self.login_username.focus_set()

    def authenticate(self, _event=None):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        credentials_configured = bool(self.admin_username and self.admin_password)
        if not credentials_configured:
            self.login_password.delete(0, tk.END)
            self.login_error.configure(
                text=(
                    "Admin credentials are not configured. Set "
                    "STUDENT_ADMIN_USERNAME and STUDENT_ADMIN_PASSWORD, "
                    "then restart the application."
                )
            )
            self.login_password.focus_set()
            return "break"

        username_matches = hmac.compare_digest(
            username.encode("utf-8"), self.admin_username.encode("utf-8")
        )
        password_matches = hmac.compare_digest(
            password.encode("utf-8"), self.admin_password.encode("utf-8")
        )
        if username_matches and password_matches:
            self.login_error.configure(text="")
            self.login_password.delete(0, tk.END)
            self.login_page.grid_remove()
            self.dashboard_shell.grid()
            self.refresh_dashboard()
            return "break"

        self.login_password.delete(0, tk.END)
        self.login_error.configure(text="Invalid username or password.")
        self.login_password.focus_set()
        return "break"

    def toggle_password_visibility(self):
        self.login_password.configure(
            show="" if self.show_password_var.get() else "*"
        )

    def logout(self):
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.login_error.configure(text="")
        self.show_password_var.set(False)
        self.toggle_password_visibility()
        self.show_login()

    def _build_layout(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.dashboard_shell = ttk.Frame(self.root, style="App.TFrame")
        self.dashboard_shell.grid(row=0, column=0, sticky="nsew")
        self.dashboard_shell.grid_rowconfigure(0, weight=1)
        self.dashboard_shell.grid_columnconfigure(1, weight=1)

        self.sidebar = ttk.Frame(
            self.dashboard_shell, style="Sidebar.TFrame", width=220
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.brand = ttk.Label(
            self.sidebar,
            text="STUDENT\nMANAGEMENT",
            style="Brand.TLabel",
            justify="left",
        )
        self.brand.pack(anchor="w", padx=24, pady=(30, 34))

        self.navigation = {}
        for label in ("Dashboard", "Add Student", "Manage Students"):
            button = ttk.Button(
                self.sidebar,
                text=f"   {label}",
                style="Navigation.TButton",
                command=lambda page=label: self.show_page(page),
            )
            button.pack(fill="x", padx=12, pady=4, ipady=7)
            self.navigation[label] = button

        self.sidebar_footer = ttk.Label(
            self.sidebar,
            text="Student records\nstored locally",
            style="Muted.Sidebar.TLabel",
            justify="left",
        )
        self.sidebar_footer.pack(side="bottom", anchor="w", padx=24, pady=24)

        self.workspace = ttk.Frame(self.dashboard_shell, style="App.TFrame")
        self.workspace.grid(row=0, column=1, sticky="nsew")
        self.workspace.grid_rowconfigure(1, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)

        self.header = ttk.Frame(self.workspace, style="Header.TFrame")
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
        self.header.grid_columnconfigure(0, weight=1)

        self.page_title = ttk.Label(
            self.header,
            text="Dashboard",
            style="PageTitle.TLabel",
        )
        self.page_title.grid(row=0, column=0, sticky="w")
        self.theme_button = ttk.Button(
            self.header,
            text="Dark Mode",
            style="Secondary.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.grid(row=0, column=1, sticky="e")
        self.logout_button = ttk.Button(
            self.header,
            text="Log Out",
            style="Secondary.TButton",
            command=self.logout,
        )
        self.logout_button.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.page_container = ttk.Frame(self.workspace, style="App.TFrame")
        self.page_container.grid(
            row=1, column=0, sticky="nsew", padx=30, pady=(22, 30)
        )
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def _build_dashboard(self):
        self.dashboard_page = ttk.Frame(self.page_container, style="App.TFrame")
        self.dashboard_page.grid(row=0, column=0, sticky="nsew")
        self.dashboard_page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.dashboard_page.grid_rowconfigure(2, weight=1)

        heading = ttk.Frame(self.dashboard_page, style="App.TFrame")
        heading.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        heading.grid_columnconfigure(0, weight=1)
        ttk.Label(
            heading,
            text="Student analytics at a glance",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(
            heading,
            text="Refresh Analytics",
            style="Accent.TButton",
            command=self.refresh_dashboard,
        ).grid(row=0, column=1, sticky="e")

        self.total_students_value = tk.StringVar(value="0")
        self.unique_courses_value = tk.StringVar(value="0")
        self.average_age_value = tk.StringVar(value="0")
        self.course_statistics_value = tk.StringVar(value="No courses")
        metric_cards = (
            ("Total Students", self.total_students_value),
            ("Total Unique Courses", self.unique_courses_value),
            ("Average Student Age", self.average_age_value),
            ("Course-wise Statistics", self.course_statistics_value),
        )
        for column, (title, value) in enumerate(metric_cards):
            card = ttk.Frame(
                self.dashboard_page,
                style="Card.TFrame",
                padding=(17, 18),
            )
            card.grid(
                row=1,
                column=column,
                sticky="nsew",
                padx=(0, 6) if column == 0 else (6, 0),
                pady=(0, 16),
            )
            ttk.Label(
                card,
                text=title,
                style="Muted.TLabel",
                wraplength=180,
            ).pack(anchor="w")
            ttk.Label(
                card,
                textvariable=value,
                style="AnalyticsValue.TLabel",
                wraplength=180,
                justify="left",
            ).pack(anchor="w", pady=(10, 0))

        self.course_chart_card = ttk.Frame(
            self.dashboard_page, style="Card.TFrame", padding=14
        )
        self.course_chart_card.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=(0, 8),
            pady=(0, 8),
        )
        self.course_chart_card.grid_rowconfigure(1, weight=1)
        self.course_chart_card.grid_columnconfigure(0, weight=1)
        ttk.Label(
            self.course_chart_card,
            text="Students by Course",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.course_figure = Figure(figsize=(3.6, 2.4), dpi=90, tight_layout=True)
        self.course_axes = self.course_figure.add_subplot(111)
        self.course_canvas = FigureCanvasTkAgg(
            self.course_figure, master=self.course_chart_card
        )
        self.course_canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew"
        )

        self.age_chart_card = ttk.Frame(
            self.dashboard_page, style="Card.TFrame", padding=14
        )
        self.age_chart_card.grid(
            row=2,
            column=2,
            columnspan=2,
            sticky="nsew",
            padx=(8, 0),
            pady=(0, 8),
        )
        self.age_chart_card.grid_rowconfigure(1, weight=1)
        self.age_chart_card.grid_columnconfigure(0, weight=1)
        ttk.Label(
            self.age_chart_card,
            text="Age Distribution",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.age_figure = Figure(figsize=(3.6, 2.4), dpi=90, tight_layout=True)
        self.age_axes = self.age_figure.add_subplot(111)
        self.age_canvas = FigureCanvasTkAgg(
            self.age_figure, master=self.age_chart_card
        )
        self.age_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    def _build_add_page(self):
        self.add_page = ttk.Frame(self.page_container, style="App.TFrame")
        self.add_page.grid(row=0, column=0, sticky="nsew")

        card = ttk.Frame(self.add_page, style="Card.TFrame", padding=26)
        card.pack(fill="x", anchor="n")
        ttk.Label(
            card, text="Student Registration", style="SectionTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            card,
            text="Enter the student's details below.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 20))

        self.add_entries = self._create_student_fields(card, start_row=2)
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=6, column=0, columnspan=2, sticky="w", pady=(22, 0))
        ttk.Button(
            actions,
            text="Add Student",
            style="Accent.TButton",
            command=self.add_student,
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            actions,
            text="Clear",
            style="Secondary.TButton",
            command=lambda: self.clear_form(self.add_entries),
        ).pack(side="left")
        card.grid_columnconfigure(1, weight=1)

    def _create_student_fields(self, parent, start_row=0, readonly_id=False):
        fields = {}
        definitions = (
            ("student_id", "Student ID"),
            ("name", "Full Name"),
            ("age", "Age"),
            ("course", "Course"),
        )
        for offset, (key, label) in enumerate(definitions):
            row = start_row + offset
            ttk.Label(parent, text=label, style="Field.TLabel").grid(
                row=row, column=0, sticky="w", pady=7, padx=(0, 20)
            )
            entry = ttk.Entry(parent, style="Form.TEntry")
            entry.grid(row=row, column=1, sticky="ew", pady=7, ipady=5)
            if readonly_id and key == "student_id":
                entry.configure(state="readonly")
            fields[key] = entry
        return fields

    def _build_manage_page(self):
        self.manage_page = ttk.Frame(self.page_container, style="App.TFrame")
        self.manage_page.grid(row=0, column=0, sticky="nsew")
        self.manage_page.grid_columnconfigure(0, weight=3)
        self.manage_page.grid_columnconfigure(1, weight=2)
        self.manage_page.grid_rowconfigure(1, weight=1)

        search_card = ttk.Frame(
            self.manage_page, style="Card.TFrame", padding=(18, 14)
        )
        search_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        search_card.grid_columnconfigure(0, weight=1)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_card,
            textvariable=self.search_var,
            style="Form.TEntry",
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=6)
        self.search_entry.bind("<Return>", lambda event: self.search_students())
        ttk.Button(
            search_card,
            text="Search",
            style="Accent.TButton",
            command=self.search_students,
        ).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(
            search_card,
            text="Show All",
            style="Secondary.TButton",
            command=self.clear_search,
        ).grid(row=0, column=2)
        ttk.Button(
            search_card,
            text="Export to CSV",
            style="Secondary.TButton",
            command=self.export_to_csv,
        ).grid(row=0, column=3, padx=(12, 8))
        ttk.Button(
            search_card,
            text="Export to Excel",
            style="Secondary.TButton",
            command=self.export_to_excel,
        ).grid(row=0, column=4)
        ttk.Button(
            search_card,
            text="Export PDF",
            style="Accent.TButton",
            command=self.choose_pdf_report_type,
        ).grid(row=0, column=5, padx=(8, 0))

        table_card = ttk.Frame(
            self.manage_page, style="Card.TFrame", padding=16
        )
        table_card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        ttk.Label(
            table_card, text="Student Records", style="SectionTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        columns = ("student_id", "name", "age", "course")
        self.student_table = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            style="Students.Treeview",
            selectmode="browse",
        )
        headings = {
            "student_id": ("Student ID", 100),
            "name": ("Full Name", 160),
            "age": ("Age", 55),
            "course": ("Course", 110),
        }
        for column, (heading, width) in headings.items():
            self.student_table.heading(column, text=heading)
            self.student_table.column(
                column,
                width=width,
                minwidth=55,
                anchor="w",
                stretch=column == "name",
            )
        scrollbar = ttk.Scrollbar(
            table_card, orient="vertical", command=self.student_table.yview
        )
        self.student_table.configure(yscrollcommand=scrollbar.set)
        self.student_table.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.student_table.bind("<<TreeviewSelect>>", self.on_student_selected)

        detail_card = ttk.Frame(
            self.manage_page, style="Card.TFrame", padding=20
        )
        detail_card.grid(row=1, column=1, sticky="nsew")
        detail_card.grid_columnconfigure(1, weight=1)
        ttk.Label(
            detail_card, text="Student Details", style="SectionTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self.manage_entries = self._create_student_fields(
            detail_card, start_row=1, readonly_id=True
        )

        actions = ttk.Frame(detail_card, style="Card.TFrame")
        actions.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        actions.grid_columnconfigure((0, 1), weight=1)
        ttk.Button(
            actions,
            text="Update",
            style="Accent.TButton",
            command=self.update_student,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=4)
        ttk.Button(
            actions,
            text="Delete",
            style="Danger.TButton",
            command=self.delete_student,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=4)
        ttk.Button(
            actions,
            text="Clear",
            style="Secondary.TButton",
            command=self.clear_manage_form,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)

    def show_page(self, page_name):
        pages = {
            "Dashboard": self.dashboard_page,
            "Add Student": self.add_page,
            "Manage Students": self.manage_page,
        }
        self.current_page = page_name
        self.page_title.configure(text=page_name)
        for page in pages.values():
            page.grid_remove()
        pages[page_name].grid()

        for name, button in self.navigation.items():
            button.configure(
                style="NavigationActive.TButton"
                if name == page_name
                else "Navigation.TButton"
            )
        if page_name == "Dashboard":
            self.refresh_dashboard()
        elif page_name == "Manage Students":
            self.refresh_table()

    def add_student(self):
        try:
            student = Student(
                self._field_value(self.add_entries, "student_id"),
                self._field_value(self.add_entries, "name"),
                self._read_age(self.add_entries),
                self._field_value(self.add_entries, "course"),
            )
            self.manager.add_student(student)
        except (ValueError, TypeError, OSError) as error:
            messagebox.showerror("Unable to add student", str(error), parent=self.root)
            return

        self.refresh_table()
        self.refresh_dashboard()
        self.clear_form(self.add_entries)
        messagebox.showinfo(
            "Student added", "The student record was added successfully.", parent=self.root
        )

    def update_student(self):
        student_id = self._field_value(self.manage_entries, "student_id")
        if not student_id:
            messagebox.showwarning(
                "Select a student",
                "Select a student from the table before updating.",
                parent=self.root,
            )
            return

        try:
            updated = self.manager.update_student(
                student_id,
                self._field_value(self.manage_entries, "name"),
                self._read_age(self.manage_entries),
                self._field_value(self.manage_entries, "course"),
            )
        except (ValueError, TypeError, OSError) as error:
            messagebox.showerror(
                "Unable to update student", str(error), parent=self.root
            )
            return

        if not updated:
            messagebox.showwarning(
                "Student not found",
                "The selected student could not be found.",
                parent=self.root,
            )
            self.refresh_table()
            return

        self.refresh_table()
        self.refresh_dashboard()
        self._select_table_student(student_id)
        messagebox.showinfo(
            "Student updated",
            "The student record was updated successfully.",
            parent=self.root,
        )

    def delete_student(self):
        student_id = self._field_value(self.manage_entries, "student_id")
        if not student_id:
            messagebox.showwarning(
                "Select a student",
                "Select a student from the table before deleting.",
                parent=self.root,
            )
            return

        confirmed = messagebox.askyesno(
            "Delete student",
            f"Delete the record for student ID '{student_id}'?",
            parent=self.root,
        )
        if not confirmed:
            return

        try:
            deleted = self.manager.delete_student(student_id)
        except (ValueError, TypeError, OSError) as error:
            messagebox.showerror(
                "Unable to delete student", str(error), parent=self.root
            )
            return

        if not deleted:
            messagebox.showwarning(
                "Student not found",
                "The selected student could not be found.",
                parent=self.root,
            )
            self.refresh_table()
            return

        self.refresh_table()
        self.refresh_dashboard()
        self.clear_manage_form()
        messagebox.showinfo(
            "Student deleted",
            "The student record was deleted successfully.",
            parent=self.root,
        )

    def search_students(self):
        query = self.search_var.get().strip().casefold()
        self.refresh_table(query)
        if query and not self.student_table.get_children():
            messagebox.showinfo(
                "No results",
                "No students matched that ID or name.",
                parent=self.root,
            )

    def clear_search(self):
        self.search_var.set("")
        self.refresh_table()

    def export_to_csv(self):
        """Export the latest student records to a CSV file."""
        students = self.manager.get_all_students()
        if not students:
            messagebox.showinfo(
                "No student records",
                "There are no student records to export.",
                parent=self.root,
            )
            return

        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export students to CSV",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(("Student ID", "Name", "Age", "Course"))
                writer.writerows(
                    (student.student_id, student.name, student.age, student.course)
                    for student in students
                )
        except (OSError, csv.Error) as error:
            messagebox.showerror(
                "CSV export failed",
                f"Could not export student records:\n{error}",
                parent=self.root,
            )
            return

        messagebox.showinfo(
            "CSV export complete",
            f"Exported {len(students)} student record(s) to:\n{file_path}",
            parent=self.root,
        )

    def export_to_excel(self):
        """Export the latest student records to a formatted Excel workbook."""
        students = self.manager.get_all_students()
        if not students:
            messagebox.showinfo(
                "No student records",
                "There are no student records to export.",
                parent=self.root,
            )
            return

        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export students to Excel",
            defaultextension=".xlsx",
            filetypes=(("Excel workbooks", "*.xlsx"), ("All files", "*.*")),
        )
        if not file_path:
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
            from openpyxl.utils.exceptions import IllegalCharacterError
        except ImportError:
            messagebox.showerror(
                "Excel export unavailable",
                "Excel export requires openpyxl. Install it with:\n"
                "python -m pip install openpyxl",
                parent=self.root,
            )
            return

        try:
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Students"
            headers = ("Student ID", "Name", "Age", "Course")
            worksheet.append(headers)

            for cell in worksheet[1]:
                cell.font = Font(bold=True)

            for student in students:
                worksheet.append(
                    (student.student_id, student.name, student.age, student.course)
                )

            for column_cells in worksheet.columns:
                width = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )
                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(width + 2, 50)

            workbook.save(file_path)
        except (OSError, ValueError, IllegalCharacterError) as error:
            messagebox.showerror(
                "Excel export failed",
                f"Could not export student records:\n{error}",
                parent=self.root,
            )
            return

        messagebox.showinfo(
            "Excel export complete",
            f"Exported {len(students)} student record(s) to:\n{file_path}",
            parent=self.root,
        )

    def choose_pdf_report_type(self):
        """Ask whether to export all records or the selected student."""
        choice = messagebox.askyesnocancel(
            "Export PDF Report",
            "Choose the report type:\n\n"
            "Yes: All Students\n"
            "No: Selected Student\n"
            "Cancel: Close this dialog",
            parent=self.root,
        )
        if choice is None:
            return
        self.export_pdf_report("all" if choice else "individual")

    def export_pdf_report(self, report_type):
        """Create a formatted PDF report from the latest manager records."""
        if report_type not in {"all", "individual"}:
            messagebox.showerror(
                "PDF export failed",
                "Choose either an all-students or individual-student report.",
                parent=self.root,
            )
            return

        students = self.manager.get_all_students()
        if not students:
            messagebox.showinfo(
                "No student records",
                "There are no student records to include in a PDF report.",
                parent=self.root,
            )
            return

        report_students = students
        if report_type == "individual":
            selection = self.student_table.selection()
            if not selection:
                messagebox.showwarning(
                    "Select a student",
                    "Select a student from the table before exporting an individual report.",
                    parent=self.root,
                )
                return

            student = self.manager.search_student(selection[0])
            if student is None:
                messagebox.showwarning(
                    "Student not found",
                    "The selected student could not be found.",
                    parent=self.root,
                )
                self.refresh_table()
                return
            report_students = [student]

        try:
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.platypus.doctemplate import LayoutError
        except ImportError:
            messagebox.showerror(
                "PDF export unavailable",
                "PDF export requires ReportLab. Install it with:\n"
                "python -m pip install reportlab",
                parent=self.root,
            )
            return

        report_title = (
            "All Students Report"
            if report_type == "all"
            else "Individual Student Report"
        )
        default_name = (
            "all_students_report.pdf"
            if report_type == "all"
            else f"student_{report_students[0].student_id}_report.pdf"
        )
        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save PDF report",
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
        )
        if not file_path:
            return

        palette = self.themes[self.current_theme]
        accent = colors.HexColor(palette["accent"])
        muted = colors.HexColor(palette["muted"])
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=25,
            textColor=colors.HexColor("#172b4d"),
            alignment=TA_LEFT,
            spaceAfter=8,
        )
        metadata_style = ParagraphStyle(
            "ReportMetadata",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=muted,
        )
        cell_style = ParagraphStyle(
            "ReportCell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#243247"),
        )
        header_cell_style = ParagraphStyle(
            "ReportHeaderCell",
            parent=cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        story = [
            Paragraph(report_title, title_style),
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                metadata_style,
            ),
            Paragraph(
                f"Students in report: {len(report_students)}"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; Total students: {len(students)}",
                metadata_style,
            ),
            Spacer(1, 18),
        ]

        table_data = [
            [
                Paragraph(header, header_cell_style)
                for header in ("Student ID", "Name", "Age", "Course")
            ],
            *[
                [
                    Paragraph(escape(str(student.student_id)), cell_style),
                    Paragraph(escape(str(student.name)), cell_style),
                    Paragraph(escape(str(student.age)), cell_style),
                    Paragraph(escape(str(student.course)), cell_style),
                ]
                for student in report_students
            ],
        ]
        report_table = Table(
            table_data,
            repeatRows=1,
            colWidths=(105, 190, 55, 150),
            hAlign="LEFT",
        )
        report_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), accent),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("LEADING", (0, 0), (-1, -1), 13),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#243247")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce4ef")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f3f6fb")],
                    ),
                ]
            )
        )
        story.append(report_table)

        try:
            document = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=42,
                leftMargin=42,
                topMargin=48,
                bottomMargin=48,
                title=report_title,
                author="Student Management System",
            )
            document.build(
                story,
                onFirstPage=self._draw_pdf_page_number,
                onLaterPages=self._draw_pdf_page_number,
            )
        except (OSError, ValueError, UnicodeEncodeError, LayoutError) as error:
            messagebox.showerror(
                "PDF export failed",
                f"Could not generate the PDF report:\n{error}",
                parent=self.root,
            )
            return

        messagebox.showinfo(
            "PDF export complete",
            f"Created the {report_title.lower()} with "
            f"{len(report_students)} student record(s):\n{file_path}",
            parent=self.root,
        )

    @staticmethod
    def _draw_pdf_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColorRGB(0.4, 0.46, 0.54)
        canvas.drawRightString(
            document.pagesize[0] - document.rightMargin,
            25,
            f"Page {document.page}",
        )
        canvas.restoreState()

    def refresh_table(self, query=""):
        if not hasattr(self, "student_table"):
            return
        for item in self.student_table.get_children():
            self.student_table.delete(item)

        normalized_query = query.casefold().strip()
        for student in self.manager.get_all_students():
            if normalized_query and not (
                normalized_query in student.student_id.casefold()
                or normalized_query in student.name.casefold()
            ):
                continue
            self.student_table.insert(
                "",
                "end",
                iid=student.student_id,
                values=(
                    student.student_id,
                    student.name,
                    student.age,
                    student.course,
                ),
            )

    def on_student_selected(self, _event=None):
        selection = self.student_table.selection()
        if not selection:
            return
        student = self.manager.search_student(selection[0])
        if student is None:
            return
        self._set_readonly_value(
            self.manage_entries["student_id"], student.student_id
        )
        self._set_entry_value(self.manage_entries["name"], student.name)
        self._set_entry_value(self.manage_entries["age"], str(student.age))
        self._set_entry_value(self.manage_entries["course"], student.course)

    def _select_table_student(self, student_id):
        if self.student_table.exists(student_id):
            self.student_table.selection_set(student_id)
            self.student_table.focus(student_id)
            self.student_table.see(student_id)
            self.on_student_selected()

    def refresh_dashboard(self):
        self.refresh_analytics()

    def refresh_analytics(self):
        """Recalculate dashboard metrics and charts from the latest records."""
        students = self.manager.get_all_students()
        course_counts = Counter(student.course.strip() for student in students)
        age_counts = Counter(student.age for student in students)
        unique_courses = len(course_counts)

        self.total_students_value.set(str(len(students)))
        self.unique_courses_value.set(str(unique_courses))
        if students:
            average_age = sum(student.age for student in students) / len(students)
            self.average_age_value.set(f"{average_age:.1f}")
        else:
            self.average_age_value.set("N/A")

        if course_counts:
            most_common_course, count = sorted(
                course_counts.items(),
                key=lambda item: (-item[1], item[0].casefold()),
            )[0]
            self.course_statistics_value.set(
                f"{most_common_course}: {count}"
            )
        else:
            self.course_statistics_value.set("No courses")

        self._draw_analytics_charts(course_counts, age_counts)

    def _draw_analytics_charts(self, course_counts, age_counts):
        colors = self.themes[self.current_theme]
        text_color = colors["foreground"]
        grid_color = colors["border"]
        self.course_canvas.get_tk_widget().configure(
            background=colors["surface"],
            highlightthickness=0,
        )
        self.age_canvas.get_tk_widget().configure(
            background=colors["surface"],
            highlightthickness=0,
        )

        self.course_figure.set_facecolor(colors["surface"])
        self.course_axes.clear()
        self.course_axes.set_facecolor(colors["surface"])
        if course_counts:
            courses = sorted(
                course_counts.items(),
                key=lambda item: (item[1], item[0].casefold()),
            )
            labels, counts = zip(*courses)
            self.course_axes.barh(
                labels,
                counts,
                color=colors["accent"],
                height=0.65,
            )
            self.course_axes.set_xlabel("Students", color=text_color)
            self.course_axes.xaxis.grid(True, color=grid_color, alpha=0.6)
            self.course_axes.set_axisbelow(True)
        else:
            self.course_axes.text(
                0.5,
                0.5,
                "No student data yet",
                color=colors["muted"],
                ha="center",
                va="center",
                transform=self.course_axes.transAxes,
            )
            self.course_axes.set_xticks([])
            self.course_axes.set_yticks([])
        self._style_chart_axes(self.course_axes, text_color, grid_color)
        self.course_figure.tight_layout()
        self.course_canvas.draw()

        self.age_figure.set_facecolor(colors["surface"])
        self.age_axes.clear()
        self.age_axes.set_facecolor(colors["surface"])
        if age_counts:
            ages = sorted(age_counts)
            counts = [age_counts[age] for age in ages]
            self.age_axes.bar(
                [str(age) for age in ages],
                counts,
                color=colors["accent"],
                width=0.7,
            )
            self.age_axes.set_xlabel("Age (years)", color=text_color)
            self.age_axes.set_ylabel("Students", color=text_color)
            self.age_axes.yaxis.grid(True, color=grid_color, alpha=0.6)
            self.age_axes.set_axisbelow(True)
            if len(ages) > 8:
                self.age_axes.tick_params(axis="x", labelrotation=45)
        else:
            self.age_axes.text(
                0.5,
                0.5,
                "No student data yet",
                color=colors["muted"],
                ha="center",
                va="center",
                transform=self.age_axes.transAxes,
            )
            self.age_axes.set_xticks([])
            self.age_axes.set_yticks([])
        self._style_chart_axes(self.age_axes, text_color, grid_color)
        self.age_figure.tight_layout()
        self.age_canvas.draw()

    @staticmethod
    def _style_chart_axes(axes, text_color, grid_color):
        axes.tick_params(axis="both", colors=text_color, labelsize=8)
        for spine in axes.spines.values():
            spine.set_color(grid_color)
        axes.xaxis.label.set_color(text_color)
        axes.yaxis.label.set_color(text_color)

    def clear_manage_form(self):
        self._set_readonly_value(self.manage_entries["student_id"], "")
        for key in ("name", "age", "course"):
            self._set_entry_value(self.manage_entries[key], "")
        for item in self.student_table.selection():
            self.student_table.selection_remove(item)

    @staticmethod
    def clear_form(entries):
        for entry in entries.values():
            entry.configure(state="normal")
            entry.delete(0, tk.END)

    @staticmethod
    def _field_value(entries, key):
        return entries[key].get().strip()

    def _read_age(self, entries):
        value = self._field_value(entries, "age")
        try:
            return int(value)
        except ValueError as error:
            raise ValueError("Age must be a positive whole number.") from error

    @staticmethod
    def _set_entry_value(entry, value):
        entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def _set_readonly_value(self, entry, value):
        entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.configure(state="readonly")

    def toggle_theme(self):
        """Switch between light and dark themes without restarting."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        """Apply the active palette to the window and every themed widget."""
        colors = self.themes[self.current_theme]
        self.root.configure(bg=colors["background"])
        self._configure_ttk_styles(colors)
        next_theme_label = (
            "Light Mode" if self.current_theme == "dark" else "Dark Mode"
        )
        self.theme_button.configure(text=next_theme_label)
        self.login_theme_button.configure(text=next_theme_label)
        if hasattr(self, "course_canvas"):
            self.refresh_analytics()

    def _configure_ttk_styles(self, colors):
        self.style.configure("TFrame", background=colors["background"])
        self.style.configure(
            "App.TFrame", background=colors["background"]
        )
        self.style.configure(
            "Sidebar.TFrame", background=colors["sidebar"]
        )
        self.style.configure(
            "Header.TFrame", background=colors["background"]
        )
        self.style.configure(
            "Card.TFrame",
            background=colors["surface"],
            relief="solid",
            borderwidth=1,
        )
        self.style.configure(
            "Login.Card.TFrame",
            background=colors["surface"],
            relief="solid",
            borderwidth=1,
        )
        self.style.configure(
            "TLabel",
            background=colors["background"],
            foreground=colors["foreground"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Brand.TLabel",
            background=colors["sidebar"],
            foreground=colors["accent"],
            font=("Segoe UI", 15, "bold"),
        )
        self.style.configure(
            "PageTitle.TLabel",
            background=colors["background"],
            foreground=colors["foreground"],
            font=("Segoe UI", 21, "bold"),
        )
        self.style.configure(
            "SectionTitle.TLabel",
            background=colors["surface"],
            foreground=colors["foreground"],
            font=("Segoe UI", 14, "bold"),
        )
        self.style.configure(
            "StatValue.TLabel",
            background=colors["surface"],
            foreground=colors["accent"],
            font=("Segoe UI", 30, "bold"),
        )
        self.style.configure(
            "AnalyticsValue.TLabel",
            background=colors["surface"],
            foreground=colors["accent"],
            font=("Segoe UI", 19, "bold"),
        )
        self.style.configure(
            "Muted.TLabel",
            background=colors["surface"],
            foreground=colors["muted"],
        )
        self.style.configure(
            "Field.TLabel",
            background=colors["surface"],
            foreground=colors["foreground"],
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "Muted.Sidebar.TLabel",
            background=colors["sidebar"],
            foreground=colors["muted"],
        )
        self.style.configure(
            "Login.Brand.TLabel",
            background=colors["surface"],
            foreground=colors["accent"],
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "Login.Title.TLabel",
            background=colors["surface"],
            foreground=colors["foreground"],
            font=("Segoe UI", 22, "bold"),
        )
        self.style.configure(
            "Login.Subtitle.TLabel",
            background=colors["surface"],
            foreground=colors["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Login.Error.TLabel",
            background=colors["surface"],
            foreground=colors["danger"],
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Login.TCheckbutton",
            background=colors["surface"],
            foreground=colors["muted"],
            font=("Segoe UI", 9),
        )
        self.style.map(
            "Login.TCheckbutton",
            background=[("active", colors["surface"])],
            foreground=[("active", colors["foreground"])],
        )
        self.style.configure(
            "TButton",
            background=colors["accent"],
            foreground="#ffffff",
            padding=(13, 9),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TButton",
            background=[
                ("disabled", colors["border"]),
                ("active", colors["accent_active"]),
            ],
            foreground=[("disabled", colors["muted"])],
        )
        self.style.configure(
            "Accent.TButton",
            background=colors["accent"],
            foreground="#ffffff",
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", colors["accent_active"])],
        )
        self.style.configure(
            "Danger.TButton",
            background=colors["danger"],
            foreground="#ffffff",
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", colors["accent_active"])],
        )
        self.style.configure(
            "Secondary.TButton",
            background=colors["surface"],
            foreground=colors["foreground"],
            borderwidth=1,
            relief="solid",
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", colors["hover"])],
            foreground=[("active", colors["foreground"])],
        )
        self.style.configure(
            "Navigation.TButton",
            background=colors["sidebar"],
            foreground=colors["muted"],
            anchor="w",
            padding=(12, 11),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Navigation.TButton",
            background=[("active", colors["hover"])],
            foreground=[("active", colors["foreground"])],
        )
        self.style.configure(
            "NavigationActive.TButton",
            background=colors["selected"],
            foreground=colors["accent"],
            anchor="w",
            padding=(12, 11),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "TEntry",
            fieldbackground=colors["input"],
            foreground=colors["foreground"],
            insertcolor=colors["foreground"],
            bordercolor=colors["border"],
            padding=8,
        )
        self.style.configure(
            "Form.TEntry",
            fieldbackground=colors["input"],
            foreground=colors["foreground"],
            insertcolor=colors["foreground"],
            bordercolor=colors["border"],
            padding=8,
        )
        self.style.map(
            "Form.TEntry",
            fieldbackground=[("readonly", colors["input"])],
            foreground=[("readonly", colors["foreground"])],
        )
        self.style.configure(
            "Students.Treeview",
            background=colors["surface"],
            fieldbackground=colors["surface"],
            foreground=colors["foreground"],
            rowheight=34,
            bordercolor=colors["border"],
            font=("Segoe UI", 10),
        )
        self.style.map(
            "Students.Treeview",
            background=[("selected", colors["selected"])],
            foreground=[("selected", colors["foreground"])],
        )
        self.style.configure(
            "Students.Treeview.Heading",
            background=colors["background"],
            foreground=colors["muted"],
            font=("Segoe UI", 9, "bold"),
            padding=(8, 10),
            relief="flat",
        )
        self.style.map(
            "Students.Treeview.Heading",
            background=[("active", colors["hover"])],
            foreground=[("active", colors["foreground"])],
        )
        self.style.configure(
            "TScrollbar",
            background=colors["surface"],
            troughcolor=colors["background"],
            bordercolor=colors["background"],
            arrowcolor=colors["muted"],
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementGUI(root)
    root.mainloop()
