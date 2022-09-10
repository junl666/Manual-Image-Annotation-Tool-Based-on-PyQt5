from PyQt5.Qt import *


class DeleteConfirm(QWidget):
    """
    该类用于创建确认删除的窗口

    Attributes:
        delete_yes(QPushButton): 确认删除按钮
        delete_no(QPushButton): 取消按钮

    """
    def __init__(self):
        super().__init__()
        self.setGeometry(850, 750, 460, 220)
        self.setWindowTitle('是否删除')
        self.delete_yes = QPushButton('确认', self)
        self.delete_no = QPushButton('取消', self)
        self.delete_no.setGeometry(50, 80, 120, 80)
        self.delete_yes.setGeometry(250, 80, 120, 80)
        self.setWindowModality(Qt.ApplicationModal)
