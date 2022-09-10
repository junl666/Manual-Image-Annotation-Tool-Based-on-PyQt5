from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.Qt import *
from PyQt5.QtWidgets import QCheckBox


class LabelDockWidget(QDockWidget):
    """
    可移动的窗口类，用于创建标签列表窗口

    Attributes:
        header_field(list): 用于设置行表头字段和设置列数
        all_checkbox(list): 用于储存当前所有复选框
        table(QTableWidget): 用于创建标签列表
        renamewin(QWidget): 'RenameWindow'类的实例化对象，为重命名窗口

    """
    changeValue = QtCore.pyqtSignal(str)
    Delete_label_in_table = QtCore.pyqtSignal(str)

    def __init__(self, *__args):
        super().__init__(*__args)
        # self.header_field = ['', 'label', 'group_id']
        self.header_field = ['label(group_id)']
        self.all_checkbox = []

        self.table = QTableWidget()
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.table.customContextMenuRequested.connect(self.generateMenu)
        self.initUI()
        self.renamewin = RenameWindow()
        self.renamewin.my_Signal.connect(self.Havechaged)

    def initUI(self):
        """
        初始化表格

        """
        self.setDockWidget()  # 设置表格
        self.show()

    # 设置表格
    def setDockWidget(self):
        """
        表格样式设置

        """
        # 表格控件
        # self.table.setFixedWidth(200)  # 表格宽度
        self.setInitTableHead()  # 设置表格行表头字段
        self.table.setAlternatingRowColors(True)  # 交替行颜色
        self.setWidget(self.table)

        # print(f"行数为:{self.table.rowCount()}")
        # print(f"列数为:{self.table.columnCount()}")

    # 设置行表头字段
    def setInitTableHead(self):
        """
        设置行表头字段

        """
        self.table.setColumnCount(len(self.header_field))  # 设置列数
        self.table.setHorizontalHeaderLabels(self.header_field)  # 设置行表头字段
        self.table.setRowHeight(0, 30)  # 行高
        self.table.setColumnWidth(0, 230)

    def addCheckBox(self):
        """
        向Table widget中添加复选框

        """
        self.table.insertRow(self.table.rowCount())
        check_box = QCheckBox()
        self.table.setCellWidget(self.table.rowCount() - 1, 0, check_box)

    def addRow(self, label, group_id, nodes, scene):
        """
        将新建的标签添加到table widget中，并将对应checkbox初始化为选中状态，同时后台存入复选框信息

        Args:
            label(str): 用户输入的标签名
            group_id(int): 用户输入的组号
            nodes(list): 储存当前标签的顶点图元
            scene(QgraphicsScene): 管理图元的scene

        """
        self.table.insertRow(self.table.rowCount())

        # 为刚添加的线加复选框
        check_box = Checkbox(nodes, scene)
        check_box.setChecked(True)
        check_box.setText(f"{label}({group_id})")

        self.all_checkbox.append(check_box)
        self.table.setCellWidget(self.table.rowCount() - 1, 0, check_box)

    def deleteAllRow(self):
        """
        从table widget中删除所有行

        """
        row_num = self.table.rowCount()
        for i in range(row_num):
            self.table.removeRow(0)
        self.all_checkbox.clear()
        # print(self.all_checkbox)

    def generateMenu(self, pos):
        """
        设置标签列表的右键菜单并对点击不同选项作出响应（删除、重命名）

        Args:
            pos(QPoint):鼠标右击时的位置

        """
        # rint( pos)
        row_num = -1
        for i in self.table.selectionModel().selection().indexes():
            self.Rename_num = i.row()
        menu = QMenu()
        item1 = menu.addAction(u"删除")
        item2 = menu.addAction(u"重命名")
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == item1:
            del self.all_checkbox[self.Rename_num]
            self.table.removeRow(self.Rename_num)
            self.Delete_label_in_table.emit('1')

        elif action == item2:
            self.renamewin.show()
            self.renamewin.inputbutton.clicked.connect(self.renamewin.close)
        else:
            return

    def Havechaged(self):
        """
        重命名成功录入标签名与组号后对标签列表显示内容和
        后台储存的信息进行修改

        """
        if self.renamewin.data_ready:
            self.name = self.renamewin.line_edit_label.text()
            self.group = self.renamewin.line_edit_groupid.text()
            none = None
            content = f"{self.name}({self.group})" if self.group != "" else f"{self.name}({none})"
            self.all_checkbox[self.Rename_num].setText(content)
            self.changeValue.emit('1')
            self.renamewin.data_ready = False
        else:
            self.renamewin.data_ready = False
            pass


class RenameWindow(QWidget):
    """
    该类用于创建重命名窗口

    Attributes:
        inputbutton(QPushButton): 输入确认按钮
        line_edit_label(QLineEdit): 输入标签文本框
        line_edit_groupid(QLineEdit): 输入组号文本框

    """
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.data_ready = False
        self.setWindowTitle("重命名标签:")
        self.move(1700, 500)
        self.resize(600, 150)
        self.inputbutton = QPushButton("输入", self)
        self.inputbutton.move(500, 110)
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
        self.line_edit_label.setClearButtonEnabled(True)
        self.line_edit_groupid.setClearButtonEnabled(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.inputbutton.clicked.connect(self.Data_Ready)

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


class Checkbox(QCheckBox):
    """
    该类用于创建展示标签信息的复选框

    Attributes:
        nodes_list(list): 储存对应标签的顶点图元
        scene(QgraphicsScene): 表示对应的QgraphicsScene对象

    """
    def __init__(self, nodes, scene, parent=None):
        super().__init__(parent)

        self.nodes_list = nodes
        self.scene = scene
        self.clicked.connect(self.showOrHideItem)

    def showOrHideItem(self):
        """
        隐藏或显示被点击的复选框

        """
        if self.isChecked():
            for node in self.nodes_list:
                self.scene.addItem(node)
                for edge in node.node_s_edges:
                    if edge in self.scene.items():
                        continue
                    else:
                        self.scene.addItem(edge)
        else:
            for node in self.nodes_list:
                self.scene.removeItem(node)
                for edge in node.node_s_edges:
                    if edge in self.scene.items():
                        self.scene.removeItem(edge)
                    else:
                        continue


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ta = LabelDockWidget('label')
    sys.exit(app.exec_())
