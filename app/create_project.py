import sys, os, tkinter, shutil
from tkinter import filedialog
from docx import Document

# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from db import DatabaseHandler
from multi_combobox import MultiComboBox

class CreateProject(QWidget):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.db = DatabaseHandler()
        self.user_id = user_id
        self.initUI()
        self.load_stylesheet('app/styles.qss')
        self.init_signal_slot()
        self.get_modules()

    def load_stylesheet(self, stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)
    
    def init_signal_slot(self):
        self.folder_path = None
        self.new_project_btn.clicked.connect(self.new_project)
        self.project_path_btn.clicked.connect(self.choose_folder)
    
    def initUI(self):
        # self.resize(300, 200)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setVerticalSpacing(15)
        
        self.frame = QFrame(parent=self)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        # self.frame.setObjectName('frame')
        
        self.vbox = QVBoxLayout(self.frame)
        self.vbox.setContentsMargins(30, 20, 30, 20)
        self.vbox.setSpacing(15)

        self.label_1 = QLabel('введите название проекта:', parent=self.frame)
        self.project_name = QLineEdit(parent=self.frame)
        self.label_2 = QLabel('выберите используемый модуль:', parent=self.frame)
        self.module_used = MultiComboBox(parent=self.frame)

        self.project_path = QLineEdit(parent=self.frame)
        self.project_path.setReadOnly(True)
        self.project_path.setPlaceholderText('путь к папке проекта')
        self.project_path_btn = QPushButton('выбрать папку', parent=self.frame)

        self.doc_template_check = QCheckBox('добавить шаблоны', parent=self.frame)
        self.new_project_btn = QPushButton('создать новый проект', parent=self.frame)

        self.vbox.addWidget(self.label_1)
        self.vbox.addWidget(self.project_name)
        self.vbox.addWidget(self.label_2)
        self.vbox.addWidget(self.module_used)
        self.vbox.addWidget(self.project_path)
        self.vbox.addWidget(self.project_path_btn)
        self.vbox.addWidget(self.doc_template_check)
        self.vbox.addWidget(self.new_project_btn)
        
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
    
    def get_modules(self):
        modules = self.db.get_all_modules()
        for module in modules:
            self.module_used.addItems(module[0])
        self.module_used.lineEdit().clear()
    
    def new_project(self):
        if (self.project_name.text() != '') & (not self.folder_path is None):
            path_root = os.path.join(self.folder_path, self.project_name.text())
            path_root = path_root.replace('/', '\\')
            path_root = path_root.replace('\\', '\\\\')

            p_id = self.db.add_project(self.project_name.text(), path_root, self.user_id)
        
            if (self.doc_template_check.isChecked()):
                path_main = f"{path_root}\\\\main\\\\"
                
                try:
                    os.makedirs(path_main, exist_ok = True)
                    print(f'Directory created successfully')

                    categories = self.db.get_all_categories()
                    for category in categories:
                        d_path = self.db.add_doc_templates(p_id, path_main, category[0], category[1], self.user_id)
                        doc = Document()
                        doc.save(d_path)
                
                except OSError:
                    print(f'Directory can not be created')
            
            if (self.module_used.lineEdit().text() != ''):
                modules = self.module_used.lineEdit().text().split(", ")

                for module in modules:
                    path_module = f"{path_root}\\\\{module}\\\\"

                    try:
                        self.db.copy_modules(p_id, module, self.user_id)
                        module_path = self.db.get_module_path(module)

                        # Проверяем существование папок и права доступа
                        if not os.path.exists(module_path[0]):
                            print(f'Исходная папка {module_path[0]} не существует.')
                        elif not os.access(module_path[0], os.R_OK):
                            print(f'Нет прав на чтение исходной папки {module_path[0]}.')
                        else:
                            try:
                                self.copy_folder(src=module_path[0], dst=str(path_module))
                                print(f'Папка {module_path[0]} успешно скопирована в {path_root}')
                            except Exception as e:
                                print(f'Произошла ошибка при копировании: {e}')
                        
                    except OSError:
                        print(f'Directory can not be created')
            
            os.system('start ' + path_root)

        else:
            QMessageBox.information(self, "Ошибка!", "Пожалуйста, введите название проекта.", QMessageBox.StandardButton.Ok)
        
        self.project_name.clear()
        self.project_path.setPlaceholderText('путь к папке проекта')
        self.doc_template_check.setChecked(False)
        self.get_modules()

    def copy_folder(self, src=None, dst=None):
        # Убедимся, что целевая директория существует
        if not os.path.exists(dst):
            os.makedirs(dst)
        
        # Копируем папку src в папку dst
        shutil.copytree(src, dst, dirs_exist_ok=True)
    
    def choose_folder(self):
        tkinter.Tk().withdraw()
        self.folder_path = filedialog.askdirectory()
        self.project_path.setReadOnly(True)
        self.project_path.setPlaceholderText(self.folder_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreateProject(user_id=1)
    window.show()
    sys.exit(app.exec())
