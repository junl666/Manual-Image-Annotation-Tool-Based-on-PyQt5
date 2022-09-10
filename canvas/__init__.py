from .items import GraphicItem
from PyQt5.QtWidgets import QApplication
import sys

temp = QApplication(sys.argv)  # QPixmap: Must construct a QGuiApplication before a QPixmap
item_init = GraphicItem()
item_width = item_init.width
item_height = item_init.height

