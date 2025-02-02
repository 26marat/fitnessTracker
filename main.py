# Imports
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QHeaderView, QDateEdit, QLineEdit, QTableWidgetItem, QComboBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from sys import exit


# Main Class
class ExerciseTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.settings()
        self.initUI()
        self.button_click()
    
    # Settings
    def settings(self):
        self.setWindowTitle("Exercise Tracker")
        self.resize(800,600)

    # init UI
    def initUI(self):
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate()) # Displays current date
        
        self.rep_box = QLineEdit()
        self.rep_box.setPlaceholderText("Number of reps completed")
        self.weight_box = QLineEdit()
        self.weight_box.setPlaceholderText("Enter weight lifted (lbs)")
        self.exercise_type = QComboBox()
        self.exercise_type.addItems(["Bench Press", "Squat", "Deadlift", "Other"])

        self.submit_btn = QPushButton("Submit")
        self.add_btn = QPushButton("Add")
        self.delete_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")
        self.summary_btn = QPushButton(" Workout Summary")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Id","Date","Reps","Weight","Exercise Type"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Removes the whitespace for the table label

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Design Our Layout
        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()

        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)
        self.sub_row2.addWidget(QLabel("Reps:"))
        self.sub_row2.addWidget(self.rep_box)
        self.sub_row3.addWidget(QLabel("Lbs:"))
        self.sub_row3.addWidget(self.weight_box)
        self.sub_row4.addWidget(QLabel("Exercise:"))
        self.sub_row4.addWidget(self.exercise_type)

        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)

        btn_row1 = QHBoxLayout()
        btn_row2 = QHBoxLayout()

        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.delete_btn)
        btn_row2.addWidget(self.submit_btn)
        btn_row2.addWidget(self.clear_btn)

        self.col1.addLayout(btn_row1)
        self.col1.addLayout(btn_row2)

        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)

        self.master_layout.addLayout(self.col1, 30)
        self.master_layout.addLayout(self.col2, 70)
        self.setLayout(self.master_layout)
    
        self.apply_styles()
        self.load_table()

    # Events
    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.calculate_reps)
        self.clear_btn.clicked.connect(self.reset)

    # Load Tables
    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness ORDER BY date DESC")
        row = 0
        while query.next():
            fit_id = query.value(0)
            date = query.value(1)
            reps = query.value(2)
            weight = query.value(3)
            exercise = query.value(4)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(fit_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(str(reps)))
            self.table.setItem(row, 3, QTableWidgetItem(str(weight)))
            self.table.setItem(row, 4, QTableWidgetItem(exercise))
            row += 1

    # Add Tables
    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        reps = self.rep_box.text()
        weight = self.weight_box.text()
        exercise = self.exercise_type.currentText()

        query = QSqlQuery("""
                          INSERT INTO fitness (date, reps, weight, exercise_type)
                          VALUES (?,?,?,?)
                          """)
        query.addBindValue(date)
        query.addBindValue(reps)
        query.addBindValue(weight)
        query.addBindValue(exercise)

        if not query.exec_():
            print(query.lastError().text())
        else:
            print("Successfully logged workout")

        self.date_box.setDate(QDate.currentDate())
        self.rep_box.clear()
        self.weight_box.clear()

        self.load_table()


    # Delete Tables
    def delete_workout(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self,"Error","Please choose a row to delete")
            return

        fit_id = int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self,"Are you sure?", "Delete this workout", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM fitness WHERE id = ?")
        query.addBindValue(fit_id)
        query.exec_()

        self.load_table()

    # Calc Reps
    def calculate_reps(self):
        weights = []
        reps = []
        exercises = []

        query = QSqlQuery("SELECT weight, reps, exercise_type From fitness ORDER BY reps ASC")
        while query.next():
            weight = query.value(0)
            rep = query.value(1)
            exercise = query.value(2)
            weights.append(weight)
            reps.append(rep)
            exercises.append(exercise)


        try:
            exercise_colours = {
                'Bench Press': 'red',
                'Squat': 'blue',
                'Deadlift': 'yellow',
                'Other': 'green'
            }

            colours = [exercise_colours.get(exercise) for exercise in exercises]

            plt.style.use("fivethirtyeight") # Possibly customize (Google 'plt.style.use' and read documentation)
            ax = self.figure.subplots()
            ax.scatter(weights, reps, c=colours, label="Data Points")
            ax.set_title("Weight Lifted vs. Reps Completed")
            ax.set_xlabel("Weight")
            ax.set_ylabel("Reps")

            # Legend
            red_patch = mpatches.Patch(color="red", label="Bench Press")
            blue_patch = mpatches.Patch(color="blue", label="Squat")
            yellow_patch = mpatches.Patch(color="yellow", label="Deadlift")
            green_patch = mpatches.Patch(color="green", label="Other")
            patch_list = [red_patch, blue_patch, yellow_patch, green_patch]
            ax.legend(handles=patch_list)

            self.canvas.draw()

        except Exception as e:
            print(f"ERROR {e}")
            QMessageBox.warning(self,"Error","Please enter some data first!")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFA500;
            }
            
            QLabel {
                color: #333;
                font-size: 14px;
            }
            
            QLineEdit, QComboBox, QDateEdit {
                background-color: #FFA500;
                color: #333;
                border: 1px solid #444;
                padding: 5px;
            }
            
            QTableWidget {
                background-color: #FFA500;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
            }
            
            QPushButton {
                background-color: #1d5191;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        figure_color = "#FFA500"
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f"background-color:{figure_color}")
    
    # def summary(self):

    #     query = QSqlQuery("SELECT COUNT(*), SUM(weight), SUM(reps), AVG(weight) FROM fitness")
    #     if query.next():
    #         total_workouts = query.value(0)
    #         self.total_workouts_label.setText(f"Total Workouts: {total_workouts}")

    #         total_weight_lifted = query.value(1)
    #         self.total_weight_label.setText(f"Total Weight Lifted: {total_weight_lifted} lbs") 

    #         total_reps = query.value(2)
    #         self.total_reps_label.setText(f"Total Reps Completed: {total_reps}")

    #         average_weight = query.value(3)
    #         self.average_weight_label.setText(f"Average Weight per Exercise: {average_weight} lbs")

    # Reset (Doesn't reset table)
    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.rep_box.clear()
        self.weight_box.clear()
        self.figure.clear()
        self.canvas.draw()


# Init my DB
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("fitness.db")

if not db.open():
    QMessageBox.critical(None, "ERROR", "Can not open the Database")
    exit(2)

query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS fitness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                reps INTEGER,
                weight REAL,
                exercise_type TEXT
            )
            """)

if __name__ == "__main__":
    app = QApplication([])
    main = ExerciseTracker()
    main.show()
    app.exec_()