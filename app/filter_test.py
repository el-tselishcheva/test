import sys
import psycopg2
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class CheckBoxComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False

        self.lineEdit().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        self.model().dataChanged.connect(self.updateLineEditField)
    
    def eventFilter(self, widget, event):
        if widget == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return super().eventFilter(widget, event)
        
        if widget == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
            return super().eventFilter(widget, event)
        
        return super().eventFilter(widget, event)
        # return False
    
    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)
    
    def addItems(self, text, userData=None):
        item = QStandardItem()
        item.setText(text)
        if not userData is None:
            item.setData(userData)
        
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)
    
    def updateLineEditField(self):
        self.lineEdit().clear()
        text_container = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                text_container.append(self.model().item(i).text())
        print(text_container)
        print(not text_container)
        text_string = ', '.join(text_container)
        self.lineEdit().setText(text_string)
        print(self.lineEdit().text())

class CustomWidget(QWidget):
    def __init__(self, text, custom_attribute, parent=None):
        super().__init__(parent)
        self.custom_attribute = custom_attribute
        
        layout = QHBoxLayout()
        
        self.label = QPushButton(text)
        self.button = QPushButton("open")
        
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        self.button.clicked.connect(self.open_doc)

    def open_doc(self):
        import subprocess
        subprocess.Popen(["start", "WINWORD.EXE", self.custom_attribute], shell=True)
        print(self.custom_attribute)

class FilterApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setWindowTitle("Database Filter")
        # self.setGeometry(100, 100, 400, 200)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)

        # self.layout = QVBoxLayout(self.central_widget)
        self.layout = QVBoxLayout(self)

        self.filter_layout = QFormLayout()
        self.layout.addLayout(self.filter_layout)

        self.name_edit = CheckBoxComboBox()
        self.age_edit = CheckBoxComboBox()

        self.filter_layout.addRow("project", self.name_edit)
        self.filter_layout.addRow("tag", self.age_edit)

        self.filter_button = QPushButton("filter")
        self.filter_button.clicked.connect(self.filter_data)
        self.layout.addWidget(self.filter_button)

        self.result_label = QLabel()
        self.layout.addWidget(self.result_label)

        self.listWidget = QListWidget()
        self.layout.addWidget(self.listWidget)

        self.result_frame = QFrame()
        self.layout.addWidget(self.result_frame)
        self.result_table = QTableWidget(parent=self.result_frame)

        self.db_connection = psycopg2.connect(
            dbname="doc-archive-sys",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        self.cursor = self.db_connection.cursor()
        self.populate_tags()
    
    def show_data(self, result):
        # Function to populate the table with student information
        if result:
            self.result_table.setRowCount(0)
            self.result_table.setRowCount(len(result))

            for row, info in enumerate(result):
                info_list = [
                    info["id"],
                    info["name"],
                    info["path"],
                    info["projects"],
                ]

                for column, item in enumerate(info_list):
                    cell_item = QTableWidgetItem(str(item))
                    self.result_table.setItem(row, column, cell_item)

        else:
            self.result_table.setRowCount(0)
            return

    def populate_tags(self):
        self.cursor.execute("SELECT project_name FROM projects")
        projects = self.cursor.fetchall()
        for project in projects:
            self.name_edit.addItems(project[0])
        
        self.cursor.execute("SELECT tag_name FROM tags")
        tags = self.cursor.fetchall()
        for tag in tags:
            self.age_edit.addItems(tag[0])
        
        self.name_edit.lineEdit().clear()
        self.age_edit.lineEdit().clear()
    
    def filter_data(self):
        self.listWidget.clear()
        
        name = self.name_edit.lineEdit().text().split(", ")
        age = self.age_edit.lineEdit().text().split(", ")

        conditions1 = []
        conditions2 = []
        values = []

        if name:
            for n in name:
                conditions1.append("p.project_name = %s")
                values.append(n)
        if age:
            for a in age:
                conditions2.append("t.tag_name = %s")
                values.append(a)

        query = """SELECT d.doc_name, d.file_path
        FROM docs d
        JOIN doc_tags dt ON d.doc_id = dt.doc_id
        JOIN tags t ON dt.tag_id = t.tag_id
        JOIN projects p ON d.project_id = p.project_id"""

        if conditions1:
            query += " WHERE (" + " OR ".join(conditions1)
        if conditions2:
            if (name[0] == '') | (age[0] == ''):
                query += ") OR "
            else:
                query += ") AND "
            query += "(" + " OR ".join(conditions2)
            query += ")"

        print(query)
        self.cursor.execute(query, values)
        results = self.cursor.fetchall()

        if results:
            result_text = "\n".join(str(row[0]) for row in results)
            for r in results:
                item = QListWidgetItem()
                widget = CustomWidget(r[0], custom_attribute=r[1])
                item.setSizeHint(widget.sizeHint())  # Установка размера элемента
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, widget)

                # self.listWidget.addItem(CustomListItem(str(r[0]), custom_attribute=str(r[1])))
                # self.listWidget.setItemWidget(CustomListItem(str(r[0]), custom_attribute=str(r[1])), QPushButton("open"))
            # result_text = "\n".join(", ".join(str(cell) for cell in row) for row in results)
        else:
            result_text = "No results found."

        # self.result_label.setText(result_text)
        self.listWidget.show()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = FilterApp()
#     window.show()
#     sys.exit(app.exec())
