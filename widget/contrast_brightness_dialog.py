from PyQt5 import QtCore
from PyQt5.Qt import *


class SliderWindow(QWidget):
    """
    该类用于创建调节亮度和对比度的窗口

    Attributes:
        label_brightness(QLabel): 标明“亮度”的标签
        label_contrast(QLabel): 标明“对比度”的标签
        slider_brightness(QSlider): 调节亮度水平滑动条
        slider_contrast(QSlider): 调节对比度水平滑动条

    """
    def __init__(self, parent=None):
        super(SliderWindow, self).__init__(parent)
        self.setWindowTitle("亮度与对比度调整")
        self.resize(600, 50)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.label_brightness = QLabel("亮度")
        self.label_brightness.setAlignment(Qt.AlignLeft)
        self.label_contrast = QLabel('对比度')
        self.label_contrast.setAlignment(Qt.AlignLeft)
        # 创建水平滑动条
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_contrast = QSlider(Qt.Horizontal)
        # 设置布局
        hbox = QFormLayout()
        hbox.addRow(self.label_brightness, self.slider_brightness)
        hbox2 = QHBoxLayout()
        hbox.addRow(self.label_contrast, self.slider_contrast)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        # hbox.addLayout(gridlayout2)
        self.setLayout(vbox)
        # 设置最小值
        self.slider_brightness.setMinimum(0)
        self.slider_contrast.setMinimum(0)
        # 设置最大值
        self.slider_brightness.setMaximum(20)
        self.slider_contrast.setMaximum(20)
        # 设置步长
        self.slider_brightness.setSingleStep(1)
        self.slider_contrast.setSingleStep(1)
        # 设置当前值
        self.slider_brightness.setValue(10)
        self.slider_contrast.setValue(10)
        # 刻度位置在下方
        self.slider_brightness.setTickPosition(QSlider.TicksBelow)
        self.slider_contrast.setTickPosition(QSlider.TicksBelow)
        # 设置刻度间隔
        self.slider_brightness.setTickInterval(1)
        self.slider_contrast.setTickInterval(1)

        # 连接信号槽
        self.slider_brightness.sliderReleased.connect(self.brightnessChanged)
        self.slider_contrast.sliderReleased.connect(self.contrastChanged)

    def brightnessChanged(self):
        """
        亮度滑动条被拖动释放后传递新的亮度值

        """
        print("current slider value=%s" % self.slider_brightness.value())
        self.sendEditBrightness()

    def contrastChanged(self):
        """
        对比度滑动条被拖动释放后传递新的对比度值

        """
        print("current slider value2=%s" % self.slider_contrast.value())
        self.sendEditContrast()

    bright_contrast_signal = QtCore.pyqtSignal()

    def sendEditBrightness(self):
        """
        发射调整亮度的信号

        """
        self.bright_contrast_signal.emit()

    def sendEditContrast(self):
        """
        发射调整对比度的信号

        """
        self.bright_contrast_signal.emit()
