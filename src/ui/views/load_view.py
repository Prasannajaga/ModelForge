from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt
from src.styles.theme import (
    OPTIMIZE_VIEW_STYLE, CARD_STYLE, GROUP_TITLE_STYLE, 
    INPUT_STYLE, BUTTON_PRIMARY_STYLE, TEXT_SECONDARY, 
    ACCENT_BLUE, INPUT_BG
)

class LoadView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(OPTIMIZE_VIEW_STYLE)
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. Load Model Section
        load_card, load_layout = self.create_card()
        load_layout.addWidget(self.create_group_title("Load Model"))
        
        file_row = QHBoxLayout()
        file_label = QLabel("Model File:")
        file_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select a trained model file...")
        self.file_input.setStyleSheet(INPUT_STYLE)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet(f"background-color: {ACCENT_BLUE}; color: white; border: none; padding: 5px 10px; border-radius: 4px;")
        browse_btn.clicked.connect(self.browse_model_file)
        
        file_row.addWidget(file_label)
        file_row.addWidget(self.file_input, 1)
        file_row.addWidget(browse_btn)
        load_layout.addLayout(file_row)
        
        load_btn = QPushButton("LOAD MODEL")
        load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        load_btn.setStyleSheet(BUTTON_PRIMARY_STYLE)
        load_btn.clicked.connect(self.load_model)
        load_layout.addWidget(load_btn)
        
        self.load_status = QLabel("Status: No model loaded")
        self.load_status.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        load_layout.addWidget(self.load_status)
        
        main_layout.addWidget(load_card)
        
        # 2. Test Interface Section
        test_card, test_layout = self.create_card()
        test_layout.addWidget(self.create_group_title("Test Model"))
        
        # Input Text
        input_label = QLabel("Input Text:")
        input_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        test_layout.addWidget(input_label)
        
        self.test_input = QTextEdit()
        self.test_input.setPlaceholderText("Enter text to test...")
        self.test_input.setStyleSheet(INPUT_STYLE)
        self.test_input.setMaximumHeight(100)
        test_layout.addWidget(self.test_input)
        
        # Run Button
        run_btn = QPushButton("RUN INFERENCE")
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        run_btn.setStyleSheet(BUTTON_PRIMARY_STYLE)
        run_btn.clicked.connect(self.run_inference)
        test_layout.addWidget(run_btn)
        
        # Output Text
        output_label = QLabel("Output:")
        output_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        test_layout.addWidget(output_label)
        
        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setPlaceholderText("Results will appear here...")
        self.test_output.setStyleSheet(f"{INPUT_STYLE} background-color: {INPUT_BG};")
        test_layout.addWidget(self.test_output)
        
        main_layout.addWidget(test_card)
        main_layout.addStretch()

    def create_card(self):
        card = QFrame()
        card.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        return card, layout
        
    def create_group_title(self, text):
        label = QLabel(text)
        label.setStyleSheet(GROUP_TITLE_STYLE)
        return label

    def browse_model_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "Model Files (*.pt *.pth *.onnx *.pb *.h5)")
        if file_path:
            self.file_input.setText(file_path)

    def load_model(self):
        # Mock load logic
        if self.file_input.text():
            self.load_status.setText(f"Status: Model loaded from {self.file_input.text()}")
        else:
            self.load_status.setText("Status: Error - No file selected")

    def run_inference(self):
        # Mock inference logic
        input_text = self.test_input.toPlainText()
        if input_text:
            self.test_output.setText(f"Simulated output for: '{input_text}'")
        else:
            self.test_output.setText("Please enter input text.")
