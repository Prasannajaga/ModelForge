from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QComboBox, QLineEdit, QPushButton, QRadioButton, 
    QApplication, QProgressBar, QCheckBox, QStackedLayout,
    QFileDialog
)

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.styles.theme import (
    OPTIMIZE_VIEW_STYLE, CARD_STYLE, GROUP_TITLE_STYLE, 
    INPUT_STYLE, BUTTON_PRIMARY_STYLE, UPLOAD_WIDGET_STYLE, 
    TAB_BUTTON_STYLE, CHECKBOX_STYLE, TEXT_COLOR, TEXT_SECONDARY, ACCENT_BLUE,
    PANEL_BG, BORDER_COLOR
)
from styles.theme import INPUT_BG 
from services.convert_service import ConvertOnnxModel
from services.quantize_service import QuantizeModel
from services.transformers_service import TransformersService

class OptimizeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(OPTIMIZE_VIEW_STYLE)
        
        # Services
        self.converter = ConvertOnnxModel()
        self.quantizer = QuantizeModel()
        self.transformers_service = TransformersService()
        
        # State
        self.start_model_path = None
        self.calib_data_path = None
        
        # Main Layout: Vertical (Tabs on top, Content below)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. Custom Tab Bar
        self.tab_layout = QHBoxLayout()
        self.tab_layout.setSpacing(0)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.btn_convert = self.create_tab_button("Convert to ONNX", True)
        self.btn_quantize = self.create_tab_button("Quantize ONNX", False)
        
        self.tab_layout.addWidget(self.btn_convert)
        self.tab_layout.addWidget(self.btn_quantize)
        self.tab_layout.addStretch() # Push tabs to the left
        
        main_layout.addLayout(self.tab_layout)
        
        # 2. Content Stack
        self.stack = QStackedLayout()
        
        # Panel 1: Convert
        self.convert_panel = self.create_convert_panel()
        self.stack.addWidget(self.convert_panel)
        
        # Panel 2: Quantize
        self.quantize_panel = self.create_quantize_panel()
        self.stack.addWidget(self.quantize_panel)
        
        main_layout.addLayout(self.stack)
        
        # Connect Tabs
        self.btn_convert.clicked.connect(lambda: self.switch_tab(0))
        self.btn_quantize.clicked.connect(lambda: self.switch_tab(1))

    def create_tab_button(self, text, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(TAB_BUTTON_STYLE)
        # Fixed width for tabs to look like the mockup potentially, or let them expand
        btn.setMinimumWidth(200) 
        return btn

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_convert.setChecked(index == 0)
        self.btn_quantize.setChecked(index == 1)

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

    def create_upload_widget(self, text, subtext, icon_text="↑", callback=None): 
        widget = QFrame()
        widget.setStyleSheet(UPLOAD_WIDGET_STYLE)
        widget.setMinimumHeight(100)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Make clickable
        if callback:
             widget.mousePressEvent = lambda e: callback()
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"font-size: 24px; color: {TEXT_SECONDARY}; margin-bottom: 5px; background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(text)
        text_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; background: transparent;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        if subtext:
            sub_label = QLabel(subtext)
            sub_label.setStyleSheet(f"color: {ACCENT_BLUE}; font-size: 12px; background: transparent;")
            sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sub_label)
            
        return widget

    def open_file_dialog(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "Model Files (*.pt *.pth *.onnx *.pb *.h5)")
        if file_path:
            line_edit.setText(file_path)

    def create_convert_panel(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(15)

        # 1. Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold;")
        
        self.mode_torch = QRadioButton("Torch (Local File)")
        self.mode_torch.setChecked(True)
        self.mode_torch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_torch.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        
        self.mode_transformers = QRadioButton("Transformers (HuggingFace)")
        self.mode_transformers.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_transformers.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_torch)
        mode_layout.addWidget(self.mode_transformers)
        mode_layout.addStretch()
        
        layout.addLayout(mode_layout)

        # -------------------------
        # TORCH CONTAINER
        # -------------------------
        self.torch_container = QWidget()
        torch_layout = QVBoxLayout(self.torch_container)
        torch_layout.setContentsMargins(0,0,0,0)
        torch_layout.setSpacing(15)

        # 1. Source Model Card
        card1, l1 = self.create_card()
        l1.addWidget(self.create_group_title("Source Model"))
        
        # Framework Dropdown
        frame_layout = QHBoxLayout()
        frame_label = QLabel("Framework:")
        frame_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.frame_combo = QComboBox()
        self.frame_combo.addItems(["PyTorch (.pt, .pth)",  "TensorFlow, Keras (.h5, .keras)"])
        self.frame_combo.setStyleSheet(INPUT_STYLE)
        self.frame_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        frame_layout.addWidget(frame_label)
        frame_layout.addWidget(self.frame_combo, 1)
        l1.addLayout(frame_layout)
        
        # Upload Area
        self.upload_widget_convert = self.create_upload_widget("Click to Upload Source Model", "Supports .pt, .pb, .h5", "↑", self.select_source_model)
        l1.addWidget(self.upload_widget_convert) 
        torch_layout.addWidget(card1)
        
        # 2. Conversion Config Card
        card2, l2 = self.create_card()
        l2.addWidget(self.create_group_title("Conversion Configuration"))
        
        row1 = QHBoxLayout()
        # Input Shapes
        # shape_layout = QVBoxLayout()
        # shape_label = QLabel("Input Shapes (Name: Shape)")
        # shape_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.shape_input = QLineEdit("")
        self.shape_input.setStyleSheet(INPUT_STYLE)
        # shape_layout.addWidget(shape_label)
        # shape_layout.addWidget(self.shape_input)
        
        # Opset Version
        opset_layout = QVBoxLayout()
        opset_label = QLabel("Opset Version")
        opset_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.opset_combo = QComboBox()
        self.opset_combo.addItems(["18", "16", "15"])
        self.opset_combo.setStyleSheet(INPUT_STYLE)
        opset_layout.addWidget(opset_label)
        opset_layout.addWidget(self.opset_combo)
        
        # row1.addLayout(shape_layout, 2)
        row1.addLayout(opset_layout, 1)
        l2.addLayout(row1)
        
        # Buttons Row
        row2 = QHBoxLayout() 
        self.opt_check = QCheckBox("Apply Basic Optimizations")
        self.opt_check.setChecked(True)
        self.opt_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.opt_check.setStyleSheet(CHECKBOX_STYLE)
         
        row2.addWidget(self.opt_check)
        l2.addLayout(row2)
        torch_layout.addWidget(card2)
        
        # 3. Action & Output Card
        card3, l3 = self.create_card()
        l3.addWidget(self.create_group_title("Action & Output"))
        
        # Filename Input
        file_layout = QHBoxLayout()
        file_label = QLabel("Output Filename:")
        file_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.file_input_convert = QLineEdit("bert_model.onnx")
        self.file_input_convert.setStyleSheet(INPUT_STYLE)
        browse_out_btn = QPushButton("Browse")
        browse_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_out_btn.setStyleSheet(f"background-color: {ACCENT_BLUE}; color: white; border: none; padding: 5px 10px; border-radius: 4px;")
        browse_out_btn.clicked.connect(lambda: self.open_file_dialog(self.file_input_convert))

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input_convert, 1)
        file_layout.addWidget(browse_out_btn)
        l3.addLayout(file_layout)
        
        # Convert Button
        convert_btn = QPushButton("CONVERT MODEL")
        convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_btn.setStyleSheet(BUTTON_PRIMARY_STYLE)
        convert_btn.clicked.connect(self.run_conversion)
        l3.addWidget(convert_btn)
        
        # Status
        self.status_label_convert = QLabel("Status: Ready to convert")
        self.status_label_convert.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        l3.addWidget(self.status_label_convert)
        
        torch_layout.addWidget(card3)

        layout.addWidget(self.torch_container)

        # -------------------------
        # TRANSFORMERS CONTAINER
        # -------------------------
        self.transformers_container = QWidget()
        self.transformers_container.setVisible(False) # Hidden by default
        trans_layout = QVBoxLayout(self.transformers_container)
        trans_layout.setContentsMargins(0,0,0,0)
        trans_layout.setSpacing(15)

        # Transformers Configuration Card
        card_t, lt = self.create_card()
        lt.addWidget(self.create_group_title("Transformers Configuration"))

        # Model ID Input
        mid_layout = QVBoxLayout()
        mid_label = QLabel("Model ID (HuggingFace):")
        mid_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.hf_model_id = QLineEdit("sentence-transformers/all-MiniLM-L6-v2")
        self.hf_model_id.setPlaceholderText("e.g. sentence-transformers/all-MiniLM-L6-v2")
        self.hf_model_id.setStyleSheet(INPUT_STYLE)
        mid_layout.addWidget(mid_label)
        mid_layout.addWidget(self.hf_model_id)
        lt.addLayout(mid_layout)

        # Output Filename Input
        hout_layout = QVBoxLayout()
        hout_label = QLabel("Output Filename:")
        hout_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.hf_output_file = QLineEdit("model.onnx")
        self.hf_output_file.setStyleSheet(INPUT_STYLE)
        hout_layout.addWidget(hout_label)
        hout_layout.addWidget(self.hf_output_file)
        lt.addLayout(hout_layout)

        # Convert Button
        hf_convert_btn = QPushButton("CONVERT & DOWNLOAD")
        hf_convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hf_convert_btn.setStyleSheet(BUTTON_PRIMARY_STYLE)
        hf_convert_btn.clicked.connect(self.run_hf_conversion) # Connected now
        lt.addWidget(hf_convert_btn)

        # Download Status Label
        self.status_label_hf = QLabel("Status: Ready to download")
        self.status_label_hf.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        lt.addWidget(self.status_label_hf)

        trans_layout.addWidget(card_t)
        trans_layout.addStretch()

        layout.addWidget(self.transformers_container)

        # Logic for switching
        self.mode_torch.toggled.connect(self.toggle_convert_mode)
        self.mode_transformers.toggled.connect(self.toggle_convert_mode)

        layout.addStretch()
        return container
    
    def toggle_convert_mode(self):
        is_torch = self.mode_torch.isChecked()
        self.torch_container.setVisible(is_torch)
        self.transformers_container.setVisible(not is_torch)



    class HFConversionWorker(QThread):
        finished_signal = pyqtSignal(bool, str)

        def __init__(self, service: TransformersService, model_id, output_path):
            super().__init__()
            self.service = service
            self.model_id = model_id
            self.output_path = output_path

        def run(self):  
            try:
                success = self.service.convert_from_hub(self.model_id, self.output_path)
                if success:
                    self.finished_signal.emit(True, f"Status: Success - Saved to {self.output_path}")
                else:
                    self.finished_signal.emit(False, "Status: Failed - Check console/logs")
            except Exception as e:
                self.finished_signal.emit(False, f"Status: Error - {str(e)}")

    def run_hf_conversion(self):
        model_id = self.hf_model_id.text()
        output_file = self.hf_output_file.text()
        
        if not model_id:
            self.status_label_hf.setText("Status: Error - Model ID required")
            return
            
        self.status_label_hf.setText(f"Status: Downloading and converting {model_id}...")
        
        # Disable inputs during processing
        self.hf_model_id.setEnabled(False)
        self.hf_output_file.setEnabled(False)
        
        # Create and start worker thread
        self.hf_worker = self.HFConversionWorker(self.transformers_service, model_id, output_file)
        self.hf_worker.finished_signal.connect(self.on_hf_conversion_finished)
        self.hf_worker.start()

    def on_hf_conversion_finished(self, success, message):
        self.status_label_hf.setText(message)
        # Re-enable inputs
        self.hf_model_id.setEnabled(True)
        self.hf_output_file.setEnabled(True)


    def create_quantize_panel(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(15)
        
        # 1. ONNX Model Input
        card1, l1 = self.create_card()
        l1.addWidget(self.create_group_title("ONNX Model Input"))
        
        input_row = QHBoxLayout()
        input_label = QLabel("ONNX Model")
        input_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.input_edit_quant = QLineEdit("bert_model.onnx")
        self.input_edit_quant.setStyleSheet(INPUT_STYLE)
        browse_btn = QPushButton("Browse")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet(f"background-color: {ACCENT_BLUE}; color: white; border: none; padding: 5px 10px; border-radius: 4px;")
        browse_btn.clicked.connect(lambda: self.open_file_dialog(self.input_edit_quant))
        
        input_row.addWidget(input_label)
        input_row.addWidget(self.input_edit_quant)
        input_row.addWidget(browse_btn)
        l1.addLayout(input_row)
        layout.addWidget(card1)
        
        # 2. Quantization Strategy
        card2, l2 = self.create_card()
        l2.addWidget(self.create_group_title("Quantization Strategy"))
        
        radio_layout = QHBoxLayout()
        self.quant_strategy_dynamic = QRadioButton("Dynamic")
        self.quant_strategy_dynamic.setChecked(True)
        self.quant_strategy_dynamic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quant_strategy_dynamic.setStyleSheet(f"color: {TEXT_COLOR};")
        self.quant_strategy_static = QRadioButton("Static")
        self.quant_strategy_static.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quant_strategy_static.setStyleSheet(f"color: {TEXT_COLOR};")
        radio_layout.addWidget(self.quant_strategy_dynamic)
        radio_layout.addWidget(self.quant_strategy_static)
        radio_layout.addStretch()
        l2.addLayout(radio_layout)
        layout.addWidget(card2)
        
        # 3. Calibration Config
        card3, l3 = self.create_card()
        l3.addWidget(self.create_group_title("Calibration Config"))
        
        calib_layout = QHBoxLayout()
        self.upload_widget_calib = self.create_upload_widget("Data upload,", "upload", "↑", self.select_calib_data)
        
        method_layout = QVBoxLayout()
        method_label = QLabel("Method")
        method_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["MinMax", "Entropy", "Percentile"]) 
        self.method_combo.setStyleSheet(INPUT_STYLE)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        
        calib_layout.addWidget(self.upload_widget_calib, 1)
        calib_layout.addLayout(method_layout, 1)
        l3.addLayout(calib_layout)
        layout.addWidget(card3)
        
        # 4. Format & Settings
        card4, l4 = self.create_card()
        l4.addWidget(self.create_group_title("Format & Settings"))
        
        # Radio buttons for type
        # Radio buttons for type
        type_layout = QHBoxLayout()
        self.type_qdq = QRadioButton("QDQ/QOperator")
        self.type_qdq.setChecked(True)
        self.type_qdq.setCursor(Qt.CursorShape.PointingHandCursor)
        self.type_qdq.setStyleSheet(f"color: {TEXT_COLOR};")
        self.type_int8 = QRadioButton("INT8/UINT8")
        self.type_int8.setCursor(Qt.CursorShape.PointingHandCursor)
        self.type_int8.setStyleSheet(f"color: {TEXT_COLOR};")
        
        # Toggle Switch (Simulated with CheckBox for now)
        self.per_channel_check = QCheckBox("Per-Channel")
        self.per_channel_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.per_channel_check.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_COLOR}; spacing: 8px; }}
            QCheckBox::indicator {{ width: 32px; height: 18px; border-radius: 9px; background-color: {INPUT_BG}; border: 1px solid {BORDER_COLOR}; }}
            QCheckBox::indicator:checked {{ background-color: {ACCENT_BLUE}; border: 1px solid {ACCENT_BLUE}; }}
        """)
        
        type_layout.addWidget(self.type_qdq)
        type_layout.addWidget(self.type_int8)
        type_layout.addStretch()
        type_layout.addWidget(self.per_channel_check)
        l4.addLayout(type_layout)
        layout.addWidget(card4)
        
        # 5. Action & Output
        card5, l5 = self.create_card()
        l5.addWidget(self.create_group_title("Action & Output"))
        
        # Filename
        out_row = QHBoxLayout()
        out_lbl = QLabel("Output Filename:")
        out_lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.out_edt_quant = QLineEdit("bert_model_quantized.onnx")
        self.out_edt_quant.setStyleSheet(INPUT_STYLE)
        out_row.addWidget(out_lbl)
        out_row.addWidget(self.out_edt_quant, 1)
        l5.addLayout(out_row)
        
        # Quantize Button
        quant_btn = QPushButton("QUANTIZE")
        quant_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        quant_btn.setStyleSheet(BUTTON_PRIMARY_STYLE)
        quant_btn.clicked.connect(self.run_quantization)
        l5.addWidget(quant_btn)
        
        # Status
        self.status_label_quant = QLabel("Status: Ready to quantize")
        self.status_label_quant.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        l5.addWidget(self.status_label_quant)
        
        layout.addWidget(card5)
        layout.addStretch()
        return container

    def select_source_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Source Model", "", "Model Files (*.pt *.pth *.pb *.h5)")
        if file_path:
            self.start_model_path = file_path
            # Update UI to show filename
            layout = self.upload_widget_convert.layout()
            # Assuming 2nd label is text_label (index 1)
            filename = file_path.split("/")[-1]
            layout.itemAt(1).widget().setText(f"{filename} - Selected")

    def select_calib_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Calibration Data", "", "Data Files (*.npy *.json *.txt)")
        if file_path:
            self.calib_data_path = file_path
            layout = self.upload_widget_calib.layout()
            filename = file_path.split("/")[-1]
            layout.itemAt(1).widget().setText(f"{filename} - Selected")

    def run_conversion(self):
        if not self.start_model_path:
            self.status_label_convert.setText("Status: Error - No source model selected")
            return
            
        output_path = self.file_input_convert.text()
        framework = self.frame_combo.currentText()
        shapes = self.shape_input.text()
        opset = int(self.opset_combo.currentText().split()[0])
        optimize = self.opt_check.isChecked()
        
        self.status_label_convert.setText("Status: Converting...")
        # Since logic might be blocking, ideally use QThread. For now, calling directly.
        try:
            success = self.converter.convert(
                self.start_model_path,
                output_path,
                framework,
                shapes,
                opset,
                optimize
            )
            if success:
                self.status_label_convert.setText(f"Status: Success - Saved to {output_path}")
            else:
                self.status_label_convert.setText("Status: Failed")
        except Exception as e:
            self.status_label_convert.setText(f"Status: Error - {str(e)}")

    def run_quantization(self):
        input_model = self.input_edit_quant.text()
        output_model = self.out_edt_quant.text()
        strategy = "Dynamic" if self.quant_strategy_dynamic.isChecked() else "Static"
        calib_method = self.method_combo.currentText()
        quant_type = "QDQ" if self.type_qdq.isChecked() else "INT8"
        per_channel = self.per_channel_check.isChecked()
        
        self.status_label_quant.setText("Status: Quantizing...")
        try:
            success = self.quantizer.quantize(
                input_model,
                output_model,
                strategy,
                calib_method,
                quant_type,
                per_channel,
                self.calib_data_path
            )
            if success:
                self.status_label_quant.setText("Status: Success - Quantized model saved")
            else:
                self.status_label_quant.setText("Status: Failed")
        except Exception as e:
            self.status_label_quant.setText(f"Status: Error - {str(e)}")
            print(f"Quantization Failed: {e}")
