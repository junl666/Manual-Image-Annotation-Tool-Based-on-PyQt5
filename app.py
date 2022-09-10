from PIL.Image import fromqimage
from PyQt5.Qt import *
from PyQt5 import QtGui, QtCore
import PIL.ImageEnhance
import utils
from main_ui import UiMain
from widget.file_dialog import FileDialogPreview
import os.path as osp
import json
import label_file
from label_file import LabelFile
from canvas.items import Edge, GraphicItem, RectEdge
from canvas import item_width, item_height
import base64
import os


class Window(QMainWindow, UiMain):
    """窗口类，对main_ui进行补充，也是连接不同控件的“桥梁”

    Attributes:
        action_label_list(list):存放四种标注图形的列表
        file_num_old(int):记入滑动slider时的上一时刻UI上显示的图片在文件夹中的对应数字
        filename(str):当前图片的绝对路径
        have_json(bool):当前图片是否有同名json的判断
        image(QImage):当前载入的图片的QImage格式
        imageData(bytes):前载入的图片的编码格式
        imagePath(str):当前图片的绝对路径或者同名json的绝对路径
        item(QGraphicsPixmapItem):当前图片转化成的QGraphicsPixmapItem对象
        labelFile(LabelFile): 储存json文件的信息的容器
        pic_type(bool):
        pix(QPixmap): 当前图片转化成的QPixmap对象
        view_scale(float):控制当前GraphicView的缩放比例

    """

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.filename = None
        self.labelFile = None
        self.view_scale = None
        self.file_num_old = None
        self.imageData = None
        self.imagePath = None
        self.image = None
        self.action_label_list = [self.action_label_point,
                                  self.action_label_line,
                                  self.action_label_rect,
                                  self.action_label_poly]
        self.setInitEnable()
        self.slot()

    def openFile(self):
        """打开一张图片

        """
        path = osp.dirname(str(self.filename)) if self.filename else "."
        formats = ["*.{}".format(fmt.data().decode()) for fmt in
                   QtGui.QImageReader.supportedImageFormats()]  # 使得所有的图片格式都支持？
        filters = self.tr("Image & Label files (%s)") % " ".join(formats + ["*%s" % ".json"])
        fileDialog = FileDialogPreview(self)
        fileDialog.setFileMode(FileDialogPreview.ExistingFile)
        fileDialog.setNameFilter(filters)
        fileDialog.setWindowTitle(self.tr("%s - Choose Image or Label file") % "labelall", )
        fileDialog.setWindowFilePath(path)
        fileDialog.setViewMode(FileDialogPreview.Detail)
        if fileDialog.exec_():
            fileName = fileDialog.selectedFiles()[0]
            print(fileName)
            # fileName_eg: E:/pythonProject3/qt5manager-master/result.jpg
            #              E:/pythonProject3/qt5manager-master/result.json
            if fileName:
                self.loadFile(fileName)
        self.file_suffix()

    def openDir(self):
        """打开一个图片文件夹

        """
        cur_dir = QDir.currentPath()  # 获取当前文件夹路径
        # 选择文件夹
        dir_path = QFileDialog.getExistingDirectory(self, '打开文件夹', cur_dir)
        # 读取文件夹文件
        file_paths = []
        if dir_path != '':
            self.fileWidget.deleteAllRow()
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                format = '*' + os.path.splitext(file)[-1]
                if format in ["*.{}".format(fmt.data().decode()) for fmt in
                              QtGui.QImageReader.supportedImageFormats()]:
                    file_paths.append(os.path.join(root, file))
        print('file_paths')
        print(file_paths)
        if len(file_paths) <= 0:
            return
        # 获取第一个文件
        for cur_path in file_paths:
            self.fileWidget.addRow(cur_path)

    def changeFile(self):
        """
        文件栏改变选择后，重新加载图片

        """
        self.loadFile(self.fileWidget.change_file)

    def sliderChangeFile(self):
        """
        通过下方滑动条移动的位置（对应的数值），进行对相应图片的加载

        """
        try:
            filenum = int(self.fileWidget.table.rowCount() * self.horizontalSlider.nowratio / 1000)
            if filenum == self.file_num_old:
                return
            self.fileWidget.sliderchange(filenum)
            self.file_num_old = filenum
        except:
            pass

    def file_suffix(self):
        """


        """
        portion = os.path.splitext(str(self.filename))
        if portion[1] == '.json':
            self.pic_type = False
        else:
            self.pic_type = True

    def loadFile(self, filename):
        """
        载入一张图片，同时自适应大小，并初始化相关按钮与参数

        Args:
            filename(str):图片的绝对路径

        """
        self.clearAll()

        if self.view_scale is not None:
            # 按照之前的缩放倍数先进行还原，然后才能进行自适应窗口
            self.graphicsView.scale(1 / self.view_scale, 1 / self.view_scale)

        json_file = osp.splitext(filename)[0] + ".json"
        if QtCore.QFile.exists(json_file):  # 即存在这个json文件
            self.have_json = True
            self.labelFile = LabelFile(json_file)  # self.labelFile.shapes即为存信息的list
            self.imageData = self.labelFile.imageData
            self.imagePath = osp.join(osp.dirname(json_file),
                                      self.labelFile.imagePath, )
        else:
            self.have_json = False
            self.imageData = LabelFile.load_image_file(filename)
            if self.imageData:
                self.imagePath = filename

        image = QtGui.QImage.fromData(self.imageData)
        self.image = image
        self.filename = filename

        self.pix = QPixmap.fromImage(image)
        self.item = QGraphicsPixmapItem(self.pix)
        # self.item.setPos(0, 0)
        self.scene.addItem(self.item)
        self.scene.setSceneRect(0, 0, self.pix.width(), self.pix.height())

        if self.labelFile:
            self.addLabelInfo(self.labelFile)

        # 自适应大小
        self.view_scale = self.viewScale()
        self.graphicsView.scale(self.view_scale, self.view_scale)

        # 打开图片后将放缩功能设置为可用
        self.actionZoom_In.setEnabled(True)
        self.actionZoom_Out.setEnabled(True)
        self.action_Brightness.setEnabled(True)

        # 初始化亮度和对比度滑动条
        self.sliderwinow.slider_brightness.setValue(10)
        self.sliderwinow.slider_contrast.setValue(10)

        for action_label in self.action_label_list:
            action_label.setEnabled(True)
            action_label.setCheckable(True)
        self.action_edit_label.setEnabled(True)
        self.action_edit_label.setCheckable(True)

        self.labelFile = None

    def slot(self):
        """
        所有的槽函数

        """
        self.actionOpenFile.triggered.connect(self.openFile)
        self.actionOpenDir.triggered.connect(self.openDir)
        self.actionZoom_Out.triggered.connect(self.graphicsView.zoomOut)
        self.actionZoom_In.triggered.connect(self.graphicsView.zoomIn)
        self.action_Brightness.triggered.connect(lambda: self.sliderwinow.show())
        self.action_label_poly.triggered.connect(self.actionPolyTriggered)
        self.action_label_point.triggered.connect(self.actionPointTriggered)
        self.action_label_line.triggered.connect(self.actionLineTriggered)
        self.action_label_rect.triggered.connect(self.actionRectTriggered)

        self.actionRotate_clock.triggered.connect(self.clock_rotate)
        self.actionRotate_counter.triggered.connect(self.counter_rotate)

        self.actionSaveAs.triggered.connect(self.saveJsonAs)
        self.actionSave.triggered.connect(self.saveJson)

        # 获得label时弹窗所对应的槽函数
        self.graphicsView.label_dialog.line_edit_groupid.returnPressed.connect(self.getAndShowLabel)
        self.graphicsView.label_dialog.inputbutton.clicked.connect(self.getAndShowLabel)

        self.graphicsView.delete_label_signal.connect(self.deleteLabel)

        self.graphicsView.can_edit_signal.connect(self.canEdit)
        self.graphicsView.cannot_edit_signal.connect(self.cannotEdit)
        self.action_edit_label.triggered.connect(self.actionEditTriggered)

        self.labelWidget.changeValue.connect(self.renameLabelInDict)
        self.labelWidget.Delete_label_in_table.connect(self.deleteLabelInTableWidget)

        self.graphicsView.set_cross_cursor_signal.connect(self.setCrossCursor)
        self.graphicsView.set_hand_cursor_signal.connect(self.setHandCursor)
        self.graphicsView.set_arrow_cursor_signal.connect(self.setArrowCursor)

        self.graphicsView.delete_confirm.delete_yes.clicked.connect(self.graphicsView.confirmDelete)
        self.graphicsView.delete_confirm.delete_no.clicked.connect(self.graphicsView.delete_confirm.close)
        self.graphicsView.label_dialog.my_Signal.connect(self.graphicsView.activeExit)

        self.sliderwinow.bright_contrast_signal.connect(self.changeBrightnessAndContrast)  # 改变亮度和对比度的信号

        self.fileWidget.signal_file.connect(self.changeFile)
        self.horizontalSlider.signal_filechange.connect(self.sliderChangeFile)  # 打开文件有关的三个信号

    def setInitEnable(self):
        """
        将一些按钮初始化为禁用状态

        """
        self.actionZoom_In.setEnabled(False)
        self.actionZoom_Out.setEnabled(False)
        self.action_Brightness.setEnabled(False)
        # self.actionSave.setEnabled(False)
        # self.actionSaveAs.setEnabled(False)
        for action_label in self.action_label_list:
            action_label.setEnabled(False)
        self.action_edit_label.setEnabled(False)

    def changeBrightnessAndContrast(self):
        """
        完成对图片亮度与对比度的调节

        """
        img = self.image
        img = fromqimage(img)
        value = self.sliderwinow.slider_brightness.value() / 10
        img = PIL.ImageEnhance.Brightness(img).enhance(value)
        value2 = self.sliderwinow.slider_contrast.value() / 10
        img = PIL.ImageEnhance.Contrast(img).enhance(value2)
        img_data = utils.img_pil_to_data(img)
        image = QtGui.QImage.fromData(img_data)
        self.scene.removeItem(self.item)
        self.pix = QPixmap.fromImage(image)
        self.item = QGraphicsPixmapItem(self.pix)
        self.scene.addItem(self.item)
        self.scene.setSceneRect(0, 0, self.pix.width(), self.pix.height())

    def addLabelInfo(self, label_info):
        """获取label_info里的信息，并把这些信息写入到scene中的nodes_info

        Args:
            label_info(): 现在打开的json文件中的label信息

        """
        for shape in label_info.shapes:
            shape_type = shape['shape_type']
            if shape_type == 'polygon':
                nodes_list = self.addPolyInfo(shape)
            elif shape_type == 'rectangle':
                nodes_list = self.addRectInfo(shape)
            elif shape_type == 'line':
                nodes_list = self.addLineInfo(shape)
            elif shape_type == 'point':
                nodes_list = self.addPointInfo(shape)
            else:
                raise TypeError("We don't have this shape type.")

            self.labelWidget.addRow(shape['label'], shape['group_id'], nodes_list, self.scene)
            node_info_dic = {'label': shape['label'], 'points': nodes_list,
                             'shape_type': shape_type, 'flags': shape['flags'],
                             'group_id': shape['group_id'], 'other_data': shape['other_data']}
            self.scene.nodes_info['shapes'].append(node_info_dic)

    def canEdit(self):
        """
        激活edit功能

        """
        self.action_edit_label.setChecked(False)
        self.action_edit_label.setEnabled(True)

    def cannotEdit(self):
        """
        关闭edit功能

        """
        self.action_edit_label.setEnabled(False)

    def viewScale(self):
        """
        实现图片自适应窗口功能

        Returns:
            float: 缩放的一个比值

        """
        if (self.pix.width() / self.pix.height()) < (
                self.graphicsView.size().width() / self.graphicsView.size().height()):
            return self.graphicsView.size().height() / self.pix.height()
        else:
            return self.graphicsView.size().width() / self.pix.width()

    def clearAll(self):
        """
        若要打开新的图片，则清除现存的所有信息

        """
        for item in self.scene.items().copy():
            self.scene.removeItem(item)
        self.scene.nodes_info = {'shapes': []}
        self.labelWidget.deleteAllRow()

    def deleteLabel(self):
        """
        确认删除后把相关联的checkbox删除

        """
        if self.graphicsView.graphicsTouched_delete:
            for checkbox in self.labelWidget.all_checkbox:
                if checkbox.nodes_list == self.graphicsView.shapeTouched_delete['points']:
                    self.labelWidget.table.removeRow(self.labelWidget.all_checkbox.index(checkbox))
                    self.labelWidget.all_checkbox.remove(checkbox)
                    break
                else:
                    continue
        else:
            # 能从这个else进来的，在当前的逻辑下，只有点到 point 或者 line的point 才有可能
            for checkbox in self.labelWidget.all_checkbox:
                if self.graphicsView.point_now in checkbox.nodes_list:
                    self.labelWidget.table.removeRow(self.labelWidget.all_checkbox.index(checkbox))
                    self.labelWidget.all_checkbox.remove(checkbox)
                    break
                else:
                    continue

    def getAndShowLabel(self):
        """
        连接 "获取label弹窗" 与 "添加checkbox至右边栏"

        """
        label, group_id, nodes, scene = self.graphicsView.sendData()
        self.labelWidget.addRow(label, group_id, nodes, scene)

    def clock_rotate(self):
        """
        顺时针旋转90°

        """
        self.graphicsView.rotate(90)

    def counter_rotate(self):
        """
        逆时针旋转90°

        """
        self.graphicsView.rotate(-90)

    def closeEvent(self, event):
        """
        关闭主程序的警告

        Args:
            event(QEvent): "点击关闭"这一事件

        """
        reply = QMessageBox.question(self, '确认', '确认退出吗', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def saveJsonAs(self):
        """
        json的另存为

        """
        empty = {
            "version": "5.0.1",
            "flags": {},
            "shapes": [],
            "imagePath": "",
            "imageData": "",
            "imageHeight": 0,
            "imageWidth": 0
        }
        shapelist = self.scene.nodes_info['shapes']
        pointlist = []
        coordinate = []
        empty["imageWidth"] = self.pix.width()
        empty["imageHeight"] = self.pix.height()
        i = 0
        while i < len(shapelist):
            pointlist.append([])
            pointlist[i] = shapelist[i]['points']
            i += 1
        e = 0
        while e < len(pointlist):
            coordinate.append([])
            e += 1
        h = 0
        while h < len(pointlist):
            for ite in pointlist[h]:
                if isinstance(ite, list):
                    coordinate[h].append(ite)
                else:
                    # print(pointlist)
                    cor = []
                    view_pos = ite.pos()
                    x = view_pos.x() + item_width / 2
                    y = view_pos.y() + item_height / 2
                    cor = [x, y]
                    coordinate[h].append(cor)
            h += 1
        transition = self.scene.nodes_info['shapes']
        one_list = {
            "label": "",
            "points": [],
            "group_id": "",
            "shape_type": "",
            "flags": {}
        }
        p = 0
        while p < len(transition):
            xxxxxx = one_list.copy()
            empty["shapes"].append(xxxxxx)
            p += 1
        p = 0
        while p < len(transition):
            empty["shapes"][p]['label'] = transition[p]['label']
            p += 1
        j = 0
        while j < len(empty["shapes"]):
            empty["shapes"][j]["points"] = coordinate.copy()[j]
            j += 1
        p = 0
        while p < len(transition):
            empty["shapes"][p]['group_id'] = transition[p]['group_id']
            p += 1
        p = 0
        while p < len(transition):
            empty["shapes"][p]['shape_type'] = transition[p]['shape_type']
            p += 1
        while p < len(transition):
            empty["shapes"][p]['flags'] = transition[p]['flags']
            p += 1
        pic_str = self.encode_base64(self.filename)
        if self.pic_type:
            empty["imagePath"] = self.filename
            empty["imageData"] = str(pic_str)
            base_name = os.path.splitext(self.filename)[0]
            new_name = base_name + ".json"
        else:
            new_name = self.filename
            empty["imagePath"] = self.imagePath
            empty["imageData"] = label_file.imageData_again
        jso = empty
        filepath, type = QFileDialog.getSaveFileName(self, '文件保存', new_name, 'json(*.json)')
        if filepath == '':
            pass
        else:
            # print(filepath)
            with open(filepath, 'w') as file_obj:
                json.dump(jso, file_obj, indent=2, sort_keys=False)

    def saveJson(self):
        """
        保存json文件

        """
        if self.pic_type and (not self.have_json):
            self.saveJsonAs()
            self.have_json = True
        else:
            empty = {
                "version": "5.0.1",
                "flags": {},
                "shapes": [],
                "imagePath": "",
                "imageData": "",
                "imageHeight": 0,
                "imageWidth": 0
            }
            shapelist = self.scene.nodes_info['shapes']
            pointlist = []
            coordinate = []
            empty["imageWidth"] = self.pix.width()
            empty["imageHeight"] = self.pix.height()
            i = 0
            while i < len(shapelist):
                pointlist.append([])
                pointlist[i] = shapelist[i]['points']
                i += 1
            e = 0
            while e < len(pointlist):
                coordinate.append([])
                e += 1
            h = 0
            while h < len(pointlist):
                for ite in pointlist[h]:
                    if isinstance(ite, list):
                        coordinate[h].append(ite)
                    else:
                        view_pos = ite.pos()
                        x = view_pos.x() + item_width / 2
                        y = view_pos.y() + item_height / 2
                        cor = [x, y]
                        coordinate[h].append(cor)
                h += 1
            transition = self.scene.nodes_info['shapes']
            one_list = {
                "label": "",
                "points": [],
                "group_id": "",
                "shape_type": "",
                "flags": {}
            }
            p = 0
            while p < len(transition):
                xxxxxx = one_list.copy()
                empty["shapes"].append(xxxxxx)
                p += 1
            p = 0
            while p < len(transition):
                empty["shapes"][p]['label'] = transition[p]['label']
                p += 1
            j = 0
            while j < len(transition):
                empty["shapes"][j]["points"] = coordinate.copy()[j]
                j += 1
            p = 0
            while p < len(transition):
                empty["shapes"][p]['group_id'] = transition[p]['group_id']
                p += 1
            p = 0
            while p < len(transition):
                empty["shapes"][p]['shape_type'] = transition[p]['shape_type']
                p += 1
            while p < len(transition):
                empty["shapes"][p]['flags'] = transition[p]['flags']
                p += 1
            pic_str = self.encode_base64(self.filename)
            if self.pic_type:
                empty["imagePath"] = self.filename
                empty["imageData"] = str(pic_str)
                base_name = os.path.splitext(self.filename)[0]
                new_name = base_name + ".json"
            else:
                new_name = self.filename
                empty["imagePath"] = self.imagePath
                empty["imageData"] = label_file.imageData_again
            jso = empty
            with open(new_name, 'w') as file_obj:
                json.dump(jso, file_obj, indent=2, sort_keys=False)

    def encode_base64(self, file):
        """把图片信息进行编码

        Args:
            file(str): 图片的绝对路径

        """
        with open(file, 'rb') as f:
            img_data = f.read()
            base64_data = base64.b64encode(img_data)
            base64_str = str(base64_data, 'utf-8')
            return base64_str

    def renameLabelInDict(self):
        """
        重命名后对相应字典中的信息进行修改

        """
        self.scene.nodes_info['shapes'][self.labelWidget.Rename_num]['label'] = self.labelWidget.name
        self.scene.nodes_info['shapes'][self.labelWidget.Rename_num]['group_id'] = self.labelWidget.group

    def deleteLabelInTableWidget(self):
        """
        根据右键菜单发出的”删除“信号，对UI上的对应图形进行删除

        """
        for point in self.scene.nodes_info['shapes'][self.labelWidget.Rename_num]['points']:
            self.scene.removeItem(point)
            for edge in point.node_s_edges:
                if edge in self.scene.items():
                    self.scene.removeItem(edge)
                else:
                    continue
        del self.scene.nodes_info['shapes'][self.labelWidget.Rename_num]

    def setHandCursor(self):
        """
        把光标设置为“手形”

        """
        self.graphicsView.setCursor(Qt.PointingHandCursor)

    def setCrossCursor(self):
        """把光标设置为“十字形”

        """
        self.graphicsView.setCursor(Qt.CrossCursor)

    def setArrowCursor(self):
        """
        把光标设置为“箭头形”

        """
        self.graphicsView.setCursor(Qt.ArrowCursor)

    def actionPointTriggered(self):
        """
        完成点标注相关功能/按钮等的设置与激活/关闭

        """
        if self.action_label_point.isChecked():
            self.graphicsView.point_triggered = True
            self.graphicsView.edit_enable = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_point:
                    continue
                else:
                    action_label.setEnabled(False)
            self.action_edit_label.setEnabled(False)
        else:
            self.graphicsView.point_triggered = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_point:
                    continue
                else:
                    action_label.setEnabled(True)
            self.action_edit_label.setEnabled(True)
            self.setArrowCursor()
        self.action_edit_label.setChecked(False)

    def actionLineTriggered(self):
        """
        完成线段标注相关功能/按钮等的设置与激活/关闭

        """
        if self.action_label_line.isChecked():
            self.graphicsView.line_triggered = True
            self.graphicsView.edit_enable = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_line:
                    continue
                else:
                    action_label.setEnabled(False)
            self.action_edit_label.setEnabled(False)
        else:
            self.graphicsView.line_triggered = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_line:
                    continue
                else:
                    action_label.setEnabled(True)
            self.action_edit_label.setEnabled(True)
            self.setArrowCursor()
        self.action_edit_label.setChecked(False)

    def actionRectTriggered(self):
        """
        完成矩形标注相关功能/按钮等的设置与激活/关闭

        """
        if self.action_label_rect.isChecked():
            self.graphicsView.rect_triggered = True
            self.graphicsView.edit_enable = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_rect:
                    continue
                else:
                    action_label.setEnabled(False)
            self.action_edit_label.setEnabled(False)
        else:
            self.graphicsView.rect_triggered = False
            self.setArrowCursor()
            for action_label in self.action_label_list:
                if action_label == self.action_label_rect:
                    continue
                else:
                    action_label.setEnabled(True)
            self.action_edit_label.setEnabled(True)
        self.action_edit_label.setChecked(False)

    def actionPolyTriggered(self):
        """
        完成多边形标注相关功能/按钮等的设置与激活/关闭

        """
        if self.action_label_poly.isChecked():
            self.graphicsView.poly_triggered = True
            self.graphicsView.edit_enable = False
            for action_label in self.action_label_list:
                if action_label == self.action_label_poly:
                    continue
                else:
                    action_label.setEnabled(False)
            self.action_edit_label.setEnabled(False)
        else:
            self.graphicsView.poly_triggered = False
            self.setArrowCursor()
            for action_label in self.action_label_list:
                if action_label == self.action_label_poly:
                    continue
                else:
                    action_label.setEnabled(True)
            self.action_edit_label.setEnabled(True)
        self.action_edit_label.setChecked(False)

    def actionEditTriggered(self):
        """
        完成与edit相关功能/按钮等的设置与激活/关闭

        """
        if self.action_edit_label.isChecked():
            self.graphicsView.edit_enable = True
            self.graphicsView.poly_triggered = False
            self.graphicsView.rect_triggered = False
            self.graphicsView.point_triggered = False
            self.graphicsView.line_triggered = False
            self.action_edit_label.setChecked(True)
            self.setArrowCursor()
            for action_label in self.action_label_list:
                action_label.setEnabled(True)
                action_label.setChecked(False)
        else:
            self.graphicsView.edit_enable = False
            self.action_edit_label.setChecked(False)

    def addPolyInfo(self, shape):
        """得到shape里的信息，完成多边形从json中到app中的显示

        Args:
            shape(dict): 存储某一个图形所有信息的字典

        Returns:
            list: 储存多边形所有点对象的list
        """
        nodes_list = []
        for node_pos in shape['points']:
            node = self.addNodeToScene(shape['shape_type'], node_pos)
            nodes_list.append(node)
        for index in range(len(nodes_list)):
            node_start = nodes_list[index]
            node_end = nodes_list[index + 1] if (index + 1 < len(nodes_list)) else nodes_list[0]
            edge = Edge(node_start, node_end)
            self.scene.addItem(edge)
            node_start.node_s_edges.append(edge)
            node_end.node_s_edges.append(edge)
        return nodes_list

    def addRectInfo(self, shape):
        """得到shape里的信息，完成多边形从json中到app中的显示

        Args:
            shape(dict): 存储某一个图形所有信息的字典

        Returns:
            list: 储存矩形所有点对象的list
        """
        nodes_list = []
        for node_pos in shape['points']:
            node = self.addNodeToScene(shape['shape_type'], node_pos)
            nodes_list.append(node)
        edges = [RectEdge(nodes_list[0], nodes_list[1], i) for i in range(1, 5)]
        for edge in edges:
            self.scene.addEdge(edge)
        nodes_list[0].node_s_edges.extend(edges)
        nodes_list[1].node_s_edges.extend(edges)

        return nodes_list

    def addLineInfo(self, shape):
        """得到shape里的信息，完成多边形从json中到app中的显示

        Args:
            shape(dict): 存储某一个图形所有信息的字典

        Returns:
            list: 储存线段两端点对象的list
        """
        nodes_list = []
        for node_pos in shape['points']:
            node = self.addNodeToScene(shape['shape_type'], node_pos)
            nodes_list.append(node)
        edge = Edge(nodes_list[0], nodes_list[1])
        self.scene.addEdge(edge)
        nodes_list[0].node_s_edges.append(edge)
        nodes_list[1].node_s_edges.append(edge)
        return nodes_list

    def addPointInfo(self, shape):
        """得到shape里的信息，完成多边形从json中到app中的显示

        Args:
            shape(dict): 存储某一个图形所有信息的字典

        Returns:
            list: 储存多该点对象的list
        """
        nodes_list = []
        node = self.addNodeToScene(shape['shape_type'], shape['points'][0])
        nodes_list.append(node)
        return nodes_list

    def addNodeToScene(self, shape_type, node_pos):
        """
        在该位置创建一个点对象并返回该点对象

        Args:
            shape_type(str): 形状（如 polygon  line ...）
            node_pos(list): 该点坐标的list[x, y]

        Returns:
            GraphicItem：在此函数中创建的点对象

        """
        node = GraphicItem()
        node.shape_type = shape_type
        node.setZValue(2)
        node.setPos(node_pos[0] - node.width / 2, node_pos[1] - node.height / 2)
        self.scene.addItem(node)
        node.scene = self.scene
        return node
