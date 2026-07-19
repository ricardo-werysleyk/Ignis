import sys
import os
import cv2
import numpy as np
import pandas as pd
from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from scipy.signal import butter, filtfilt

class IgnisV3(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IGNIS Analytics - Dashboard")
        self.setGeometry(50, 50, 1400, 850)
        
        self.FREQUENCY_HZ = 3440.0
        self.FREQUENCY_SLICE = 1.0
        
        self.time = np.array([0])
        self.raw_mass = np.array([0])
        self.filtered_mass = np.array([0])
        self.filtered_rate_mass = np.array([0])
        self.temp_tp_start = np.array([0])
        self.temp_tp_mid = np.array([0])
        self.temp_ir = np.array([0])
        
        self.video_path = None
        self.video_cap = None
        self.video_fps = 30.0
        
        self.current_idx = 0
        self.running = False
        self.step_velocity = 12 
        
        self.init_ui()
        
        if os.path.exists('data/dados_simulados.csv'):
            self.load_process_experiment('data/dados_simulados.csv')

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout_global = QtWidgets.QHBoxLayout(central_widget)
        
        # Container pai side_panel
        # Painel lateral de controle
        side_panel = QtWidgets.QVBoxLayout()
        layout_global.addLayout(side_panel, stretch=1)
        
        lbl_project = QtWidgets.QLabel("IGNIS")
        lbl_project.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        lbl_project.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        side_panel.addWidget(lbl_project)
        
        self.lbl_arquive_name = QtWidgets.QLabel("Arquivo: Nenhum carregado")
        self.lbl_arquive_name.setWordWrap(True)
        self.lbl_arquive_name.setStyleSheet("color: #aaa; font-style: italic;")
        side_panel.addWidget(self.lbl_arquive_name)
        
        # Botão de entrada de arquivo
        self.btn_arquive_load = QtWidgets.QPushButton("Selecionar Ensaio (.csv)")
        self.btn_arquive_load.setMinimumHeight(30)
        self.btn_arquive_load.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold;")
        self.btn_arquive_load.clicked.connect(self.open_arquive_selector)
        side_panel.addWidget(self.btn_arquive_load)
        
        self.add_separator(side_panel)
        
        # Seção de Controle
        side_panel.addWidget(QtWidgets.QLabel("<b>CONTROLE</b>"))
        self.btn_play = QtWidgets.QPushButton("Iniciar Playback")
        self.btn_play.setMinimumHeight(35)
        self.btn_play.clicked.connect(self.play_toggle)
        side_panel.addWidget(self.btn_play)
        
        self.btn_reset = QtWidgets.QPushButton("Resetar (Tempo Zero)")
        self.btn_reset.clicked.connect(self.experiment_reset)
        side_panel.addWidget(self.btn_reset)
        
        self.add_separator(side_panel)
        
        # Seção dos gráficos
        side_panel.addWidget(QtWidgets.QLabel("<b>Dashboard</b>"))
        
        self.lbl_mass = QtWidgets.QLabel("Massa: --- g")
        self.lbl_mass.setStyleSheet("font-size: 14px; color: #1f77b4; font-weight: bold;")
        side_panel.addWidget(self.lbl_mass)
        
        self.lbl_rate_mass = QtWidgets.QLabel("Taxa: --- g/s")
        self.lbl_rate_mass.setStyleSheet("font-size: 14px; color: #ff7f0e; font-weight: bold;")
        side_panel.addWidget(self.lbl_rate_mass)
        
        self.lbl_temp_tp_start = QtWidgets.QLabel("Temp. TP Início: --- °C")
        self.lbl_temp_tp_start.setStyleSheet("font-size: 14px; color: #2ca02c; font-weight: bold;")
        side_panel.addWidget(self.lbl_temp_tp_start)

        self.lbl_temp_tp_mid = QtWidgets.QLabel("Temp. TP Meio: --- °C")
        self.lbl_temp_tp_mid.setStyleSheet("font-size: 14px; color: #9467bd; font-weight: bold;")
        side_panel.addWidget(self.lbl_temp_tp_mid)
        
        self.lbl_temp_ir = QtWidgets.QLabel("Temp. IR (5Hz): --- °C")
        self.lbl_temp_ir.setStyleSheet("font-size: 14px; color: #d62728; font-weight: bold;")
        side_panel.addWidget(self.lbl_temp_ir)
        
        self.add_separator(side_panel)
        
        # Seção de dados importantes
        side_panel.addWidget(QtWidgets.QLabel("<b>DADOS CONSOLIDADOS</b>"))
        
        self.lbl_metric_mass_rate_max = QtWidgets.QLabel("Taxa Máx. Consumo: --- g/s")
        side_panel.addWidget(self.lbl_metric_mass_rate_max)
        
        self.lbl_metric_burn_time = QtWidgets.QLabel("Tempo Total Queima: --- s")
        side_panel.addWidget(self.lbl_metric_burn_time)
        
        self.lbl_metric_tp_start = QtWidgets.QLabel("Temp. Máx TP Início: --- °C")
        side_panel.addWidget(self.lbl_metric_tp_start)
        
        self.lbl_metrica_tc_meio = QtWidgets.QLabel("Temp. Máx TP Meio: --- °C")
        side_panel.addWidget(self.lbl_metrica_tc_meio)
        
        self.lbl_metric_ir = QtWidgets.QLabel("Temp. Máx Sensor IR: --- °C")
        side_panel.addWidget(self.lbl_metric_ir)
        
        side_panel.addStretch()
        
        # Container pai layout_right
        # Painel do dashboard 2x2, gráficos e video
        layout_right = QtWidgets.QVBoxLayout()
        layout_global.addLayout(layout_right, stretch=4)
        
        grid_visualization = QtWidgets.QGridLayout()
        layout_right.addLayout(grid_visualization)
        
        pg.setConfigOption('background', '#101010')
        pg.setConfigOption('foreground', 'w')
        
        # [0,0] Gráfico de massa
        self.graph_mass = pg.PlotWidget(title="Monitoramento de Massa")
        self.graph_mass.setLabel('left', 'Mass', units='g')
        self.graph_mass.showGrid(x=True, y=True, alpha=0.1)
        self.plt_brute = self.graph_mass.plot(pen=pg.mkPen('gray', width=1, style=QtCore.Qt.PenStyle.DotLine))
        self.plt_filtered = self.graph_mass.plot(pen=pg.mkPen('#1f77b4', width=2.5))
        grid_visualization.addWidget(self.graph_mass, 0, 0)
        
        # [0,1] Gráfico de taxa de variação mássica
        self.graph_mass_rate = pg.PlotWidget(title="Taxa de Variação Mássica (g/s)")
        self.graph_mass_rate.setLabel('left', 'Consumo', units='g/s')
        self.graph_mass_rate.showGrid(x=True, y=True, alpha=0.1)
        self.plt_rate = self.graph_mass_rate.plot(pen=pg.mkPen('#ff7f0e', width=2.5))
        grid_visualization.addWidget(self.graph_mass_rate, 0, 1)
        
        # [1,0] Gráfico de temperatura dos termopares e infravermelho
        self.graph_thermal = pg.PlotWidget(title="Perfis de Temperatura (Fusão de Sensores)")
        self.graph_thermal.setLabel('left', 'Temperatura', units='°C')
        self.graph_thermal.setLabel('bottom', 'Tempo', units='s')
        self.graph_thermal.showGrid(x=True, y=True, alpha=0.1)
        self.graph_thermal.addLegend()
        
        self.plt_tp_start = self.graph_thermal.plot(pen=pg.mkPen('#2ca02c', width=2), name="TC 1 - Base Amostra")
        self.plt_tp_mid = self.graph_thermal.plot(pen=pg.mkPen('#9467bd', width=2), name="TC 2 - Meio Amostra")
        self.plt_ir = self.graph_thermal.plot(pen=pg.mkPen('#d62728', width=2), name="Pirômetro IR (5Hz)")
        grid_visualization.addWidget(self.graph_thermal, 1, 0)
        
        # [1,1] Tela de exibição do vídeo
        self.lbl_video = QtWidgets.QLabel("Monitor de Vídeo da Queima\n(Nenhum arquivo .mp4 vinculado)")
        self.lbl_video.setStyleSheet("background-color: #000; border: 1px solid #333; color: #666;")
        self.lbl_video.setFont(QtGui.QFont("Arial", 11))
        self.lbl_video.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        grid_visualization.addWidget(self.lbl_video, 1, 1)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.att_with_slider)
        layout_right.addWidget(self.slider)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop_playback)

    def open_arquive_selector(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir Arquivo do Ensaio", "", "Arquivos de Dados (*.csv)")
        if path:
            self.load_process_experiment(path)

    def load_process_experiment(self, path_csv):
        self.timer.stop()
        self.running = False
        self.btn_play.setText("Iniciar Playback")
        
        # time,mass,termopar_start,termopar_mid,infrared
        df = pd.read_csv(path_csv)
        self.time = df["time"].values
        self.raw_mass = df["mass"].values
        self.temp_tp_start = df["termopar_start"].values
        self.temp_tp_mid = df["termopar_mid"].values
        
        self.lbl_arquive_name.setText(f"Arquivo: {os.path.basename(path_csv)}")
        
        # Filtro passa-baixas Butterworth (1Hz) para cálculo da derivada de consumo
        fs = self.FREQUENCY_HZ
        fc = self.FREQUENCY_SLICE  
        nyquist = fs / 2.0        
        b, a = butter(N=4, Wn=fc/nyquist, btype='low')
        self.filtered_mass = filtfilt(b, a, self.raw_mass)
        
        dt = 1.0 / fs
        self.filtered_rate_mass = -np.gradient(self.filtered_mass, dt)
        self.filtered_rate_mass = np.clip(self.filtered_rate_mass, 0, None)

        if "infrared" in df.columns:
            self.temp_ir = df["infrared"].values
            self.plt_ir.setVisible(True)
            self.lbl_temp_ir.setVisible(True)
            self.lbl_metric_ir.setText(f"Temp. Máx Sensor IR: {np.max(self.temp_ir):.1f} °C")
        else:
            self.temp_ir = np.zeros(len(self.time))
            self.plt_ir.setVisible(False)
            self.lbl_temp_ir.setVisible(False)
            self.lbl_metric_ir.setText("Temp. Máx Sensor IR: Não Instalado")

        # Sincronismo de vídeo do ensaio
        base_name, _ = os.path.splitext(path_csv)
        video_path_temporary = base_name + ".mp4"
        
        if os.path.exists(video_path_temporary):
            self.video_path = video_path_temporary
            self.video_cap = cv2.VideoCapture(self.video_path)
            self.video_fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        else:
            self.video_path = None
            if self.video_cap:
                self.video_cap.release()
            self.video_cap = None
            self.lbl_video.setText("Monitor de Vídeo\n(Nenhum arquivo .mp4 correspondente)")

        # Atualização dos dados estáticos
        max_burn_rate = np.max(self.filtered_rate_mass)
        self.lbl_metric_mass_rate_max.setText(f"Taxa Máx. Consumo: {max_burn_rate:.2f} g/s")
        
        burn_index = np.where(self.filtered_rate_mass > 0.5)[0]
        burn_time = self.time[burn_index[-1]] - self.time[burn_index[0]] if len(burn_index) > 1 else 0.0
        self.lbl_metric_burn_time.setText(f"Tempo Total Queima: {burn_time:.2f} s")
        
        self.lbl_metric_tp_start.setText(f"Temp. Máx TP Início: {np.max(self.temp_tp_start):.1f} °C")
        self.lbl_metrica_tc_meio.setText(f"Temp. Máx TP Meio: {np.max(self.temp_tp_mid):.1f} °C")

        # Ajuste de escalas dos eixos do gráfico
        self.graph_mass.setXRange(0, np.max(self.time))
        self.graph_mass.setYRange(-2, np.max(self.raw_mass) + 5)
        self.graph_mass_rate.setXRange(0, np.max(self.time))
        self.graph_mass_rate.setYRange(-2, max_burn_rate * 1.3)
        self.graph_thermal.setXRange(0, np.max(self.time))
        self.graph_thermal.setYRange(-10, 1200)
        
        self.slider.setRange(0, len(self.time) - 1)
        self.current_idx = 0
        self.dinamic_interface_att()

    # SINCRONISMO DOS GRÁFICOS E VIDEO
    def dinamic_interface_att(self):
        if len(self.time) <= 1:
            return
            
        t_slice = self.time[:self.current_idx]
        
        # Alimentação das curvas na GPU
        self.plt_brute.setData(t_slice, self.raw_mass[:self.current_idx])
        self.plt_filtered.setData(t_slice, self.filtered_mass[:self.current_idx])
        self.plt_rate.setData(t_slice, self.filtered_rate_mass[:self.current_idx])
        self.plt_tp_start.setData(t_slice, self.temp_tp_start[:self.current_idx])
        self.plt_tp_mid.setData(t_slice, self.temp_tp_mid[:self.current_idx])
        self.plt_ir.setData(t_slice, self.temp_ir[:self.current_idx])
        
        # Atualização numérica no painel lateral
        self.lbl_mass.setText(f"Massa: {self.filtered_mass[self.current_idx]:.2f} g")
        self.lbl_rate_mass.setText(f"Taxa: {self.filtered_rate_mass[self.current_idx]:.2f} g/s")
        self.lbl_temp_tp_start.setText(f"Temp. TC Base: {self.temp_tp_start[self.current_idx]:.1f} °C")
        self.lbl_temp_tp_mid.setText(f"Temp. TC Meio: {self.temp_tp_mid[self.current_idx]:.1f} °C")
        
        if self.lbl_temp_ir.isVisible():
            self.lbl_temp_ir.setText(f"Temp. IR: {self.temp_ir[self.current_idx]:.1f} °C")

        if self.video_cap and self.video_path:
            total_frames = self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            percentual_time = self.current_idx / len(self.time)
            frame_target = int(percentual_time * total_frames)
            
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_target)
            sucess, frame = self.video_cap.read()
            if sucess:
                frame = cv2.resize(frame, (600, 350))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = frame.shape
                line_pass = channels * width
                q_img = QtGui.QImage(frame.data, width, height, line_pass, QtGui.QImage.Format.Format_RGB888)
                self.lbl_video.setPixmap(QtGui.QPixmap.fromImage(q_img))
                
        self.slider.setValue(self.current_idx)

    def att_with_slider(self, position):
        self.current_idx = position
        self.dinamic_interface_att()

    def play_toggle(self):
        if len(self.time) <= 1:
            return
        if self.running:
            self.timer.stop()
            self.btn_play.setText("Iniciar Playback")
            self.running = False
        else:
            if self.current_idx >= len(self.time) - 30:
                self.current_idx = 0
            self.timer.start(16)
            self.btn_play.setText("Pausar Playback")
            self.running = True

    def loop_playback(self):
        if self.current_idx < len(self.time) - self.step_velocity:
            self.current_idx += self.step_velocity
            self.dinamic_interface_att()
        else:
            self.play_toggle()

    def experiment_reset(self):
        self.timer.stop()
        self.running = False
        self.btn_play.setText("Iniciar Playback")
        self.current_idx = 0
        self.dinamic_interface_att()

    def add_separator(self, layout):
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        layout.addWidget(sep)

    def closeEvent(self, event):
        if self.video_cap:
            self.video_cap.release()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    janela = IgnisV3()
    janela.show()
    sys.exit(app.exec())
