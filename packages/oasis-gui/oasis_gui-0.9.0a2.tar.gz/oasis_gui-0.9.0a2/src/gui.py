import sys
import os
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTabWidget, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QFileDialog,
    QGridLayout, QGroupBox, QMessageBox, QFormLayout, QDialog, QMenuBar, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap
import pyqtgraph as pg


from oasis.api import OasisBoard  

# -------- Worker Thread for Acquisition --------
class AcquisitionThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(object)  # Emits acquired OasisBoard

    def __init__(self, board: OasisBoard):
        super().__init__()
        self.board = board

    def run(self):
        try:
            self.board.acquire(
                print_log=self.log.emit,
                progress=self.progress.emit
            )
            self.finished.emit(self.board)
        except Exception as e:
            self.log.emit(f"[ERROR] {e}")
            self.finished.emit(None)

# --------- PyQtGraph Data Plot Dialog -----------
class DataPlotDialog(QDialog):
    def __init__(self, board: OasisBoard, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OASIS Data Plot")
        self.setMinimumSize(900, 600)
        layout = QVBoxLayout(self)
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('w')
        layout.addWidget(self.plot_widget)
        self.channel_plots = []
        data = board.OASISData
        t = board.t
        # 4 rows × 2 columns = 8 plots
        for row in range(4):
            for col in range(2):
                plt = self.plot_widget.addPlot(row=row, col=col)
                idx = row * 2 + col
                plt.setLabel('left', f'Ch {idx+1} U/V')
                plt.setLabel('bottom', 'Time t/s')
                plt.showGrid(x=True, y=True)
                if data is not None:
                    plt.plot(t, data[idx], pen=pg.mkPen('b', width=1.2))
                self.channel_plots.append(plt)
        self.setLayout(layout)


# --------- Device/Passive Data Tab Widget -----------
class BoardTab(QWidget):
    def __init__(self, mode="serial", port=None, baudrate=115200, ip=None, tcp_port=5025, board: OasisBoard=None, is_passive=False):
        super().__init__()
        self.mode = mode
        self.port = port
        self.baudrate = baudrate
        self.ip = ip
        self.tcp_port = tcp_port
        self.is_passive = is_passive
        self.data_loaded = False

        if board is not None:
            self.board = board
        else:
            if mode == "serial":
                self.board = OasisBoard(mode="serial", port=port, baudrate=baudrate)
            elif mode == "tcp":
                self.board = OasisBoard(mode="tcp", ip=ip, tcp_port=tcp_port)
            else:
                self.board = OasisBoard(mode="offline")
        self._init_ui()


    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Device Info ---
        self.info_group = QGroupBox("Device Information" if not self.is_passive else "Imported Data Info")
        self.info_text = QLabel("Not connected." if not self.is_passive else "No device. Data imported from file.")
        vbox_info = QVBoxLayout()
        vbox_info.addWidget(self.info_text)
        self.info_group.setLayout(vbox_info)
        self.info_group.setMinimumHeight(80)  # Prevent info panel from shrinking too much

        # --- Acquisition Config (hidden for passive boards) ---
        if not self.is_passive:
            config_group = QGroupBox("Acquisition Configuration")
            form = QFormLayout()
            # --- Set Voltage for all ---
            self.set_all_voltage = QComboBox()
            self.set_all_voltage.addItems(['2.5', '5', '6.25', '10', '12.5'])
            set_all_btn = QPushButton("Set for all")
            set_all_btn.clicked.connect(self.set_all_voltage_ranges)
            grid = QGridLayout()
            grid.addWidget(QLabel("Set for all:"), 0, 0)
            grid.addWidget(self.set_all_voltage, 0, 1)
            grid.addWidget(set_all_btn, 0, 2)
            # --- Per-channel voltage ranges ---
            grid.addWidget(QLabel("Ch."), 1, 0)
            for i in range(8):
                grid.addWidget(QLabel(f"{i+1}"), 1, i+1)
            grid.addWidget(QLabel("Voltage Range in Volts"), 2, 0)
            self.voltage_ranges = [QComboBox() for _ in range(8)]
            for i, combo in enumerate(self.voltage_ranges):
                combo.addItems(['2.5', '5', '6.25', '10', '12.5'])
                combo.setCurrentText('2.5')
                grid.addWidget(combo, 2, i+1)
            # --- Other config fields ---
            self.sample_time = QDoubleSpinBox(); self.sample_time.setValue(2); self.sample_time.setMinimum(0.01)
            self.sample_freq = QSpinBox(); self.sample_freq.setRange(1, 100000); self.sample_freq.setValue(10000)
            self.oversampling = QComboBox(); self.oversampling.addItems(['x1', 'x2', 'x4', 'x8'])
            form.addRow("Sample Time (s):", self.sample_time)
            form.addRow("Sample Frequency (Hz):", self.sample_freq)
            form.addRow("Oversampling:", self.oversampling)
            form.addRow(grid)
            self.level_trigger = QCheckBox("Enable Level Trigger")
            self.trigger_level = QDoubleSpinBox(); self.trigger_level.setRange(0, 100); self.trigger_level.setValue(0.2)
            self.trigger_level.setEnabled(False)
            self.level_trigger.toggled.connect(lambda v: self.trigger_level.setEnabled(v))
            form.addRow(self.level_trigger, self.trigger_level)
            config_group.setLayout(form)
        else:
            config_group = None

        # --- QSplitter for adjustable vertical layout ---
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.info_group)
        if config_group:
            splitter.addWidget(config_group)
        self.info_group.setMinimumHeight(80)  # Minimum for info panel
        if config_group:
            config_group.setMinimumHeight(120)  # You can adjust this if you want

        splitter.setSizes([120, 220])

        # --- Add splitter and rest of the widgets ---
        main_layout.addWidget(splitter)

        # --- Data actions (show/save) ---
        actions_layout = QHBoxLayout()
        self.show_plot_cb = QCheckBox("Show Data Plot"); self.show_plot_cb.setChecked(True)
        self.save_h5_cb = QCheckBox("Save as .h5")
        self.save_mat_cb = QCheckBox("Save as .mat")
        self.show_data_btn = QPushButton("Show Data")
        self.save_data_btn = QPushButton("Save Data")
        self.show_data_btn.clicked.connect(self.plot_data_dialog)
        self.save_data_btn.clicked.connect(self.save_data_dialog)
        actions_layout.addWidget(self.show_plot_cb)
        actions_layout.addWidget(self.save_h5_cb)
        actions_layout.addWidget(self.save_mat_cb)
        actions_layout.addWidget(self.show_data_btn)
        actions_layout.addWidget(self.save_data_btn)
        main_layout.addLayout(actions_layout)

        # --- Acquisition Buttons (hidden for passive boards) ---
        if not self.is_passive:
            ctrl_layout = QHBoxLayout()
            self.start_btn = QPushButton("Start Data Acquisition")
            self.start_btn.clicked.connect(self.start_acquisition)
            self.abort_btn = QPushButton("Abort")
            self.abort_btn.setEnabled(False)
            self.save_h5_cb.setChecked(True)
            ctrl_layout.addWidget(self.start_btn)
            ctrl_layout.addWidget(self.abort_btn)
            main_layout.addLayout(ctrl_layout)

        # --- Log Panel ---
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setFixedHeight(120)
        main_layout.addWidget(self.log)

        self.setLayout(main_layout)

    def set_all_voltage_ranges(self):
        val = self.set_all_voltage.currentText()
        for combo in self.voltage_ranges:
            combo.setCurrentText(val)

    def connect_and_fetch_info(self):
        try:
            self.board.connect()
            info = self.board.device_info()
            self.info_text.setText(info.replace('\n', '<br>'))
            self.log.append("[GUI] Connected and fetched device info.")
        except Exception as e:
            self.info_text.setText(f"[ERROR] {e}")
            self.log.append(f"[ERROR] {e}")

    def start_acquisition(self):
        self.log.append("[GUI] Starting acquisition...")
        # 1. Configure board
        t_sample = self.sample_time.value()
        f_sample = self.sample_freq.value()
        oversamp = {'x1': 0, 'x2': 1, 'x4': 2, 'x8': 3}[self.oversampling.currentText()]
        voltages = [float(combo.currentText()) for combo in self.voltage_ranges]
        trigger = self.level_trigger.isChecked()
        trig_level = self.trigger_level.value() if trigger else 0
        self.board.set_parameters(
            t_sample, f_sample, voltages, trigger, trig_level, oversamp, 0
        )
        # 2. Start worker thread
        self.thread = AcquisitionThread(self.board)
        self.thread.log.connect(self.log.append)
        self.thread.progress.connect(lambda v: self.log.append(f"[PROGRESS] {v}%"))
        self.thread.finished.connect(self.handle_acquisition_done)
        self.start_btn.setEnabled(False)
        self.abort_btn.setEnabled(False)
        self.thread.start()

    def handle_acquisition_done(self, board):
        self.start_btn.setEnabled(True)
        self.abort_btn.setEnabled(False)
        if board is None:
            self.log.append("[GUI] Acquisition failed.")
            return
        self.log.append("[GUI] Acquisition done.")
        self.data_loaded = True
        # Save as needed
        if self.save_h5_cb.isChecked():
            self.save_data_dialog(fmt='h5')
        if self.save_mat_cb.isChecked():
            self.save_data_dialog(fmt='mat')
        # Plot as needed
        if self.show_plot_cb.isChecked():
            self.plot_data_dialog()

    def plot_data_dialog(self):
        if self.board.OASISData is None or self.board.t is None:
            self.log.append("[GUI] No data to plot.")
            return
        dlg = DataPlotDialog(self.board, self)
        dlg.exec()

    def save_data_dialog(self, fmt=None):
        # If fmt is None, ask user; otherwise, save that format
        if self.board.OASISData is None or self.board.t is None:
            self.log.append("[GUI] No data to save.")
            return
        formats = []
        if fmt == 'h5' or (fmt is None and self.save_h5_cb.isChecked()):
            formats.append(('HDF5 File (*.h5)', 'h5'))
        if fmt == 'mat' or (fmt is None and self.save_mat_cb.isChecked()):
            formats.append(('MATLAB File (*.mat)', 'mat'))
        if not formats:
            formats = [('HDF5 File (*.h5)', 'h5'), ('MATLAB File (*.mat)', 'mat')]
        for text, ext in formats:
            fname, _ = QFileDialog.getSaveFileName(self, f"Save {ext.upper()} File", "", text)
            if fname:
                try:
                    if ext == 'h5':
                        self.board.save_data_h5(fname)
                        self.log.append(f"[GUI] Saved data as {fname}")
                    elif ext == 'mat':
                        self.board.save_data_mat(fname)
                        self.log.append(f"[GUI] Saved data as {fname}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", str(e))

    def show_imported_metadata(self, fname):
        import os
        ext = os.path.splitext(fname)[1].lower()
        meta_lines = []
        try:
            if ext == ".h5":
                import h5py
                with h5py.File(fname, "r") as f:
                    meta_lines.append(f"<b>File:</b> {os.path.basename(fname)}")
                    for key, val in f.attrs.items():
                        meta_lines.append(f"<b>{key}:</b> {val}")
            elif ext == ".mat":
                import scipy.io
                meta_lines.append(f"<b>File:</b> {os.path.basename(fname)}")
                meta_lines.append("MATLAB .mat files do not contain rich meta info. Only time and channels.")
            elif ext == ".oasismeta":
                # Use the parsed meta from OasisBoard._parse_oasismeta
                meta = self.board._parse_oasismeta(fname)
                meta_lines.append(f"<b>File:</b> {os.path.basename(fname)}")
                for k, v in meta.items():
                    meta_lines.append(f"<b>{k}:</b> {v}")
            else:
                meta_lines.append("Unknown file type.")
        except Exception as e:
            meta_lines.append(f"Error reading meta: {e}")

        # Fill info_text field (which is a QLabel)
        self.info_text.setText("<br>".join(meta_lines))

    def import_data_file(self, fname):
        try:
            ext = os.path.splitext(fname)[1].lower()
            if ext == ".h5":
                import h5py
                with h5py.File(fname, "r") as f:
                    dset = f['data']
                    ch = dset['channel']      # e.g. [1,1,...,2,2,...]
                    t = dset['time']          # e.g. [t0,t1,...,tN, t0,...]
                    v = dset['voltage']
                    n_ch = int(f.attrs.get('channels', 8))
                    unique_ch = np.unique(ch)
                    times = np.unique(t)
                    n_pts = len(times)
                    data = np.zeros((n_ch, n_pts))
                    # For each channel, find correct values by time
                    for idx, chan in enumerate(unique_ch):
                        mask = (ch == chan)
                        t_ch = t[mask]
                        v_ch = v[mask]
                        # Map each value into the right time slot
                        # If times are always the same order: data[idx] = v_ch
                        # But more robust: map by sorting time
                        sort_idx = np.argsort(t_ch)
                        data[idx, :] = v_ch[sort_idx]
                    self.board.OASISData = data
                    self.board.t = times
                    self.log.append(f"[GUI] Imported {fname}")
            elif ext == ".mat":
                import scipy.io
                mat = scipy.io.loadmat(fname)
                data = [mat.get(f'OASISChannel{i+1}', None) for i in range(8)]
                data = np.array([d.flatten() if d is not None else np.zeros(1) for d in data])
                t = mat.get('OASISTime', np.arange(data.shape[1]))
                self.board.OASISData = data
                self.board.t = t.flatten()
                self.log.append(f"[GUI] Imported {fname}")
            elif ext == ".oasismeta":
                self.board.load_from_files(fname)
                self.log.append(f"[GUI] Imported {fname}")
            else:
                QMessageBox.warning(self, "Unsupported", "Unsupported file format.")
            self.data_loaded = True
            self.show_imported_metadata(fname)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))


