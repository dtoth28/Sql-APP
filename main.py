from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QMessageBox, QGridLayout, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import sys
import sqlite3




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Students")
        self.setFixedSize(500,300)

        file_menu_item = self.menuBar().addMenu("File")
        edit_menu_item = self.menuBar().addMenu("Edit")

        add_student = QAction("Add Student", self)
        add_student.triggered.connect(self.insert)
        file_menu_item.addAction(add_student)

        search = QAction("Search", self)
        search.triggered.connect(self.search)
        edit_menu_item.addAction(search)

        edit = QAction("Update Student", self)
        edit.triggered.connect(self.edit)
        edit_menu_item.addAction(edit)

        delete = QAction("Delete entry", self)
        delete.triggered.connect(self.delete)
        edit_menu_item.addAction(delete)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile)"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_table(self):
        connection = sqlite3.connect("students.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Insert Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Add student
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Add course
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Physics", "Chemistry"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #Add mobile
        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText("Phone")
        layout.addWidget(self.mobile_number)

        #Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def click_handler(self, message ):
        confirmation = QMessageBox()
        confirmation.setText(message)
        confirmation.setIcon(QMessageBox.Icon.Information)

        confirmation.exec()

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_number.text()
        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()
        if name and mobile:
            cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                           (name, course, mobile))
            self.click_handler("Entry Added")
        else:
            self.click_handler("Please enter complete data")
        connection.commit()
        cursor.close()
        connection.close()
        students_app.load_table()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add a submit button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def search_student(self):
        name = self.student_name.text()
        items = students_app.table.findItems("*" + name + "*", Qt.MatchFlag.MatchWildcard)
        for item in items:
            print(item)
            students_app.table.item(item.row(), 1).setSelected(True)

        self.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Get student name from selected row
        index = students_app.table.currentRow()
        student_name = students_app.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = students_app.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = students_app.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = students_app.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        self.close()

        # Refresh the table
        students_app.load_table()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row index and student id
        index = students_app.table.currentRow()
        student_id = students_app.table.item(index, 0).text()

        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        students_app.load_table()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()



app = QApplication(sys.argv)
students_app = MainWindow()
students_app.show()
students_app.load_table()
sys.exit(app.exec())