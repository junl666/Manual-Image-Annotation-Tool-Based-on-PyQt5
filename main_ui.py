from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene
from canvas.scene import GraphicScene
from canvas.view import GraphicView
from widget.label_dock_widget import LabelDockWidget
from widget.contrast_brightness_dialog import SliderWindow
from widget.file_dock_widget import FileDockWidget
from widget.file_slider import FileSlider


class UiMain(object):
    """
    该类用于创建应用主界面

    Attributes:
        centralwidget(QWidget): 中央窗口
        sliderwinow(QWidget): SliderWindow类的实例化对象，打开文件夹时选择图片的滑动条
        scene(QgraphicsScene): GraphicScene类的实例化对象，管理所有图元
        graphicsView(QgraphicsView): GraphicView的实例化对象，可视化图元
        gridLayout(QGridLayout): 栅格布局
        horizontalSlider(FileSlider): 中心窗口滑动条
        name(str): 滑动条名称
        statusbar(QStatusBar): 状态栏
        toolBar(QToolBar): 工具栏
        menubar(QMenuBar): 菜单栏
        menu_F(QMenu): 菜单栏“文件”按钮
        menu_E(QMenu): 菜单栏“编辑”按钮
        labelWidget(QDockWidget): 标签列表窗口，为可移动的停靠窗口
        fileWidget(FileDockWidget): 文件夹文件列表窗口， 为移动的停靠窗口
        actionSave(QAction): 保存动作按钮
        actionSaveAs(QAction): 另存为动作按钮
        actionZoom_Out(QAction): 放大动作按钮
        actionZoom_In(QAction): 缩小动作按钮
        actionCrop(QAction): 裁剪动作按钮
        actionUndo(QAction): 撤回动作按钮
        actionRestore(QAction): 恢复动作按钮
        actionRotate_counter(QAction): 逆时针旋转动作按钮
        actionRotate_clock(QAction):  顺时针旋转动作按钮
        action_Brightness(QAction): 调节亮度与对比度动作按钮
        action_label_point(QAction): 画点动作按钮
        action_label_poly(QAction): 画多边形动作按钮
        action_label_rect(QAction): 画矩形动作按钮
        action_label_line(QAction): 画线动作按钮
        actionDelete(QAction): 删除动作按钮
        actionOpenDir(QAction): 打开目录动作按钮
        action_edit_label(QAction): 编辑动作按钮
        actionVideo(QAction): 打开视频动作按钮

    """
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("labelall")
        MainWindow.resize(1550, 1200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.sliderwinow = SliderWindow()
        self.scene = GraphicScene()
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.graphicsView = GraphicView(self.scene, self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 2, 1)
        self.horizontalSlider = FileSlider(self.centralwidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.name = self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout.addWidget(self.horizontalSlider, 2, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 7)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 22))
        self.menubar.setObjectName("menubar")
        self.menu_F = QtWidgets.QMenu(self.menubar)
        self.menu_F.setObjectName("menu_F")
        self.menu_E = QtWidgets.QMenu(self.menubar)
        self.menu_E.setObjectName("menu_E")
        MainWindow.setMenuBar(self.menubar)
        self.labelWidget = LabelDockWidget('label', MainWindow)
        self.labelWidget.setObjectName("label")
        # self.dockWidgetContents = QtWidgets.QWidget()
        # self.dockWidgetContents.setObjectName("dockWidgetContents")
        # self.labelWidget.setWidget(self.dockWidgetContents)     # ？？？？？？你他妈是什么狗屎？？？？？？
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.labelWidget)
        self.fileWidget = FileDockWidget('file', MainWindow)
        self.fileWidget.setObjectName("file")
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.fileWidget)
        self.actionSave = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/.idea/cil-save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/save_as.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSaveAs.setIcon(icon1)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionZoom_Out = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/cil-zoom-out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoom_Out.setIcon(icon2)
        self.actionZoom_Out.setObjectName("actionZoom_Out")
        self.actionCrop = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/crop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCrop.setIcon(icon3)
        self.actionCrop.setObjectName("actionCrop")
        self.actionOpenFile = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("icons/opened_folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenFile.setIcon(icon4)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.actionExit = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("icons/backspace.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon5)
        self.actionExit.setObjectName("actionExit")
        self.actionRotate_counter = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("icons/counter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRotate_counter.setIcon(icon6)
        self.actionRotate_counter.setObjectName("actionRotate_counter")
        self.actionUndo = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("icons/arrow-back-up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUndo.setIcon(icon7)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRestore = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("icons/arrow-forward-up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRestore.setIcon(icon8)
        self.actionRestore.setObjectName("actionRestore")
        self.addWinAction = QtWidgets.QAction(MainWindow)
        self.addWinAction.setObjectName("addWinAction")
        self.actionZoom_In = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("icons/cil-zoom-in.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoom_In.setIcon(icon9)
        self.actionZoom_In.setObjectName("actionZoom_In")
        self.actionRotate_clock = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("icons/clock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRotate_clock.setIcon(icon10)
        self.actionRotate_clock.setObjectName("actionRotate_clock")
        self.action_Brightness = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("icons/brightness.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Brightness.setIcon(icon11)
        self.action_Brightness.setObjectName("action_Brightness")
        self.action_label_point = QtWidgets.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("icons/dot.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_label_point.setIcon(icon12)
        self.action_label_point.setObjectName("actionLabel_Point")
        self.action_label_poly = QtWidgets.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("icons/polygon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_label_poly.setIcon(icon13)
        self.action_label_poly.setObjectName("actionLabel_poly")
        self.action_label_rect = QtWidgets.QAction(MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap("icons/cil-rectangle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_label_rect.setIcon(icon14)
        self.action_label_rect.setObjectName("actionLabel_Rect")
        self.action_label_line = QtWidgets.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap("icons/line.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_label_line.setIcon(icon15)
        self.action_label_line.setObjectName("actionLabel_Line")
        self.actionDelete = QtWidgets.QAction(MainWindow)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap("icons/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete.setIcon(icon16)
        self.actionDelete.setObjectName("actionDelete")
        self.actionOpenDir = QtWidgets.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap("icons/opened_folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenDir.setIcon(icon17)
        self.actionOpenDir.setObjectName("actionOpenDir")
        self.actionVideo = QtWidgets.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap("icons/video.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_edit_label = QtWidgets.QAction(MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap("icons/edit.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_edit_label.setIcon(icon19)
        self.action_edit_label.setObjectName('action_EditLabel')

        self.actionVideo.setIcon(icon18)
        self.actionVideo.setObjectName("actionVideo2Img")
        self.toolBar.addAction(self.actionOpenFile)
        self.toolBar.addAction(self.actionOpenDir)
        self.toolBar.addAction(self.actionVideo)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSaveAs)
        self.toolBar.addAction(self.actionExit)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_label_point)
        self.toolBar.addAction(self.action_label_line)
        self.toolBar.addAction(self.action_label_rect)
        self.toolBar.addAction(self.action_label_poly)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionUndo)
        self.toolBar.addAction(self.actionRestore)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionZoom_Out)
        self.toolBar.addAction(self.actionZoom_In)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRotate_counter)
        self.toolBar.addAction(self.actionRotate_clock)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCrop)
        self.toolBar.addAction(self.action_Brightness)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_edit_label)
        self.menu_F.addAction(self.actionOpenFile)
        self.menu_F.addAction(self.actionOpenDir)
        self.menu_F.addAction(self.actionSave)
        self.menu_F.addAction(self.actionSaveAs)
        self.menu_F.addAction(self.actionExit)
        self.menu_E.addAction(self.actionZoom_In)
        self.menu_E.addAction(self.actionZoom_Out)
        self.menu_E.addAction(self.actionCrop)
        self.menu_E.addAction(self.actionRotate_clock)
        self.menu_E.addAction(self.actionRotate_counter)
        self.menu_E.addSeparator()
        self.menu_E.addAction(self.actionUndo)
        self.menu_E.addAction(self.actionRestore)
        self.menu_E.addAction(self.actionDelete)
        self.menubar.addAction(self.menu_F.menuAction())
        self.menubar.addAction(self.menu_E.menuAction())

        self.retranslateUi(MainWindow)
        self.menubar.triggered['QAction*'].connect(MainWindow.show)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "labelall"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.menu_F.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_E.setTitle(_translate("MainWindow", "编辑(&E)"))
        self.actionSave.setText(_translate("MainWindow", "保存"))
        self.actionSaveAs.setText(_translate("MainWindow", "另存为"))
        self.actionZoom_Out.setText(_translate("MainWindow", "缩小"))
        self.actionCrop.setText(_translate("MainWindow", "裁剪"))
        self.actionOpenFile.setText(_translate("MainWindow", "打开"))
        self.actionExit.setText(_translate("MainWindow", "退出"))
        self.actionRotate_counter.setText(_translate("MainWindow", "逆时针旋转"))
        self.actionUndo.setText(_translate("MainWindow", "撤回"))
        self.actionRestore.setText(_translate("MainWindow", "恢复"))
        self.action_edit_label.setText(_translate("MainWindow", "编辑标签"))
        self.addWinAction.setText(_translate("MainWindow", "添加窗体"))
        self.addWinAction.setToolTip(_translate("MainWindow", "添加窗体"))
        self.actionZoom_In.setText(_translate("MainWindow", "放大"))
        self.actionRotate_clock.setText(_translate("MainWindow", "顺时针旋转"))
        self.action_Brightness.setText(_translate("MainWindow", "亮度"))
        self.action_label_point.setText(_translate("MainWindow", "点"))
        self.action_label_poly.setText(_translate("MainWindow", "多边形"))
        self.action_label_rect.setText(_translate("MainWindow", "矩形"))
        self.action_label_line.setText(_translate("MainWindow", "线段"))
        self.actionDelete.setText(_translate("MainWindow", "删除"))
        self.actionOpenDir.setText(_translate("MainWindow", "打开目录"))
        self.actionVideo.setText(_translate("MainWindow", "视频"))
        self.actionVideo.setToolTip(_translate("MainWindow", "视频"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMain()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
