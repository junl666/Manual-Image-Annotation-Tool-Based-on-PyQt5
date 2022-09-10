from PyQt5 import Qt
from canvas.items import GraphicItem, Edge, GraphicPolygonItem, RectEdge
from PyQt5.Qt import *
import numpy as np
import matplotlib.path as mplPath
from PyQt5.QtCore import pyqtSignal
from widget.delete_confirm_widget import DeleteConfirm
from widget.label_add_widget import LabelDialog
from canvas import item_width, item_height


class GraphicView(QGraphicsView):
    """
    该类用于显示QgraphicsScene中的内容
    包含了大多数涉及到对QgraphicsScene中所绘制图形进行整体拖动、删除等编辑操作的函数

    Attributes:
        scene(QGraphicsScene): QgraphicsScene的实例化对象，将scene传入此处托管，方便在view中维护
        init_size = self.size()
        edge_enable(bool): 用于记录目前是否可以画线条
        drag_edge(QGraphicsPathItem): 记录拖拽时的线
        poly_triggered(bool): 用于记录绘制多边形功能是否开启
        rect_triggered(bool): 用于记录绘制矩形功能是否开启
        point_triggered(bool): 用于记录绘制点功能是否开启
        line_triggered(bool): 用于记录绘制线段功能是否开启
        checkCtrl(bool):用于记录Ctr键是否被按下
        label_dialog：LabelDialog的实例化对象，绘制完一个标签弹出的命名窗口。
        graphicsTouched_delete(bool): 用于记录鼠标是否在多边形内部
        shapeTouched_delete(dict): 用于记录被鼠标触发的图形对象
        graphicsTouched_move(bool): 用于记录图形是否可以被拖动
        shapeTouched_move(dict): 用于记录被拖动的图形对象
        edit_enable(bool): 用于记录编辑模式是否开启
        position_orig(QPoint): 鼠标在多边形内部时，用于记录鼠标左击的位置
        position_press_move(QPoint): 鼠标在多边形内部时，用于跟踪鼠标左击并移动时的位置
        q_pos_list_old(list): 用于储存上一个被鼠标触发的多边形的顶点对应Qpoint对象
        poly_now(GraphicPolygonItem): 表示此时被触发的多边形对象
        point_now(QGraphicsItem): 表示此时鼠标点击的QGraphicsItem对象(若无则为None)
        rect_points_list(list): 用于储存当前绘制的矩形已确定的斜对角顶点图元（一个或两个）
        rect_draw_points(list): 用于储存绘制矩形的两个斜对角顶点图元(在 rect_points_list被清空前，储存两个顶点信息）
        rect_pair_points(list): 用于储存所有矩形的两个斜对角顶点图元
        delete_confirm(QWidget): DeleteConfirm实例化对象，确认是否删除的弹窗

    """
    delete_label_signal = pyqtSignal()
    can_edit_signal = pyqtSignal()
    cannot_edit_signal = pyqtSignal()
    set_cross_cursor_signal = pyqtSignal()
    set_hand_cursor_signal = pyqtSignal()
    set_arrow_cursor_signal = pyqtSignal()

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene  # 将scene传入此处托管，方便在view中维护
        self.parent = parent
        self.init_ui()
        self.init_size = self.size()

        self.edge_enable = False  # 用来记录目前是否可以画线条
        self.drag_edge = None  # 记录拖拽时的线
        self.poly_triggered = False
        self.rect_triggered = False
        self.point_triggered = False
        self.line_triggered = False
        self.checkCtrl = False

        self.label_dialog = LabelDialog()
        self.setMouseTracking(True)
        self.graphicsTouched_delete = False
        self.shapeTouched_delete = None
        self.graphicsTouched_move = False
        self.shapeTouched_move = None
        self.edit_enable = False
        self.position_orig = None
        self.position_press_move = None

        self.q_pos_list_old = None
        self.poly_now = None
        self.point_now = None

        self.rect_points_list = []
        self.rect_pair_points = []
        self.rect_draw_points = []

        self.delete_confirm = DeleteConfirm()

    def init_ui(self):
        """
        初始化Graphicsview部件

        """
        self.setScene(self.scene)
        # 设置渲染属性
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高品质抗锯齿
                            QPainter.TextAntialiasing |  # 文字抗锯齿
                            QPainter.SmoothPixmapTransform )  # 使图元变换更加平滑
                            #QPainter.LosslessImageRendering)  # 不失真的图片渲染
        # 视窗更新模式
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def keyPressEvent(self, event):
        """
        键盘按下后的响应
        1)按下Ctrl键: self.checkCtrl = True

        2)按下M键: 打印相应内容

        3)按下Backspace键:撤回一步标记操作

        4)按下Delete键: 删除对应图形操作

        Args:
            event(QEvent): 键盘按下事件

        """
        if event.key() == Qt.Key_Control:
            self.checkCtrl = True
        if event.key() == Qt.Key_M:
            print("=" * 25)
            print(f"scene中item总数：{len(self.scene.items())}")
            # print(f"scene中node总数：{len(self.scene.nodes)}")
            # print(f"scene中edge总数：{len(self.scene.edges)}")
            # print(f"已经存储的总图形个数{len(self.scene.nodes_info['shapes'])}")
            # print(f"node的线：{item.node_s_edges}" for item in self.scene.items() if isinstance(item, GraphicItem))
        if event.key() == Qt.Key_Backspace:
            if self.poly_triggered:
                if len(self.scene.nodes) > 1:
                    self.scene.removeNode(self.scene.nodes[-1])
                    self.edgeDragStart(self.scene.nodes[-1])
                elif len(self.scene.nodes) == 1:
                    self.scene.removeNode(self.scene.nodes[-1])
                    self.can_edit_signal.emit()
                    self.edge_enable = False
                else:
                    return
            elif self.rect_triggered:
                if len(self.rect_points_list) == 1:
                    self.scene.removeNode(self.rect_points_list[0])
                    self.rect_points_list = []
            elif self.line_triggered:
                if len(self.scene.nodes) == 1:
                    self.scene.removeNode(self.scene.nodes[-1])
                    self.can_edit_signal.emit()
                    self.edge_enable = False
                else:
                    return

            else:
                return
        if event.key() == Qt.Key_Delete:
            # 两种情况触发self.delete_confirm.show()：
            # 1. 多边形/矩形 内部且当前图形没有隐藏
            # 2. 鼠标在点上，且该点shape_type 是 point 或者 line
            if self.graphicsTouched_delete and self.pointsOnScene(self.shapeTouched_delete['points']):
                self.delete_confirm.show()
            elif isinstance(self.point_now, GraphicItem):
                if self.point_now.shape_type == 'point' or self.point_now.shape_type == 'line':
                    self.delete_confirm.show()
                else:
                    return
            else:
                return
        else:
            return

    def keyReleaseEvent(self, event):
        """键盘释放事件响应

        释放Ctrl键: self.checkCtrl = False

        Args:
            event(QEvent): 键盘按键被释放

        """
        if event.key() == Qt.Key_Control:
            self.checkCtrl = False

    def mousePressEvent(self, event):
        """鼠标按钮按下事件响应

        1)在标记功能被触发时，可在图片内创建多边形、矩形、点或线段

        2)在编辑功能被触发时，点击图形内部开启拖动整个图形的功能

        Args:
            event(QEvent): 鼠标按下事件

        """
        self.label_dialog.data_ready = False
        if self.poly_triggered and event.button() == Qt.LeftButton:
            if not self.insideScene(event.pos()):  # 如果点击的位置不在在图片范围内则直接返回
                return
            self.edge_enable = True
            self.cannot_edit_signal.emit()
            item = self.getItemAtClick(event)
            if isinstance(item, GraphicItem):
                if len(self.scene.nodes) >= 3 and item == self.scene.nodes[0]:  # 点到第一个，且是合法的多边形
                    self.edgeDragEnd(item)
                    self.label_dialog.show()
                    self.nodeGetEdge()
                    self.edge_enable = False
                else:
                    return
            else:
                node = self.createNode("polygon", event.pos())  # 创建点，加点，并获得点
                if node == self.scene.nodes[0]:
                    self.edgeDragStart(node)
                else:
                    self.edgeDragEnd(node)
                    self.edgeDragStart(node)
        elif self.rect_triggered and event.button() == Qt.LeftButton:
            # 判断点击的位置是否在图片范围内
            if self.insideScene(event.pos()):
                rect_item = self.createNode("rectangle", event.pos())
                self.rect_points_list.append(rect_item)
                if len(self.rect_points_list) == 1:
                    self.drawRect(self.rect_points_list)
                elif len(self.rect_points_list) == 2:
                    self.rect_draw_points = self.rect_points_list.copy()
                    self.rect_points_list = []
                    self.drawRect(self.rect_draw_points)
                    self.rect_pair_points.append([self.rect_draw_points[0], self.rect_draw_points[1]])
                    self.label_dialog.show()
                    self.nodeGetEdge()
                    self.edge_enable = False
        elif self.point_triggered and event.button() == Qt.LeftButton:
            self.set_cross_cursor_signal.emit()
            item = self.getItemAtClick(event)
            if isinstance(item, GraphicItem):
                return
            else:
                self.cannot_edit_signal.emit()
                self.set_arrow_cursor_signal.emit()
                self.createNode("point", event.pos())
                self.label_dialog.show()
        elif self.line_triggered and event.button() == Qt.LeftButton:
            self.set_cross_cursor_signal.emit()
            item = self.getItemAtClick(event)
            self.edge_enable = True
            if isinstance(item, GraphicItem):
                return
            else:
                node = self.createNode("line", event.pos())
                if node == self.scene.nodes[0]:
                    self.edge_enable = True
                    self.edgeDragStart(node)
                else:
                    self.edgeDragEnd(node)
                    self.label_dialog.show()
                    self.nodeGetEdge()
                    self.edge_enable = False
        elif self.edit_enable:
            self.position_press_move = self.mapToScene(event.pos()).toPoint()
            self.position_orig = self.mapToScene(event.pos()).toPoint()
            if self.insideScene(event.pos()) and (self.scene.nodes_info['shapes']):
                if self.judgePosition(self.position_press_move) is None:
                    self.graphicsTouched_move = False
                    return
                else:
                    self.graphicsTouched_move, self.shapeTouched_move = self.judgePosition(self.position_press_move)
            else:
                return
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """对鼠标移动事件的响应

        1)标记功能下，随着鼠标移动实时更新临时的线条

        2)编辑模式下，鼠标左击在图形内部拖拽实现图形整体移动；鼠标无论是否点击，鼠标在图形内部则填充图形

        Args:
            event(QEvent): 鼠标移动事件

        """
        self.point_now = self.getItemAtClick(event)
        if self.poly_triggered:
            self.set_cross_cursor_signal.emit()
            self.emptyPoly()
            if self.drag_edge is not None:
                sc_pos = self.mapToScene(event.pos())
                self.drag_edge.set_dst(sc_pos.x(), sc_pos.y())
                self.drag_edge.update()

                # 结束时的“磁铁”
                if ((self.insideScene(event.pos())) and
                        (len(self.scene.nodes) >= 3) and
                        (self.getItemAtClick(event) == self.scene.nodes[0])):
                    self.cursor().setPos(self.toQpoint(self.mapToGlobal(self.mapFromScene(
                        self.itemGetCentralPos(self.getItemAtClick(event))))))
                else:
                    return
            else:
                return
        elif self.rect_triggered:
            self.set_cross_cursor_signal.emit()
            if len(self.rect_points_list) == 1:
                sc_pos = self.mapToScene(event.pos())
                self.drag_rect_new_edge_one.set_src(sc_pos.x() - item_width / 2, self.rect_points_list[0].y())
                self.drag_rect_new_edge_two.set_src(self.rect_points_list[0].x(), sc_pos.y() - item_height / 2)
                self.drag_rect_new_edge_three.set_dst(sc_pos.x() - item_width / 2, sc_pos.y() - item_height / 2)
                self.drag_rect_new_edge_three.set_src(self.rect_points_list[0].x(), sc_pos.y() - item_height / 2)
                self.drag_rect_new_edge_four.set_dst(sc_pos.x() - item_width / 2, sc_pos.y() - item_height / 2)
                self.drag_rect_new_edge_four.set_src(sc_pos.x() - item_width / 2, self.rect_points_list[0].y())
                self.drag_rect_new_edge_one.update()
                self.drag_rect_new_edge_two.update()
                self.drag_rect_new_edge_three.update()
                self.drag_rect_new_edge_four.update()
        elif self.line_triggered:
            self.set_cross_cursor_signal.emit()
            self.emptyPoly()
            if self.drag_edge is not None:
                sc_pos = self.mapToScene(event.pos())
                self.drag_edge.set_dst(sc_pos.x(), sc_pos.y())
                self.drag_edge.update()
            else:
                return
        elif self.point_triggered:
            self.set_cross_cursor_signal.emit()
        elif self.edit_enable:
            # 如果点击拖动则整体位移
            if event.buttons() == Qt.LeftButton and self.insideScene(event.pos()):
                distance_x = self.mapToScene(event.pos()).x() - self.position_orig.x()
                distance_y = self.mapToScene(event.pos()).y() - self.position_orig.y()
                if self.graphicsTouched_move and self.pointsOnScene(self.shapeTouched_move['points']):
                    self.set_hand_cursor_signal.emit()
                    for point in self.shapeTouched_move['points']:
                        if not self.insideScene(
                                self.mapFromScene((point.pos().x()) + distance_x + point.width / 2,
                                                  point.pos().y() + distance_y + point.height / 2)):
                            return
                    for point in self.shapeTouched_move['points']:
                        point.setPos((point.pos().x()) + distance_x, point.pos().y() + distance_y)
                        for drag_edge in point.node_s_edges:
                            drag_edge.updatePositions()
                        self.scene.update()
                    self.position_orig = self.mapToScene(event.pos())

                    # 填充的多边形的更新
                    if self.shapeTouched_move['shape_type'] == 'polygon':
                        q_pos_list_now = [self.pointGetCentral(node.pos()) for node in self.shapeTouched_move['points']]
                    elif self.shapeTouched_delete['shape_type'] == 'rectangle':
                        q_pos_list_now = [self.pointGetCentral(q_point) for q_point in
                                          self.rectGetPoint(self.shapeTouched_move['points'])]
                    else:
                        return
                    if self.q_pos_list_old != q_pos_list_now:
                        self.emptyPoly()
                        self.fillPoly(q_pos_list_now)
                else:
                    return
            elif self.insideScene(event.pos()) and self.scene.nodes_info['shapes']:
                self.set_arrow_cursor_signal.emit()
                pos = self.mapToScene(event.pos())
                if self.judgePosition(pos) is None:
                    # 靠近点或者线时触发“磁铁”
                    if isinstance(self.getItemAtClick(event), GraphicItem):
                        if self.getItemAtClick(event).shape_type == "line" or self.getItemAtClick(event).shape_type == "point":
                            self.cursor().setPos(self.toQpoint(self.mapToGlobal(self.mapFromScene(
                                self.itemGetCentralPos(self.getItemAtClick(event))))))
                        else:
                            return
                    else:
                        self.graphicsTouched_delete = False
                        self.emptyPoly()
                        self.q_pos_list_old = None
                    return
                else:
                    self.graphicsTouched_delete, self.shapeTouched_delete = self.judgePosition(pos)

                    # 填充多边形/矩形内部
                    if self.shapeTouched_delete['shape_type'] == 'polygon':
                        q_pos_list_now = [self.pointGetCentral(node.pos()) for node in
                                          self.shapeTouched_delete['points']]
                    elif self.shapeTouched_delete['shape_type'] == 'rectangle':
                        q_pos_list_now = [self.pointGetCentral(q_point) for q_point in
                                          self.rectGetPoint(self.shapeTouched_delete['points'])]
                    else:
                        return
                    if ((self.q_pos_list_old != q_pos_list_now) and
                            self.pointsOnScene(self.shapeTouched_delete['points'])):
                        self.emptyPoly()
                        self.fillPoly(q_pos_list_now)
                    return
            else:
                return
        else:
            super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        """鼠标滚轮事件响应

        滚轮控制图片的缩放

        Args:
            event(QEvent): 鼠标滚轮事件

        """
        angle = event.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        angleY = angle.y()  # 竖直滚过的距离
        if self.checkCtrl is True:
            if angleY > 0:
                self.zoomIn()
            else:
                self.zoomOut()

    def zoomIn(self):
        """
        图片放大

        """
        zoom_scale = 1
        zoom_scale = zoom_scale + 0.05
        if zoom_scale >= 10:
            zoom_scale = 10
        self.scale(zoom_scale, zoom_scale)

    def zoomOut(self):
        """
        图片缩小

        """
        zoom_scale = 1
        zoom_scale = zoom_scale - 0.05
        if zoom_scale <= 0:
            zoom_scale = 0.2
        self.scale(zoom_scale, zoom_scale)

    def getItemAtClick(self, event):
        """获取点击位置的图元，无则返回None.

        Args:
            event(QEvent):

        Returns:
            QGraphicsItem: 鼠标点击处的图元对象

        """
        pos = event.pos()
        item = self.itemAt(pos)
        return item

    def edgeDragStart(self, item):
        """
        确认起点端点后开始画线

        Args:
            item(QGraphicsItem): 线段起始的图元对象

        """
        self.drag_start_item = item  # 拖拽开始时的图元，此属性可以不在__init__中声明
        self.drag_edge = Edge(self.drag_start_item, None)  # 开始拖拽线条，注意到拖拽终点为None
        self.scene.addEdge(self.drag_edge)

    def edgeDragEnd(self, item):
        """
        再次点击确认终点图元后在scene上画实线，并删除画线过程中的虚线

        Args:
            item(QgraphicsItem): 终点顶点图元

        """
        new_edge = Edge(self.drag_start_item, item)  # 拖拽结束
        self.scene.addEdge(new_edge)
        self.scene.removeEdge(self.drag_edge)  # 删除拖拽时画的线
        self.drag_edge = None

    def sendData(self):
        """
        用户输入标签名、组号等标签信息后传递数据，保存至已用标签名和组号
        同时将标签名、组号、顶点图元都传入后端信息储存处

        Returns:
            str：标签名
            int：组号
            QgraphicsItem：顶点图元
            QgraphicsScene: 管理所有图元的scene

        """
        name = self.label_dialog.line_edit_label.text()
        group = self.label_dialog.line_edit_groupid.text()

        AllItems1 = [self.label_dialog.comboBox.itemText(i) for i in range(self.label_dialog.comboBox.count())]
        AllItems2 = [self.label_dialog.comboBox2.itemText(i) for i in range(self.label_dialog.comboBox2.count())]
        if name not in AllItems1:
            self.label_dialog.comboBox.addItems([name])
        if group not in AllItems2:
            self.label_dialog.comboBox2.addItems([group])

        if group == '':
            groupint = None
        else:
            groupint = int(self.label_dialog.line_edit_groupid.text())
        self.label_dialog.close()
        nodes = self.scene.addNodesInfo(name, groupint)
        return name, groupint, nodes, self.scene

    def nodeGetEdge(self):
        """
        获取顶点图元对应的线并保存到每个顶点图元对应的属性中

        """
        # for node in self.scene.nodes:
        if self.poly_triggered or self.line_triggered:
            for node in self.scene.nodes:
                node.node_s_edges = [edge for edge in self.scene.edges if
                                     (edge.start_item is node) or (edge.end_item is node)]
        elif self.rect_triggered:
            for node in self.scene.nodes:
                node.node_s_edges = [self.rect_new_edge_one, self.rect_new_edge_two,
                                     self.rect_new_edge_three, self.rect_new_edge_four]

    def judgePosition(self, position_to_judge):
        """
        判断传入的点是否在图形内部

        Args:
            position_to_judge(QPoint): 鼠标点击或者移动时的位置（具体看需要）

        """
        # 判断点击或移动时的鼠标位置
        for shape in self.scene.nodes_info['shapes'].copy():
            # 获得该多边形 或 矩形 所有点中心坐标的list
            if shape['shape_type'] == 'polygon':
                pos_list = [list((self.pointGetCentral(node.pos()).x(),
                                  self.pointGetCentral(node.pos()).y()))
                            for node in shape['points']]
            elif shape['shape_type'] == 'rectangle':
                pos_list = [list((self.pointGetCentral(q_point).x(),
                                  self.pointGetCentral(q_point).y()))
                            for q_point in self.rectGetPoint(shape["points"])]
            elif shape['shape_type'] == 'point' or shape['shape_type'] == 'line':
                continue
            else:
                return
            np.array(pos_list)
            poly_path = mplPath.Path(pos_list)
            if poly_path.contains_point((position_to_judge.x(), position_to_judge.y())):
                return poly_path.contains_point((position_to_judge.x(), position_to_judge.y())), shape
            else:
                continue
        return None

    def confirmDelete(self):
        """
        确认删除某标签后对应的删除操作，包括从scene中移除item和后端信息的清除

        """
        if self.graphicsTouched_delete:
            for point in self.shapeTouched_delete['points']:
                self.scene.removeItem(point)
                for edge in point.node_s_edges:
                    if edge in self.scene.items():
                        self.scene.removeItem(edge)
                    else:
                        continue
            self.scene.nodes_info['shapes'].remove(self.shapeTouched_delete)
            self.scene.removeItem(self.poly_now)
        else:
            for shape in self.scene.nodes_info['shapes']:
                if shape['shape_type'] == 'point' and shape['points'][0] == self.point_now:
                    self.scene.nodes_info['shapes'].remove(shape)
                    self.scene.removeItem(self.point_now)
                    break
                elif shape['shape_type'] == 'line' and self.point_now in shape['points']:
                    self.scene.removeItem(shape['points'][0].node_s_edges[0])
                    self.scene.removeItem(shape['points'][0])
                    self.scene.removeItem(shape['points'][1])
                    self.scene.nodes_info["shapes"].remove(shape)
                    break
                else:
                    continue
        self.delete_label_signal.emit()
        self.delete_confirm.close()

    def pointsOnScene(self, points):
        """
        判断点是否已经被checkbox隐藏了

        Args：
            points(QGraphicsItem): 对应图形的图元顶点

        Returns：
            bool: 点是否被checkbox隐藏

        """
        for point in points:
            if point in self.scene.items():
                return True
            else:
                return False

    def activeExit(self):
        """
        若标签信息录入成功，则发送可编辑信号；
        否则（窗口被直接关闭）撤回一步标记操作

        """
        if self.label_dialog.data_ready:
            self.can_edit_signal.emit()
        elif self.poly_triggered:
            self.edge_enable = True
            self.scene.removeEdge(self.scene.edges[-1])
            self.edgeDragStart(self.scene.nodes[-1])
        elif self.rect_triggered:
            self.scene.removeItem(self.scene.nodes[-1])
            self.scene.removeEdge(self.rect_new_edge_one)
            self.scene.removeEdge(self.rect_new_edge_two)
            self.scene.removeEdge(self.rect_new_edge_three)
            self.scene.removeEdge(self.rect_new_edge_four)
            self.rect_points_list.append(self.rect_draw_points[0])
            self.drawRect([self.rect_draw_points[0]])
        elif self.line_triggered:
            self.edge_enable = True
            self.scene.removeNode(self.scene.nodes[-1])
            self.edgeDragStart(self.scene.nodes[0])
        elif self.point_triggered:
            self.scene.removeNode(self.scene.nodes[0])

    def fillPoly(self, pos_list):
        """
        填充对应多边形

        Args:
             pos_list(list):  存放多边形的QPointF

        """
        q_poly = QPolygonF(pos_list)
        self.poly_now = GraphicPolygonItem(q_poly)
        self.scene.addItem(self.poly_now)
        self.q_pos_list_old = pos_list

    def emptyPoly(self):
        """
        擦除对应多边形

        """
        if self.poly_now in self.scene.items():
            self.scene.removeItem(self.poly_now)

    def pointGetCentral(self, q_point):
        """
        设置图元中央位置在鼠标所点击处并返回中央位置

        Args:
            q_point(QPoint): 鼠标点击处的点对象

        Returns:
            QPoint: 图元位置重设后的点

        """
        q_point.setX(q_point.x() + item_width / 2)
        q_point.setY(q_point.y() + item_width / 2)
        return q_point

    def itemGetCentralPos(self, item):
        """
        获取一个图元点， 返回其中心QpointF坐标

        Args
            item(QgraphicsItem): 图元点

        """
        return QPoint(item.pos().x() + item.width / 2, item.pos().y() + item.height / 2)

    def toQpoint(self, point_f):
        """
        将QPointF转化为QPoint，但是会损失一定的精度

        Args:
            point_f(QPointF): 原先的QPointF点对象

        Returns:
            QPoint: 转化后的QPoint对象

        """
        return QPoint(int(point_f.x()), int(point_f.y()))

    def insideScene(self, event_pos):
        """
        判断鼠标位置在scene里或是外

        Args:
            event_pos(QPoint): 鼠标所在的坐标（相对于view）

        Returns:
            bool:是否在scene内

        """
        if ((0 < self.mapToScene(event_pos).x() < self.scene.width()) and
                (0 < self.mapToScene(event_pos).y() < self.scene.height())):
            return True
        else:
            return False

    def createNode(self, shape_type, event_pos):
        """
        新建顶点图元并加入到scene中

        Args:
            shape_type(str): 新建顶点所在图形类型
            event_pos(QPoint): 鼠标点击处

        Returns:
            QGraphicsItem: 新建的顶点图元对象

        """

        item = GraphicItem()
        sc_pos = self.mapToScene(event_pos)
        item.shape_type = shape_type
        item.setZValue(2)
        item.setPos(sc_pos.x() - item.width / 2, sc_pos.y() - item.height / 2)
        self.scene.addNode(item)
        item.scene = self.scene
        return item

    def drawRect(self, nodes_list):
        """
        绘制矩形

        Args:
            nodes_list(list): 储存矩形两个斜对角顶点图元

        """
        if len(nodes_list) == 1:
            self.drag_rect_new_edge_one = RectEdge(nodes_list[0], None, 1)
            self.drag_rect_new_edge_two = RectEdge(nodes_list[0], None, 2)
            self.drag_rect_new_edge_three = RectEdge(nodes_list[0], None, 3)
            self.drag_rect_new_edge_four = RectEdge(nodes_list[0], None, 4)  # 开始拖拽线条，注意到拖拽终点为None
            self.scene.addEdge(self.drag_rect_new_edge_one)
            self.scene.addEdge(self.drag_rect_new_edge_two)
            self.scene.addEdge(self.drag_rect_new_edge_three)
            self.scene.addEdge(self.drag_rect_new_edge_four)
        if len(nodes_list) == 2:
            self.rect_new_edge_one = RectEdge(nodes_list[0], nodes_list[1], 1)
            self.rect_new_edge_two = RectEdge(nodes_list[0], nodes_list[1], 2)
            self.rect_new_edge_three = RectEdge(nodes_list[0], nodes_list[1], 3)
            self.rect_new_edge_four = RectEdge(nodes_list[0], nodes_list[1], 4)  # 拖拽结束
            self.scene.addEdge(self.rect_new_edge_one)
            self.scene.addEdge(self.rect_new_edge_two)
            self.scene.addEdge(self.rect_new_edge_three)
            self.scene.addEdge(self.rect_new_edge_four)
            self.scene.removeEdge(self.drag_rect_new_edge_one)
            self.scene.removeEdge(self.drag_rect_new_edge_two)
            self.scene.removeEdge(self.drag_rect_new_edge_three)
            self.scene.removeEdge(self.drag_rect_new_edge_four)

    def rectGetPoint(self, pair_points):
        """
        通过矩形已知的两个点， 得到所有的四个点的坐标

        Args:
            pair_points(list): 储存矩形两个对应点

        Returns:
            list: 储存矩形所有4个点的q_point

        """
        all_list = []
        q_point_1 = QPointF(0.0, 0.0)
        q_point_2 = QPointF(0.0, 0.0)
        x_list = [pair_points[0].x(), pair_points[1].x()]
        y_list = [pair_points[0].y(), pair_points[1].y()]
        q_point_1.setX(x_list[0])
        q_point_1.setY(y_list[1])
        q_point_2.setX(x_list[1])
        q_point_2.setY(y_list[0])
        all_list.extend([pair_points[0].pos(), q_point_1, pair_points[1].pos(), q_point_2])
        return all_list
