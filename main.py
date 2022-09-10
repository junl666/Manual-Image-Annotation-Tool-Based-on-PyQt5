from app import Window
from PyQt5.QtWidgets import QApplication
import sys


def main():
    """
    运行程序的函数

    """
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
