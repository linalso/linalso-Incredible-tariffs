from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import time
import psutil
from resource_analyzer import ResourceAnalyzer

class TariffSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('关税政策模拟器')
        self.setGeometry(100, 100, 800, 600)

        # 创建资源分析器
        self.resource_analyzer = ResourceAnalyzer()
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.main_tab = QWidget()
        self.log_tab = QWidget()
        self.tab_widget.addTab(self.main_tab, "主界面")
        self.tab_widget.addTab(self.log_tab, "加税日志")
        
        # 设置主界面布局
        main_layout = QVBoxLayout(self.main_tab)
        
        # 设置日志界面布局
        log_layout = QVBoxLayout(self.log_tab)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # 创建控制面板
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # 关税输入框
        self.tariff_label = QLabel('关税率(%)')
        self.tariff_input = QLineEdit('245')
        self.add_tariff_button = QPushButton('加税')
        self.add_tariff_button.clicked.connect(self.start_simulation)
        
        # 添加“我后悔”按钮
        self.regret_button = QPushButton('我后悔')
        self.regret_button.clicked.connect(self.stop_simulation)
        self.regret_button.setEnabled(False)  # 初始状态为禁用
        
        control_layout.addWidget(self.tariff_label)
        control_layout.addWidget(self.tariff_input)
        control_layout.addWidget(self.add_tariff_button)
        control_layout.addWidget(self.regret_button)
        
        # 创建图表
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle('系统资源使用率变化', color='k')
        self.plot_widget.setLabel('left', '使用率 (%)', color='k')
        self.plot_widget.setLabel('bottom', '时间 (s)', color='k')
        self.plot_widget.showGrid(x=True, y=True)
        
        # 创建两条曲线
        self.cpu_curve = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='CPU使用率')
        self.memory_curve = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2), name='内存使用率')
        
        # 添加图例
        self.plot_widget.addLegend()
        
        # 数据存储
        self.times = []
        self.cpu_values = []
        self.memory_values = []
        self.start_time = 0
        
        # 创建定时器用于更新图表
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        
        # 添加组件到主界面布局
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.plot_widget)
        
        # 添加资源使用报告标签
        self.report_label = QLabel()
        main_layout.addWidget(self.report_label)
        
        # 添加标签页到主布局
        layout.addWidget(self.tab_widget)
    
    def start_simulation(self):
        try:
            tariff_rate = float(self.tariff_input.text())
            if tariff_rate <= 0:
                raise ValueError('关税率必须大于0')
                
            # 重置数据
            self.times = []
            self.cpu_values = []
            self.memory_values = []
            self.start_time = time.time()
            
            # 启动资源消耗
            self.resource_analyzer.start_resource_consumption(tariff_rate)
            
            # 记录加税日志
            running_apps = [proc.name() for proc in psutil.process_iter(['name'])]
            log_text = f"为保护我方利益，已对以下应用加征{tariff_rate}%的关税：\n"
            for app in running_apps:
                log_text += f"- {app}\n"
            log_text += "\n" + "-"*50 + "\n"
            self.log_text.append(log_text)
            
            # 启动定时器，每100ms更新一次
            self.update_timer.start(100)
            
            # 禁用加税按钮，启用“我后悔”按钮
            self.add_tariff_button.setEnabled(False)
            self.regret_button.setEnabled(True)
            
        except ValueError as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, '输入错误', str(e))
    
    def stop_simulation(self):
        """停止关税模拟"""
        # 停止资源消耗
        self.resource_analyzer.stop()
        
        # 保持定时器运行以继续更新曲线
        
        # 启用加税按钮，禁用“我后悔”按钮
        self.add_tariff_button.setEnabled(True)
        self.regret_button.setEnabled(False)
        
        # 记录日志
        self.log_text.append("已停止关税模拟\n" + "-"*50 + "\n")
    
    def update_plot(self):
        # 获取当前资源使用率
        cpu_usage, memory_usage = self.resource_analyzer.get_current_usage()
        
        # 更新数据
        current_time = time.time() - self.start_time
        self.times.append(current_time)
        self.cpu_values.append(cpu_usage)
        self.memory_values.append(memory_usage)
        
        # 更新曲线
        self.cpu_curve.setData(self.times, self.cpu_values)
        self.memory_curve.setData(self.times, self.memory_values)
        
        # 更新资源报告
        report = self.resource_analyzer.get_resource_report()
        report_text = f"基准CPU使用率: {report['baseline_cpu']:.1f}%\n"
        report_text += f"当前CPU使用率: {report['current_cpu']:.1f}%\n"
        report_text += f"CPU增长倍数: {report['cpu_increase']:.2f}\n"
        report_text += f"基准内存使用率: {report['baseline_memory']:.1f}%\n"
        report_text += f"当前内存使用率: {report['current_memory']:.1f}%\n"
        report_text += f"内存增长倍数: {report['memory_increase']:.2f}"
        self.report_label.setText(report_text)