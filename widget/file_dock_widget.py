from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.Qt import *
import os


class FileDockWidget(QDockWidget):
    """
    可移动的窗口类，用于创建文件夹图片列表窗口

    Attributes:
        header_field(list): 用于设置行表头字段和设置列数
        table(QTableWidget): 用于创建文件列表
        filepath_list(list): 用于储存文件夹内所有文件路径
        click_num(int): 表示被点击的图片序号
        savewindow(QWidget): SaveWindow 类的实例化对象，切换图片时的确认保存窗口

    """

    def __init__(self, *__args):
        super().__init__(*__args)
        self.header_field = ['filepath']
        self.table = QTableWidget()
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.table.itemClicked.connect(self.doubleclick)

        self.table.customContextMenuRequested.connect(self.generateMenu)
        self.initUI()
        self.filepath_list = []
        self.savewindow = SaveWindow()
        self.click_num = None

    def initUI(self):
        """
        初始化表格

        """
        self.setTableWidget()  # 设置表格
        self.show()

    # 设置表格
    def setTableWidget(self):
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

    def addRow(self, filepath):
        """
        向 table widget中添加行

        Args:
            filepath: 需要添加行对应的文件路径

        """
        self.table.insertRow(self.table.rowCount())
        self.filepath_list.append(filepath)
        filename = os.path.basename(filepath)
        newItem = QTableWidgetItem(filename)
        self.table.setItem(self.table.rowCount() - 1, 0, newItem)

    def deleteAllRow(self):
        """
        从table widget中删除所有行

        """
        row_num = len(self.filepath_list)
        while row_num >= 0:
            self.table.removeRow(row_num)
            row_num -= 1
        self.filepath_list = []

    def generateMenu(self, pos):
        """
        设置标签列表的右键菜单，点击删除时执行删除操作

        Args:
            pos(QPoint):鼠标右击时的位置

        """
        # rint( pos)
        row_num = -1
        for i in self.table.selectionModel().selection().indexes():
            self.del_num = i.row()
        menu = QMenu()
        item = menu.addAction(u"删除")
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == item:
            self.table.removeRow(self.del_num)
            del self.filepath_list[self.del_num]

    #         self.signal_del_file.emit('1')
    #
    signal_file = QtCore.pyqtSignal(str)
    signal_save = QtCore.pyqtSignal(str)

    def doubleclick(self):
        """
        双击切换图片(不保存）

        """
        row_num = -1
        self.num_last_time = self.click_num
        for i in self.table.selectionModel().selection().indexes():
            self.click_num = i.row()
        print(self.click_num)
        # if self.first_pic:
        self.changeimg_withoutsave()
        # self.first_pic=False
        # else:
        #     self.savewindow = SaveWindow()
        #     self.savewindow.show()
        #     self.savewindow.yescheck.clicked.connect(self.changeimg_withsave)
        #     self.savewindow.nocheck.clicked.connect(self.changeimg_withoutsave)
        #     self.savewindow.backcheck.clicked.connect(self.close_back)
        #     self.savewindow.backcheck.clicked.connect(self.savewindow.close)

    def changeimg_withoutsave(self):
        """
        切换图片且不保存

        """
        self.change_file = self.filepath_list[self.click_num]
        self.signal_file.emit('1')
        self.savewindow.close()

    def changeimg_withsave(self):
        """
        切换图片且保存

        """
        # self.old_file=self.change_file
        self.change_file = self.filepath_list[self.click_num]
        self.signal_save.emit('1')
        self.savewindow.close()

    def close_back(self):
        """
        直接关闭保存选项窗口则不切换图片

        """
        self.table.selectRow(self.num_last_time)

    def sliderchange(self, num):
        """
        根据滑动条值变化切换图片

        Args:
            num: 滑动条对应值(int)

        """
        self.change_file = self.filepath_list[num]
        self.signal_file.emit('1')
        self.table.selectRow(num)


class SaveWindow(QWidget):
    """
    该类用于创建切换图片时的保存选项窗口

    """
    def __init__(self):
        super().__init__()
        self.setGeometry(850, 750, 660, 220)
        self.setWindowTitle('是否保存')
        self.yescheck = QPushButton('是', self)
        self.nocheck = QPushButton('否', self)
        self.backcheck = QPushButton('取消', self)
        self.yescheck.setGeometry(50, 80, 120, 80)
        self.nocheck.setGeometry(250, 80, 120, 80)
        self.backcheck.setGeometry(450, 80, 120, 80)
        self.setWindowModality(Qt.ApplicationModal)
