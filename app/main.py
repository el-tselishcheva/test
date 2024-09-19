import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from filter_docs import FilterDocs
from create_project import CreateProject

class MainWindow(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.initUI()
        self.load_stylesheet('app/styles.qss')

        self.init_signal_slot()
        self.init_listwidget()
        self.init_stackwidget()
    
    def load_stylesheet(self, stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)
    
    def init_signal_slot(self):
        # Connect signals and slots for menu button and side menu
        self.menu_btn.toggled['bool'].connect(self.side_menu.setHidden)
        self.menu_btn.toggled['bool'].connect(self.title_label.setHidden)
        self.menu_btn.toggled['bool'].connect(self.side_menu_icon_only.setVisible)

        # Connect signals and slots for switching between menu items
        self.side_menu.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu_icon_only.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu.currentRowChanged['int'].connect(self.side_menu_icon_only.setCurrentRow)
        self.side_menu_icon_only.currentRowChanged['int'].connect(self.side_menu.setCurrentRow)
        self.menu_btn.toggled.connect(self.button_icon_change)
    
    def initUI(self):
        # self.resize(300, 200)
        self.setWindowTitle("Архивная система документации")

        self.centralwidget = QWidget()
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)

        self.title_frame = QFrame(parent=self.centralwidget)
        self.title_frame.setObjectName("title_frame")
        self.title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.title_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.title_frame)

        self.title_label = QLabel(parent=self.title_frame)
        self.title_label.setText("Меню")
        self.horizontalLayout.addWidget(self.title_label)

        self.menu_btn = QPushButton(parent=self.title_frame)
        self.menu_btn.setText("")
        self.menu_btn.setIcon(QIcon("app/icons/close.svg"))
        self.menu_btn.setIconSize(QSize(30, 30))
        self.menu_btn.setCheckable(True)
        self.menu_btn.setChecked(False)
        self.horizontalLayout.addWidget(self.menu_btn)

        self.gridLayout.addWidget(self.title_frame, 0, 0, 1, 2)

        self.main_content = QStackedWidget(parent=self.centralwidget)
        self.gridLayout.addWidget(self.main_content, 0, 2, 2, 1)

        self.side_menu_icon_only = QListWidget(parent=self.centralwidget)
        self.side_menu_icon_only.setMaximumSize(QSize(55, 16777215))
        self.side_menu_icon_only.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu_icon_only.hide()
        self.gridLayout.addWidget(self.side_menu_icon_only, 1, 0, 1, 1)

        self.side_menu = QListWidget(parent=self.centralwidget)
        self.side_menu.setMaximumSize(QSize(200, 16777215))
        self.side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.gridLayout.addWidget(self.side_menu, 1, 1, 1, 1)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar()
        self.menubar.setGeometry(QRect(0, 0, 875, 22))
        self.setMenuBar(self.menubar)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.menu_list = [
            {
                "name": "Новый проект",
                "icon": "app/icons/add.svg",
                "widget": CreateProject()
            },
            {
                "name": "Поиск документов",
                "icon": "app/icons/search.svg",
                "widget": FilterDocs()
            }
        ]
    
    def init_listwidget(self):
        # Initialize the side menu and side menu with icons only
        self.side_menu_icon_only.clear()
        self.side_menu.clear()

        for menu in self.menu_list:
            # Set items for the side menu with icons only
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            self.side_menu_icon_only.addItem(item)
            self.side_menu_icon_only.setCurrentRow(0)

            # Set items for the side menu with icons and text
            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item_new.setText(menu.get("name"))
            self.side_menu.addItem(item_new)
            self.side_menu.setCurrentRow(0)

    def init_stackwidget(self):
        # Initialize the stack widget with content pages
        widget_list = self.main_content.findChildren(QWidget)
        for widget in widget_list:
            self.main_content.removeWidget(widget)

        for menu in self.menu_list:
            new_page = menu.get("widget")
            self.main_content.addWidget(new_page)
    
    def button_icon_change(self, status):
        # Change the menu button icon based on its status
        if status:
            self.menu_btn.setIcon(QIcon("app/icons/open.svg"))
        else:
            self.menu_btn.setIcon(QIcon("app/icons/close.svg"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(user_id=1)
    window.show()
    sys.exit(app.exec())
