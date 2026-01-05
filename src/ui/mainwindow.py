from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt
from src.constants.menu_constants import MENU_ITEMS
from src.styles.theme import (SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, 
                              HEADER_LABEL_STYLE, CONTENT_AREA_STYLE)
from src.ui.views.load_view import LoadView
from src.ui.views.train_view import TrainView
from src.ui.views.optimize_view import OptimizeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model Forge")
        self.resize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout (Horizontal: Sidebar + Content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # Sidebar Title
        title_label = QLabel("Model Forge")
        title_label.setFixedHeight(60)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(HEADER_LABEL_STYLE)
        self.sidebar_layout.addWidget(title_label)
        
        # Content Area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet(CONTENT_AREA_STYLE)
        
        # Dynamic Menu Generation
        self.buttons = {}
        self.pages = {}
        
        # View Mapping
        self.view_mapping = {
            "load_page": LoadView,
            "train_page": TrainView,
            "optimize_page": OptimizeView
        }
        
        for label, page_id in MENU_ITEMS:
            # Create Button
            btn = self.create_sidebar_button(label)
            self.sidebar_layout.addWidget(btn)
            self.buttons[page_id] = btn
            
            # Create Page
            view_class = self.view_mapping.get(page_id)
            if view_class:
                page = view_class()
            else:
                page = QLabel(f"{label} Screen (Missing View)", alignment=Qt.AlignmentFlag.AlignCenter)
                
            self.content_area.addWidget(page)
            self.pages[page_id] = page
            
            # Connect Button
            # Use default argument capture for lambda loop variable
            btn.clicked.connect(lambda checked, p=page: self.content_area.setCurrentWidget(p))

        self.sidebar_layout.addStretch()
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

    def create_sidebar_button(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(SIDEBAR_BUTTON_STYLE)
        return btn
