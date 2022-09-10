from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsPathItem
from PyQt5.QtGui import QPixmap, QColor, QPen, QPainterPath, QBrush
from PyQt5.QtCore import Qt, QPointF


class GraphicItem(QGraphicsPixmapItem):
    """
    此类用于创建”点“对象

    Attributes:
        pix(QPixmap):绘出顶点图元
        width(int): 图元宽度
        height(int): 图元高度
        scene = None
        shape_type(str): 表示该顶点所在图形形状
        node_s_edges(list): 储存该顶点所连的线

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.pix = QPixmap("E:\\pythonProject3\\labelall0716PM\\item_dot_25\\red.png")
        self.pix = QPixmap("./item_dot_25/red.png")
        # "E:\\pythonProject3\\labelall0716PM\\item_dot_25\\red.png"
        self.width, self.height = self.pix.width(), self.pix.height()
        self.setPixmap(self.pix)  # 设置图元
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.scene = None

        self.shape_type = None
        self.node_s_edges = []

    def mouseMoveEvent(self, event):
        """
        图元被拖拽时更新线条

        Args:
            event(QEvent): 鼠标移动事件（同时鼠标有按键被按下）

        """
        super().mouseMoveEvent(event)
        if self.itemChange(QGraphicsItem.ItemPositionChange, self.mapToScene(event.pos())):
            for edge in self.node_s_edges:
                edge.updatePositions()

    def itemChange(self, change, value):
        """
        判断图元位置是否改变

        Args:
            change(bool):位置是否变化
            value(QPoint):新位置的点对象

        Returns:
            QPoint: 新位置的点对象
            bool： 位置是否变化

        """
        if change == QGraphicsItem.ItemPositionChange:
            # value is the new position.
            newPos = value
            rect = self.scene.sceneRect()
            if not rect.contains(newPos):
                # Keep the item inside the scene rect.
                newPos.setX(min(rect.right(), max(newPos.x(), rect.left())) - self.width / 2)
                newPos.setY(min(rect.bottom(), max(newPos.y(), rect.top())) - self.height / 2)
                self.setPos(newPos)
                return newPos
        return QGraphicsItem.itemChange(self, change, value)


class Edge(QGraphicsPathItem):
    """
    此类用于创建多边形的边或线段，即“线”对象

    Attributes:
        start_item(QGraphicsItem): 一条边或线段的起始顶点图元
        end_item(QGraphicsItem): 一条边或线段的结束顶点图元
        pos_src(list): 线条起始位置 x, y坐标
        pos_dst(list): 线条结束位置 x, y坐标
        pen(QPen):画线条的画笔
        pen_dragging(QPen):画拖拽线条（虚线）的画笔

    """
    def __init__(self, start_item, end_item, parent=None):
        super().__init__(parent)

        self.start_item = start_item
        self.end_item = end_item

        # 设置线条初始化参数
        self.width = 2.0  # 线条的宽度
        self.pos_src = [0, 0]  # 线条起始位置 x，y坐标
        self.pos_dst = [0, 0]  # 线条结束位置
        self.pen = QPen(QColor("red"))  # 画线条的
        self.pen.setWidthF(self.width)
        self.pen_dragging = QPen(QColor("red"))  # 画拖拽线条时线条的
        self.pen_dragging.setStyle(Qt.DashDotLine)
        self.pen_dragging.setWidthF(self.width)
        self.setFlag(QGraphicsItem.ItemIsSelectable)  # 线条可选
        self.setZValue(1)  # 让线条出现在所有图元的最下层

        # 开始更新
        if self.start_item is not None:
            self.updatePositions()

    def set_src(self, x, y):
        """
        更新要画的边的起点位置坐标

        Args:
            x(int): 起点位置的横坐标
            y(int): 起点位置的纵坐标

        """
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        """
        更新要画的边的终点位置坐标

        Args:
            x(int): 终点位置的横坐标
            y(int): 终点位置的纵坐标

        """
        self.pos_dst = [x, y]

    # 计算线条的路径
    def calcPath(self):
        """
        计算线条路径

        Returns:
            QPainterPath：计算出的线条路径

        """
        path = QPainterPath(QPointF(self.pos_src[0], self.pos_src[1]))  # 起点
        path.lineTo(self.pos_dst[0], self.pos_dst[1])  # 终点
        return path

    # 更新位置
    def updatePositions(self):
        """
        更新线条位置

        """
        # src_pos 记录的是开始图元的位置，此位置为图元的左上角
        src_pos = self.start_item.pos()
        # 想让线条从图元的中心位置开始，让他们都加上偏移
        patch = self.start_item.width / 2
        self.set_src(src_pos.x() + patch, src_pos.y() + patch)
        # 如果结束位置图元也存在，则做同样操作
        if self.end_item is not None:
            end_pos = self.end_item.pos()
            self.set_dst(end_pos.x() + patch, end_pos.y() + patch)
        else:
            self.set_dst(src_pos.x() + patch, src_pos.y() + patch)
        self.update()

    def shape(self):
        """
        返回计算出的线条路径画出的图形对象

        Returns：
             QPainterPath：计算出的线条路径

        """
        return self.calcPath()

    def paint(self, painter, graphics_item, widget=None):
        """绘制图形

        Args:
            painter(QPen):画笔
            graphics_item:
            widget:

        Returns:

        """
        self.setPath(self.calcPath())  # 设置路径
        path = self.path()
        if self.end_item is None:
            # 刚开始拖拽线条时，并没有结束位置的图元，所以是None
            painter.setPen(self.pen_dragging)  # 此时画虚线
            painter.drawPath(path)
        else:
            # 这时画的才是连接后的线(实线)
            painter.setPen(self.pen)
            painter.drawPath(path)


class GraphicPolygonItem(QGraphicsPolygonItem):
    """
    此类用于填充多边形

    """
    def __init__(self, *__args):
        super().__init__(*__args)
        self.poly, = __args
        # print(self.poly)
        self.calcPath()

    def calcPath(self):
        """
        计算多边形路径并绘制

        """
        self.path = QPainterPath()
        self.path.addPolygon(self.poly)

    def paint(self, painter, graphics_item, widget=None):
        """
        填充多边形内部

        """
        brush = QBrush(QColor(200, 0, 0, 50))
        painter.fillPath(self.path, brush)


class RectEdge(QGraphicsPathItem):
    """
    此类用于绘制矩形（不含顶点）

    Attributes:
        pos_src(list): 线条起始位置 x, y坐标
        pos_dst(list): 线条结束位置 x, y坐标
        start_item(QGraphicsItem): 一条边或线段的起始顶点图元
        end_item(QGraphicsItem): 一条边或线段的结束顶点图元
        patch(float): 图元定位偏差调整
        num_draw(int): 矩形边的序号
        width(float):线条宽度

    """
    def __init__(self, start_item, end_item, num_draw, parent=None):
        super().__init__(parent)
        self.num_draw = num_draw
        self.start_item = start_item
        self.end_item = end_item
        # 设置线条初始化参数
        self.width = 2.0  # 线条的宽度
        self.pos_src = [0, 0]  # 线条起始位置 x，y坐标
        self.pos_dst = [0, 0]  # 线条结束位置
        self.pen = QPen(QColor("red"))  # 画线条的
        self.pen.setWidthF(self.width)
        self.pen_dragging = QPen(QColor("red"))  # 画拖拽线条时线条的
        self.pen_dragging.setStyle(Qt.DashDotLine)
        self.pen_dragging.setWidthF(self.width)
        self.setFlag(QGraphicsItem.ItemIsSelectable)  # 线条可选
        self.setZValue(1)  # 让线条出现在所有图元的最下层
        self.patch = self.start_item.width / 2

        # 开始更新
        if self.start_item is not None:
            self.updatePositions()

    def set_src(self, x, y):
        """
        更新要画的边的起点位置坐标

        Args:
            x(int): 起点位置的横坐标
            y(int): 起点位置的纵坐标

        """
        self.pos_src = [x + self.patch, y + self.patch]

    def set_dst(self, x, y):
        """
        更新要画的边的终点位置坐标

        Args:
            x(int): 终点位置的横坐标
            y(int): 终点位置的纵坐标

        """
        self.pos_dst = [x + self.patch, y + self.patch]

    # 计算线条的路径
    def calcPath(self):
        """
        计算线条路径

        Returns:
            QPainterPath: 计算出的线条路径对象

        """
        path = QPainterPath(QPointF(self.pos_src[0], self.pos_src[1]))  # 起点
        path.lineTo(self.pos_dst[0], self.pos_dst[1])  # 终点
        return path

    # 更新位置
    def updatePositions(self):
        """更新线条位置

        """
        # src_pos 记录的是开始图元的位置，此位置为图元的左上角
        # 想让线条从图元的中心位置开始，让他们都加上偏移
        patch = self.start_item.width / 2
        # 如果结束位置图元也存在，则做同样操作
        sta_pos = self.start_item.pos()
        if self.end_item is None:
            if self.num_draw == 1:
                self.set_dst(sta_pos.x(), sta_pos.y())  # 起点第一个点
                self.set_src(sta_pos.x(), sta_pos.y())  # 终点一半是更新的
            if self.num_draw == 2:
                self.set_dst(sta_pos.x(), sta_pos.y())  # 起点第一个点
                self.set_src(sta_pos.x(), sta_pos.y())  # 终点一半是更新的
            if self.num_draw == 3:
                self.set_dst(sta_pos.x(), sta_pos.y())  # 起点鼠标位置
                self.set_src(sta_pos.x(), sta_pos.y())  # 终点一半是更新的
            if self.num_draw == 4:
                self.set_dst(sta_pos.x(), sta_pos.y())  # 起点鼠标位置
                self.set_src(sta_pos.x(), sta_pos.y())  # 终点一半是更新的
        else:
            end_pos = self.end_item.pos()
            if self.num_draw == 1:
                self.set_dst(sta_pos.x(), end_pos.y())
                self.set_src(sta_pos.x(), sta_pos.y())
            if self.num_draw == 2:
                self.set_dst(end_pos.x(), sta_pos.y())
                self.set_src(sta_pos.x(), sta_pos.y())
            if self.num_draw == 3:
                self.set_dst(end_pos.x(), sta_pos.y())
                self.set_src(end_pos.x(), end_pos.y())
            if self.num_draw == 4:
                self.set_dst(sta_pos.x(), end_pos.y())
                self.set_src(end_pos.x(), end_pos.y())
        self.update()

    def shape(self):
        """
        返回计算出的线条路径画出的图形对象

        Returns：
             QPainterPath：计算出的线条路径

        """
        return self.calcPath()

    def paint(self, painter, graphics_item, widget=None):
        """
        绘制图形

        Args:
            painter(QPen):画笔
            graphics_item():

        """
        self.setPath(self.calcPath())  # 设置路径
        path = self.path()
        if self.end_item is None:
            # 刚开始拖拽线条时，并没有结束位置的图元，所以是None
            painter.setPen(self.pen_dragging)  # 此时画虚线
            painter.drawPath(path)
        else:
            # 这时画的才是连接后的线(实线)
            painter.setPen(self.pen)
            painter.drawPath(path)

