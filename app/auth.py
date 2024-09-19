# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from db import DatabaseHandler
from main import MainWindow

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self.initUI()
        self.load_stylesheet('app/styles.qss')
        self.init_signal_slot()
    
    def load_stylesheet(self, stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)
    
    def init_signal_slot(self):
        # self.register_button.clicked.connect(self.register)
        self.login_button.clicked.connect(self.login)
    
    def initUI(self):
        self.resize(300, 200)

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
        
        self.username_label = QLabel('логин:', parent=self.frame)
        self.username_input = QLineEdit(parent=self.frame)

        self.password_label = QLabel('пароль:', parent=self.frame)
        self.password_input = QLineEdit(parent=self.frame)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # self.register_button = QPushButton('зарегистрироваться')
        self.login_button = QPushButton('войти')

        self.vbox.addWidget(self.username_label)
        self.vbox.addWidget(self.username_input)
        self.vbox.addWidget(self.password_label)
        self.vbox.addWidget(self.password_input)
        self.vbox.addWidget(self.login_button)
        # self.vbox.addWidget(self.register_button)
        
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.setWindowTitle('Авторизация')

    # def register(self):
    #     username = self.username_input.text()
    #     password = self.password_input.text()
    #     # Здесь должен быть код регистрации пользователя в базе данных

    #     QMessageBox.information(self, 'Регистрация', 'Пользователь успешно зарегистрирован!')

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user_id = self.db.check_auth_data(username, password)
        if user_id:
            QMessageBox.information(self, 'Авторизация', 'Вы успешно вошли в систему!')

            self.main_window = MainWindow(user_id=user_id[0])
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Авторизация', 'Неверный логин или пароль!')
