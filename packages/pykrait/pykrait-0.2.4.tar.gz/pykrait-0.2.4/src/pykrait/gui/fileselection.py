import os
import csv
from pathlib import Path
import yaml

from PySide6.QtWidgets import (
    QWidget, QPushButton, QFileDialog,
    QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox,
    QLineEdit, QGroupBox, QButtonGroup, QRadioButton, QProgressBar,
    QStackedWidget, QSizePolicy, QLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from pykrait.pipeline.pipeline import AnalysisParameters, AnalysisOutput
from pykrait.gui.async_workers import ExtractIntensitiesWorker

class FileSelectionWindow(QWidget):
    analysis_complete = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Microscopy & Model File Selection")
        self.setMinimumSize(500, 550)

        self.config_path = Path.home() / ".pykrait" / "settings.yaml"
        self.config = self.load_settings()

        self.image_path = None
        self.model_path = None
        self.label_image_path = None
        self.mean_intensities_path = None
        self.analysis_param_path = None

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        #self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(8)

        # --- Entry Point Selection ---
        entry_group = QGroupBox("Entry Point")
        entry_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        entry_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        entry_layout = QHBoxLayout()
        self.model_radio = QRadioButton("Video + Cellpose Model")
        self.label_radio = QRadioButton("Video + Label Image")
        self.label_csv_radio = QRadioButton("Video + Label Image + Intensities File")  # NEW
        self.model_radio.setChecked(True)
        entry_layout.addWidget(self.model_radio)
        entry_layout.addWidget(self.label_radio)
        entry_layout.addWidget(self.label_csv_radio)
        entry_group.setLayout(entry_layout)
        self.main_layout.addWidget(entry_group)

        # --- File Selection Group ---
        self.file_stack = QStackedWidget()
        self.file_stack.addWidget(self.create_video_model_page())   # index 0
        self.file_stack.addWidget(self.create_video_labels_page())  # index 1
        self.file_stack.addWidget(self.create_video_labels_csv_page())  # index 2
        
        # Connect radio buttons to change stack
        self.model_radio.toggled.connect(lambda: self.file_stack.setCurrentIndex(0))
        self.label_radio.toggled.connect(lambda: self.file_stack.setCurrentIndex(1))
        self.label_csv_radio.toggled.connect(lambda: self.file_stack.setCurrentIndex(2))


        # keep stack height snug to current page
        def _sync_file_stack_height():
            w = self.file_stack.currentWidget()
            h = w.sizeHint().height()
            self.file_stack.setMinimumHeight(h)
            self.file_stack.setMaximumHeight(h)
            self.file_stack.updateGeometry()

        # connect after index changes
        self.file_stack.currentChanged.connect(lambda _: _sync_file_stack_height())
        _sync_file_stack_height()  # initial

        self.main_layout.addWidget(self.file_stack)

        # --- Analysis Parameter Load Button ---
        self.load_param_button = QPushButton("Load Analysis Parameters")
        self.load_param_button.clicked.connect(self.load_analysis_parameters)
        self.load_param_button.setEnabled(False)  # Start greyed out
        self.main_layout.addWidget(self.load_param_button)

        # --- Analysis Settings Group ---
        self.analysis_stack = QStackedWidget()
        self.analysis_stack.addWidget(self.create_analysis_settings_model())   # index 0
        self.analysis_stack.addWidget(self.create_analysis_settings_other())  # index 1
        
        # Connect radio buttons to change stack
        self.model_radio.toggled.connect(lambda: self.analysis_stack.setCurrentIndex(0))
        self.label_radio.toggled.connect(lambda: self.analysis_stack.setCurrentIndex(1))
        self.label_csv_radio.toggled.connect(lambda: self.analysis_stack.setCurrentIndex(1))


        # keep stack height snug to current page
        def _sync_analysis_stack_height():
            w = self.analysis_stack.currentWidget()
            h = w.sizeHint().height()
            self.analysis_stack.setMinimumHeight(h)
            self.analysis_stack.setMaximumHeight(h)
            self.analysis_stack.updateGeometry()

        # connect after index changes
        self.analysis_stack.currentChanged.connect(lambda _: _sync_analysis_stack_height())
        _sync_analysis_stack_height()  # initial

        self.main_layout.addWidget(self.analysis_stack)

        # --- Confirm Button & Progress Bar ---
        confirm_layout = QVBoxLayout()
        confirm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.confirm_button = QPushButton("Confirm and Proceed")
        self.confirm_button.setStyleSheet("font-weight: bold; padding: 8px 16px; font-size: 14px;")
        self.confirm_button.clicked.connect(self.confirm_selection)
        confirm_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(300)
        confirm_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress_label = QLabel(self)
        self.progress_label.setText("")  # Start empty
        confirm_layout.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addLayout(confirm_layout)

        self.setLayout(self.main_layout)

    # ---------- SETTINGS LOAD/SAVE ----------
    def load_settings(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def save_settings(self):
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f)

    def get_last_directory(self, key: str):
        return self.config.get(key, str(Path.home()))

    def set_last_directory(self, key: str, path: str):
        self.config[key] = os.path.dirname(path)
        self.save_settings()

    # ---------- FILE SELECTION LAYOUT ----------
    def create_video_model_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)   # keep the page flush with the group box
        page_layout.setSpacing(0)
        page_layout.setSizeConstraint(QLayout.SetMinimumSize)


        group = QGroupBox("File Selection")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(6)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Video
        self.btn_video_vm = QPushButton("Browse Video")
        self.lbl_video_vm = QLabel("No file selected")
        self.lbl_video_vm.setWordWrap(True)
        self.btn_video_vm.clicked.connect(lambda: self.select_image(label=self.lbl_video_vm))
        g_layout.addWidget(self.btn_video_vm)
        g_layout.addWidget(self.lbl_video_vm)

        # Model
        self.btn_model_vm = QPushButton("Browse Cellpose Model")
        self.lbl_model_vm = QLabel("No file selected")
        self.lbl_model_vm.setWordWrap(True)
        self.btn_model_vm.clicked.connect(lambda: self.select_model(label=self.lbl_model_vm))
        g_layout.addWidget(self.btn_model_vm)
        g_layout.addWidget(self.lbl_model_vm)

        g_layout.addStretch(1)
        page_layout.addWidget(group)
        return page

    def create_video_labels_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)   # keep the page flush with the group box
        page_layout.setSpacing(0)
        page_layout.setSizeConstraint(QLayout.SetMinimumSize)


        group = QGroupBox("File Selection")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(6)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Video
        self.btn_video_vl = QPushButton("Browse Video")
        self.lbl_video_vl = QLabel("No file selected")
        self.lbl_video_vl.setWordWrap(True)
        self.btn_video_vl.clicked.connect(lambda: self.select_image(label=self.lbl_video_vl))
        g_layout.addWidget(self.btn_video_vl)
        g_layout.addWidget(self.lbl_video_vl)

        # Labels
        self.btn_labels_vl = QPushButton("Browse Label Image")
        self.lbl_labels_vl = QLabel("No file selected")
        self.lbl_labels_vl.setWordWrap(True)
        self.btn_labels_vl.clicked.connect(lambda: self.select_label_image(label=self.lbl_labels_vl))
        g_layout.addWidget(self.btn_labels_vl)
        g_layout.addWidget(self.lbl_labels_vl)

        g_layout.addStretch(1)
        page_layout.addWidget(group)
        return page

    def create_video_labels_csv_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)   # keep the page flush with the group box
        page_layout.setSpacing(0)
        page_layout.setSizeConstraint(QLayout.SetMinimumSize)

        group = QGroupBox("File Selection")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(6)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Video
        self.btn_video_vlc = QPushButton("Browse Video")
        self.lbl_video_vlc = QLabel("No file selected")
        self.lbl_video_vlc.setWordWrap(True)
        self.btn_video_vlc.clicked.connect(lambda: self.select_image(label=self.lbl_video_vlc))
        g_layout.addWidget(self.btn_video_vlc)
        g_layout.addWidget(self.lbl_video_vlc)

        # Labels
        self.btn_labels_vlc = QPushButton("Browse Label Image")
        self.lbl_labels_vlc = QLabel("No file selected")
        self.lbl_labels_vlc.setWordWrap(True)
        self.btn_labels_vlc.clicked.connect(lambda: self.select_label_image(label=self.lbl_labels_vlc))
        g_layout.addWidget(self.btn_labels_vlc)
        g_layout.addWidget(self.lbl_labels_vlc)

        # CSV
        self.btn_csv_vlc = QPushButton("Browse Raw Intensities")
        self.lbl_csv_vlc = QLabel("No file selected")
        self.lbl_csv_vlc.setWordWrap(True)
        self.btn_csv_vlc.clicked.connect(lambda: self.select_mean_intensities(label=self.lbl_csv_vlc))
        g_layout.addWidget(self.btn_csv_vlc)
        g_layout.addWidget(self.lbl_csv_vlc)

        g_layout.addStretch(1)
        page_layout.addWidget(group)
        return page

   # ---------- FILE PICKERS ----------
    def select_image(self, label):
        last_dir = self.get_last_directory("last_image_dir")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Microscopy Image", last_dir,
            filter="Image Files (*.czi *.tif *.tiff);;All Files (*)"
        )
        if path:
            self.image_path = path
            self.set_last_directory("last_image_dir", path)
            filename = os.path.basename(path)
            label.setText(f"Selected Image: {filename}")
            label.setToolTip(path)

            # Look for analysis parameter file in subfolder
            video_stem = Path(path).stem
            settings_dir = Path(path).parent / f"Analysis_{video_stem}"
            param_file = settings_dir / f"{video_stem}_analysis_parameters.csv"
            if param_file.exists():
                self.analysis_param_path = str(param_file)
                self.load_param_button.setEnabled(True)  # Enable if found
            else:
                self.analysis_param_path = None
                self.load_param_button.setEnabled(False)  # Disable if not found

    def select_model(self, label):
        last_dir = self.get_last_directory("last_model_dir")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Cellpose Model", last_dir,
            filter="All Files (*)"
        )
        if path:
            self.model_path = path
            self.set_last_directory("last_model_dir", path)
            filename = os.path.basename(path)
            label.setText(f"Selected Model: {filename}")
            label.setToolTip(path)

    def select_label_image(self, label):
        last_dir = self.get_last_directory("last_image_dir")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Label Image", last_dir,
            filter="Label Images (*masks*);;Image Files (*.tif *.tiff *.npy, *.png);;All Files (*)"
        )
        if path:
            self.label_image_path = path
            filename = os.path.basename(path)
            label.setText(f"Selected Label Image: {filename}")
            label.setToolTip(path)

    def select_mean_intensities(self, label):
        last_dir = self.get_last_directory("last_image_dir")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Raw Intensities", last_dir,
            filter="Raw Intensities CSV (*raw_intensities*.zst);;CSV Files (*.csv.zst);;All Files (*)"
        )
        if path:
            self.mean_intensities_path = path
            filename = os.path.basename(path)
            label.setText(f"Selected Intensity File: {filename}")
            label.setToolTip(path)

    # ---------- ANALYSIS PARAMETER LOADING ----------
    def load_analysis_parameters(self):
        if not self.analysis_param_path or not os.path.exists(self.analysis_param_path):
            QMessageBox.warning(self, "Not Found", "No analysis parameters file found.")
            return

        try:
            params = self.parse_analysis_csv(self.analysis_param_path)
            self.load_param_button.setEnabled(False)  # Start greyed out
            self.load_param_button.setText("Parameters Loaded")
        except Exception as e:
            QMessageBox.critical(self, "Load Failed", f"Could not load parameters:\n{e}")
            return

        # Extract with correct keys (all lowercase)
        tproj_type = params.get("tproj_type", "").upper()
        clahe_value = params.get("clahe_normalize", "").lower()
        frame_interval = params.get("frame_interval", "")
        model_path = params.get("cellpose_model_path", "")

        # Update UI fields
        if tproj_type == "STD":
            self.std_button.setChecked(True)
        elif tproj_type == "SUM":
            self.sum_button.setChecked(True)

        self.clahe_checkbox.setChecked(clahe_value in ("1", "true", "yes"))

        if frame_interval:
            self.frame_input.setText(str(frame_interval))

        # Optionally, auto-set model path if model_radio is selected and path is valid
        if model_path and self.model_radio.isChecked() and os.path.exists(model_path):
            self.model_path = model_path
            filename = os.path.basename(model_path)
            self.model_label.setText(f"Selected Model: {filename}")
            self.model_label.setToolTip(model_path)

        QMessageBox.information(self, "Loaded", f"Loaded parameters from {self.analysis_param_path}")

    def parse_analysis_csv(self, csv_path):
        """
        Expects CSV with headers: tproj_type, CLAHE_normalize, frame_interval, cellpose_model_path
        Only the first row is used.
        """
        params = {}
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                params = row  # Use only first row
                break
        # Normalize keys (case-insensitive access)
        params = {k.strip().lower(): v.strip() for k, v in params.items()}
        return params

    # ---------- ANALYSIS SETTINGS  ----------
    def create_analysis_settings_model(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)   # keep the page flush with the group box
        page_layout.setSpacing(0)
        page_layout.setSizeConstraint(QLayout.SetMinimumSize)


        group = QGroupBox("Analysis Settings")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g_layout = QVBoxLayout()
        g_layout.setSpacing(6)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # T-projection method
        tproj_row = QHBoxLayout()
        tproj_label = QLabel("T-projection method (required):")
        tproj_row.addWidget(tproj_label)
        self.tproj_group = QButtonGroup(self)
        self.std_button = QRadioButton("STD")
        self.sum_button = QRadioButton("SUM")
        self.tproj_group.addButton(self.std_button)
        self.tproj_group.addButton(self.sum_button)
        tproj_row.addWidget(self.std_button)
        tproj_row.addWidget(self.sum_button)
        tproj_row.addStretch() 
        g_layout.addLayout(tproj_row)

        # Restore saved T-projection
        saved_proj = self.config.get("t_projection", "STD").upper()
        (self.std_button if saved_proj == "STD" else self.sum_button).setChecked(True)

        # CLAHE
        self.clahe_checkbox = QCheckBox("Apply CLAHE normalization")
        self.clahe_checkbox.setChecked(self.config.get("clahe", False))
        g_layout.addWidget(self.clahe_checkbox)

        # Frame interval
        frame_interval_layout = QHBoxLayout()
        frame_interval_layout.addWidget(QLabel("Frame interval (s, optional):"))
        self.frame_input = QLineEdit()
        self.frame_input.setPlaceholderText("e.g. 2.50")
        if "frame_interval" in self.config:
            self.frame_input.setText(str(self.config["frame_interval"]))
        frame_interval_layout.addWidget(self.frame_input)
        g_layout.addLayout(frame_interval_layout)

        g_layout.addStretch(1)
        group.setLayout(g_layout)
        page_layout.addWidget(group)
        return page

    def create_analysis_settings_other(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)   # keep the page flush with the group box
        page_layout.setSpacing(0)
        page_layout.setSizeConstraint(QLayout.SetMinimumSize)

        group = QGroupBox("Analysis Settings")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(6)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Frame interval
        frame_interval_layout = QHBoxLayout()
        frame_interval_layout.addWidget(QLabel("Frame interval (s, optional):"))
        self.frame_input = QLineEdit()
        self.frame_input.setPlaceholderText("e.g. 2.50")
        if "frame_interval" in self.config:
            self.frame_input.setText(str(self.config["frame_interval"]))
        frame_interval_layout.addWidget(self.frame_input)
        g_layout.addLayout(frame_interval_layout)

        g_layout.addStretch(1)
        page_layout.addWidget(group)
        return page

    # ---------- CONFIRM ----------
    def confirm_selection(self):
        if not self.image_path:
            QMessageBox.warning(self, "Missing File", "Please select a microscopy image.")
            return

        if self.model_radio.isChecked():
            if not self.model_path:
                QMessageBox.warning(self, "Missing File", "Please select a Cellpose model.")
                return
        elif self.label_csv_radio.isChecked() and not self.mean_intensities_path:
            QMessageBox.warning(self, "Missing File", "Please select a mean intensities CSV file.")
            return
        else:
            if not self.label_image_path:
                QMessageBox.warning(self, "Missing File", "Please select a label image.")
                return

        if self.std_button.isChecked():
            tproj = "STD"
        elif self.sum_button.isChecked():
            tproj = "SUM"
        else:
            QMessageBox.warning(self, "Missing Selection", "Please select a T-projection method.")
            return

        clahe = self.clahe_checkbox.isChecked()
        frame_text = self.frame_input.text().strip()
        if frame_text:
            try:
                frame_interval = round(float(frame_text), 2)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Frame interval must be a number (e.g. 2.50).")
                return
            self.config["frame_interval"] = frame_interval
        else:
            self.config.pop("frame_interval", None)

        self.config["t_projection"] = tproj
        self.config["clahe"] = clahe
        self.save_settings()

        # Start progress bar
        self.progress_bar.setVisible(True)
        self.repaint()

        # --- Run Analysis ---
        tproj = "std" if self.std_button.isChecked() else "sum"
        clahe = self.clahe_checkbox.isChecked()
        frame_text = self.frame_input.text().strip()
        frame_interval = float(frame_text) if frame_text else None
        cellpose_model_path = self.model_path if self.model_radio.isChecked() else None
        self.analysis_params = AnalysisParameters(
            tproj_type=tproj,
            CLAHE_normalize=clahe,
            cellpose_model_path=cellpose_model_path,
            frame_interval=frame_interval
        )
        self.output_params = AnalysisOutput(filepath=self.image_path)
        self.output_params.filename = self.output_params.filepath.split("/")[-1]
        self.output_params.masks_path = self.label_image_path if not self.model_radio.isChecked() else None    

        self.thread = QThread()
        if self.model_radio.isChecked():
            mode = "cellpose"
        elif self.label_radio.isChecked():
            mode = "label_image"
        elif self.label_csv_radio.isChecked():
            mode = "csv"
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a valid entry point.")
            return
        self.worker = ExtractIntensitiesWorker(self.analysis_params, self.output_params, mode, self.mean_intensities_path)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_done)
        self.worker.error.connect(self.analysis_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start analysis thread
        self.thread.start()

    # ---------- ANALYSIS WORKER -----------
    def update_progress(self, percent, message):
        self.progress_bar.setValue(percent)
        if hasattr(self, "progress_label"):
            self.progress_label.setText(message)  # Optional if you use a label

    def analysis_done(self, results):
        self.progress_bar.setVisible(False)
        self.analysis_complete.emit(results)

    def analysis_failed(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Analysis Error", error_msg)
        #shut down the thread
        if hasattr(self, '_active_thread') and self._active_thread.isRunning():
            self._active_thread.quit()
            self._active_thread.wait()
        self._active_thread = None
        self._active_worker = None