# -------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OASIS Control Panel")
        self.resize(1080, 700)

        menubar = QMenuBar(self)
        about_menu = menubar.addMenu("&About")
        about_action = QAction("About OASIS…", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)
        self.setMenuBar(menubar)

        # ---- Top area: Device selection and Import ----
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_widget.setLayout(top_layout)

        # Serial
        self.com_label = QLabel("Serial Port:")
        self.com_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.com_combo.setMinimumWidth(100)
        # TCP
        self.tcp_label = QLabel("or TCP IP:")
        self.ip_edit = QComboBox()
        self.ip_edit.setEditable(True)
        self.ip_edit.addItem("192.168.4.1")  # default
        self.tcp_port_label = QLabel("Port:")
        self.tcp_port_spin = QSpinBox()
        self.tcp_port_spin.setRange(1, 65535)
        self.tcp_port_spin.setValue(5025)
        # Mode selection
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Serial", "TCP"])
        # Connect/import
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_device)
        self.import_btn = QPushButton("Import Data File")
        self.import_btn.clicked.connect(self.import_data_file)

        top_layout.addWidget(self.mode_combo)
        top_layout.addWidget(self.com_label)
        top_layout.addWidget(self.com_combo)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.tcp_label)
        top_layout.addWidget(self.ip_edit)
        top_layout.addWidget(self.tcp_port_label)
        top_layout.addWidget(self.tcp_port_spin)
        top_layout.addStretch()
        top_layout.addWidget(self.connect_btn)
        top_layout.addWidget(self.import_btn)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.addWidget(top_widget)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(main)
        self.refresh_ports()

        self.mode_combo.currentIndexChanged.connect(self.update_mode_widgets)
        self.update_mode_widgets()

    def update_mode_widgets(self):
        is_serial = self.mode_combo.currentText() == "Serial"
        self.com_label.setVisible(is_serial)
        self.com_combo.setVisible(is_serial)
        self.refresh_btn.setVisible(is_serial)
        self.tcp_label.setVisible(not is_serial)
        self.ip_edit.setVisible(not is_serial)
        self.tcp_port_label.setVisible(not is_serial)
        self.tcp_port_spin.setVisible(not is_serial)

    def refresh_ports(self):
        import serial.tools.list_ports
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.com_combo.addItem(p.device)
        if not ports:
            self.com_combo.addItem("No ports found")

    def connect_device(self):
        mode = self.mode_combo.currentText().lower()
        if mode == "serial":
            port = self.com_combo.currentText()
            if not port or port == "No ports found":
                QMessageBox.warning(self, "No port", "Please select a valid COM port.")
                return
            tab = BoardTab(mode="serial", port=port, baudrate=115200)
        else:  # TCP
            ip = self.ip_edit.currentText().strip()
            tcp_port = self.tcp_port_spin.value()
            if not ip:
                QMessageBox.warning(self, "No IP", "Please enter a valid IP address.")
                return
            tab = BoardTab(mode="tcp", ip=ip, tcp_port=tcp_port)
        tab.connect_and_fetch_info()
        self.tabs.addTab(tab, f"OASIS ({mode.upper()})")
        self.tabs.setCurrentWidget(tab)

    def close_tab(self, idx):
        self.tabs.removeTab(idx)

    def import_data_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Import Data File", "", "OASIS Data (*.h5 *.mat *.OASISmeta)")
        if not fname:
            return
        board = OasisBoard(mode="offline")
        tab = BoardTab(mode="offline", board=board, is_passive=True)
        tab.import_data_file(fname)
        self.tabs.addTab(tab, f"Imported: {os.path.basename(fname)}")
        self.tabs.setCurrentWidget(tab)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About OASIS",
            "<b>OASIS Control Panel</b><br>"
            "Open Acquisition System for IEPE Sensors<br><br>"
            "https://gitlab.com/OASIS"
        )

def _resource_root() -> str:
    # Works both in dev and with PyInstaller
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def build_app_icon() -> QIcon:
    root = _resource_root()
    icon_dir = os.path.join(root, "ui", "resources", "icons")

    sizes = [16, 24, 32, 48, 64, 96, 128, 256]

    icon = QIcon()
    added_any = False
    for s in sizes:
        path = os.path.join(icon_dir, f"{s}x{s}.png")
        if os.path.exists(path):
            icon.addFile(path, QSize(s, s))
            added_any = True

    # Fallback: if no multi-size match, try a single known file
    if not added_any:
        fallback = os.path.join(icon_dir, "256x256.png")
        if os.path.exists(fallback):
            icon.addPixmap(QPixmap(fallback))
    return icon

# ------------- Main -------------
def main():
    app = QApplication(sys.argv)
    
    # --- Set app name ---
    app.setApplicationName("OASIS")
    app.setApplicationDisplayName("OASIS")

    # --- Set app icon ---
    app.setWindowIcon(build_app_icon())

    pg.setConfigOption('background', 'w')  # Global white bg for all PyQtGraph
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()