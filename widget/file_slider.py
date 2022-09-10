from PyQt5.QtWidgets import QSlider
from PyQt5 import QtCore


class FileSlider(QSlider):
    """
    该类用于创建Graphicsview下方的选择图片滑动条

    """
    def __init__(self, widget):
        super(FileSlider, self).__init__(parent=widget)
        ##设置最小值
        self.setMinimum(0)
        # 设置最大值
        self.setMaximum(1000)
        # 步长
        self.setSingleStep(1)
        # 设置当前值
        self.setValue(0)
        # 刻度位置，刻度下方
        self.setTickPosition(self.TicksBelow)
        # 设置刻度间距
        self.setTickInterval(5)
        # 设置连接信号槽函数
        self.valueChanged.connect(self.filechange)

    signal_filechange = QtCore.pyqtSignal(str)

    def filechange(self):
        """
        当滑动条的值改变时，发送切换图片信号

        """
        self.nowratio = self.value()
        self.signal_filechange.emit('1')
