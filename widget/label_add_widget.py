from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *


class LabelDialog(QWidget):
    """
    该类用于创建标签命名窗口

    Attributes:
        inputbutton(QPushButton): 输入确认按钮
        line_edit_label(QLineEdit): 标签名文本框栏
        line_edit_groupid(QLineEdit): 组号文本框栏
        name(str): 储存标签名
        group(str): 储存组号
        comboBox(QComboBox):储存使用过的标签名
        comboBox2(QComboBox):储存使用过的组号
        data_ready(bool): 表示标签信息录入成功

    """
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("请输入标签信息:")
        self.resize(600, 250)
        self.inputbutton = QPushButton("输入", self)
        self.inputbutton.move(500, 200)
        flo = QFormLayout()
        self.line_edit_label = QLineEdit("default", self)
        self.line_edit_label.selectAll()  # 选择全部内容
        self.line_edit_label.setFocus()
        self.line_edit_groupid = QLineEdit()
        self.line_edit_groupid.setValidator(QtGui.QIntValidator())
        flo.addRow("LabelName", self.line_edit_label)
        flo.addRow("GroupID", self.line_edit_groupid)
        self.line_edit_groupid.setPlaceholderText("GroupID 不输入默认是0")
        self.line_edit_label.setEchoMode(QLineEdit.Normal)
        self.line_edit_groupid.setEchoMode(QLineEdit.Normal)
        self.line_edit_groupid.displayText()
        self.setLayout(flo)
        self.name = self.line_edit_label.text()
        self.group = self.line_edit_groupid.text()
        self.line_edit_label.setClearButtonEnabled(True)
        self.line_edit_groupid.setClearButtonEnabled(True)
        self.line_edit_label.returnPressed.connect(self.cursor_move)
        self.setWindowModality(Qt.ApplicationModal)

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(137, 130, 200, 35))
        self.comboBox.setObjectName("l")
        # print(label_table_widget.Usedlabels.copy())
        self.comboBox.addItems(['<使用过的标签>'])
        self.comboBox.setCurrentIndex(0)  # 设置默认显示的值，不设置则默认为0
        self.comboBox.activated.connect(self.auto1)  # 关联信号与槽

        self.comboBox2 = QtWidgets.QComboBox(self)
        self.comboBox2.setGeometry(QtCore.QRect(400, 130, 100, 35))
        self.comboBox2.setObjectName("ll")
        self.comboBox2.addItems(["<组名>"])
        self.comboBox2.setCurrentIndex(0)  # 设置默认显示的值，不设置则默认为0
        self.comboBox2.activated.connect(self.auto2)  # 关联信号与槽
        self.inputbutton.clicked.connect(self.Data_Ready)
        self.line_edit_groupid.returnPressed.connect(self.Data_Ready)

    def cursor_move(self):  # 光标移动事件
        """
        输入完标签名按下回车自动切换光标位置

        """
        self.line_edit_groupid.setFocus()


    def auto1(self):
        """
        选择已有标签名给当前标签命名

        """
        if (self.comboBox.currentText()) != '<使用过的标签>':
            self.line_edit_label.setText(self.comboBox.currentText())
        else:
            return

    def auto2(self):
        """
        选择已有组号给当前标签分组

        """
        if (self.comboBox2.currentText()) != '<组名>':
            self.line_edit_groupid.setText(self.comboBox2.currentText())
        else:
            return

    def closeEvent(self, event: QCloseEvent):
        """
        窗口关闭回到标记上一步

        Args:
            event: 窗口关闭事件

        """
        self.sendEditContent()

    def sendEditContent(self):
        """
        发送撤回信号

        """
        content = '1'
        self.my_Signal.emit(content)

    def Data_Ready(self):
        """
        标签名、组号成功输入

        """
        self.data_ready = True
