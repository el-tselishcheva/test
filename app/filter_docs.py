import sys, subprocess

from PyQt6.QtCore import *
# from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from db import DatabaseHandler
from multi_combobox import MultiComboBox

class FilterDocs(QWidget):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.user_id = user_id
        self.initUI()
        self.load_stylesheet('app/styles.qss')
        self.init_signal_slot()
        self.get_projects()
        self.get_categories()

    def load_stylesheet(self, stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)
    
    def init_signal_slot(self):
        self.search_btn.clicked.connect(self.search_docs)
        self.open_btn.clicked.connect(self.open_docs)
        self.delete_btn.clicked.connect(self.delete_docs)
    
    def initUI(self):
        # self.resize(300, 200)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setVerticalSpacing(15)
        
        self.frame_1 = QFrame(parent=self)
        self.frame_1.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_1.setFrameShadow(QFrame.Shadow.Raised)
        # self.frame.setObjectName('frame')
        
        self.vbox = QVBoxLayout(self.frame_1)
        self.vbox.setContentsMargins(30, 20, 30, 20)
        self.vbox.setSpacing(15)

        self.label_1 = QLabel('проекты:', parent=self.frame_1)
        self.projects = MultiComboBox(parent=self.frame_1)
        self.label_2 = QLabel('категории:', parent=self.frame_1)
        self.categories = MultiComboBox(parent=self.frame_1)

        self.vbox.addWidget(self.label_1)
        self.vbox.addWidget(self.projects)
        self.vbox.addWidget(self.label_2)
        self.vbox.addWidget(self.categories)

        self.frame_2 = QFrame(parent=self)
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        # self.frame.setObjectName('frame')
        
        self.hbox = QHBoxLayout(self.frame_2)
        # self.hbox.setContentsMargins(30, 20, 30, 20)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(15)

        self.search_btn = QPushButton('искать', parent=self.frame_2)
        self.open_btn = QPushButton('открыть', parent=self.frame_2)
        self.delete_btn = QPushButton('удалить', parent=self.frame_2)

        self.hbox.addWidget(self.search_btn)
        self.hbox.addWidget(self.open_btn)
        self.hbox.addWidget(self.delete_btn)

        self.frame_3 = QFrame(parent=self)
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        # self.frame.setObjectName('frame')

        self.result_table = QTableWidget(parent=self.frame_3)
        self.result_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.result_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setShowGrid(False)
        self.result_table.setGridStyle(Qt.PenStyle.NoPen)
        self.result_table.setWordWrap(True)
        self.result_table.setCornerButtonEnabled(False)
        self.result_table.setColumnCount(5)

        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignVCenter)
        self.result_table.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignVCenter)
        self.result_table.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignVCenter)
        self.result_table.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignVCenter)
        self.result_table.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignVCenter)
        self.result_table.setHorizontalHeaderItem(4, item)

        self.result_table.horizontalHeader().setCascadingSectionResizes(False)
        self.result_table.horizontalHeader().setDefaultSectionSize(120)
        self.result_table.horizontalHeader().setMinimumSectionSize(50)
        self.result_table.horizontalHeader().setStretchLastSection(True)

        self.result_table.verticalHeader().setVisible(False)
        self.result_table.verticalHeader().setCascadingSectionResizes(False)
        self.result_table.verticalHeader().setDefaultSectionSize(28)
        self.result_table.verticalHeader().setHighlightSections(False)
        self.result_table.verticalHeader().setSortIndicatorShown(True)
        self.result_table.verticalHeader().setStretchLastSection(False)

        item = self.result_table.horizontalHeaderItem(0)
        item.setText(QCoreApplication.translate("Form", "id"))
        item = self.result_table.horizontalHeaderItem(1)
        item.setText(QCoreApplication.translate("Form", "название"))
        item = self.result_table.horizontalHeaderItem(2)
        item.setText(QCoreApplication.translate("Form", "категория"))
        item = self.result_table.horizontalHeaderItem(3)
        item.setText(QCoreApplication.translate("Form", "проект"))
        item = self.result_table.horizontalHeaderItem(4)
        item.setText(QCoreApplication.translate("Form", "путь"))

        self.glayout = QGridLayout(self.frame_3)
        # self.glayout.setContentsMargins(30, 20, 30, 20)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.glayout.setSpacing(15)

        self.glayout.addWidget(self.result_table)
        
        self.gridLayout.addWidget(self.frame_1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame_2, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.frame_3, 2, 0, 1, 1)
    
    def getSelectedRows(self):
        selected_indexes = self.result_table.selectedIndexes()
        selected_rows = set()

        for index in selected_indexes:
            selected_rows.add(index.row())

        return selected_rows
    
    def get_projects(self):
        modules = self.db.get_all_modules()
        for module in modules:
            self.projects.addItems(module[0])
        self.projects.lineEdit().clear()
    
    def get_categories(self):
        categories = self.db.get_all_categories()
        for category in categories:
            self.categories.addItems(category[1])
        self.categories.lineEdit().clear()
    
    def search_docs(self):
        projects = self.projects.lineEdit().text().split(", ")
        categories = self.categories.lineEdit().text().split(", ")

        result = self.db.search_docs(projects=projects, categories=categories)
        if result:
            self.result_table.setRowCount(0)
            self.result_table.setRowCount(len(result))

            for row, info in enumerate(result):
                for column, item in enumerate(info):
                    cell_item = QTableWidgetItem(str(item))
                    self.result_table.setItem(row, column, cell_item)

        else:
            self.result_table.setRowCount(0)
            return

    def open_docs(self):
        selected_rows = self.getSelectedRows()

        if selected_rows:
            for select_row in selected_rows:
                file_path = self.result_table.item(select_row, 4).text().strip()
                subprocess.Popen(["start", "WINWORD.EXE", file_path], shell=True)
        else:
            QMessageBox.information(self, "Ошибка!", "Пожалуйста, выберите документ(ы).",
                                    QMessageBox.StandardButton.Ok)
    
    def delete_docs(self):
        selected_rows = self.getSelectedRows()

        if selected_rows:
            for select_row in selected_rows:
                selected_option = QMessageBox.warning(self, "Предупреждение", "Вы уверены, что хотите удалить файл(ы)?",
                                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)

                if selected_option == QMessageBox.StandardButton.Yes:
                    doc_id = self.result_table.item(select_row, 0).text().strip()
                    result = self.db.delete_docs(doc_id)

                    if not result:
                        self.search_docs()
                    else:
                        QMessageBox.information(self, "Ошибка!",
                                                f"Fail to delete the information: {result}. Please try again.",
                                                QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Ошибка!", "Пожалуйста, выберите документ(ы).",
                                    QMessageBox.StandardButton.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FilterDocs(user_id=1)
    window.show()
    sys.exit(app.exec())
