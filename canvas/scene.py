from PyQt5.QtWidgets import QGraphicsScene


class GraphicScene(QGraphicsScene):
    """
    该类用作 QGraphicsItems 的容器

    Attributes:
        nodes(list): 用于储存当前绘制图形的顶点图元
        edges(list): 用于储存当前绘制图形的边
        shapes(list): 用于储存当前scene中的图形
        nodes_info（dict): 用于暂时储存所有的图形信息 （参考json的格式）
        store_info():

    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.nodes = []  # 存储图元
        self.edges = []  # 存储连线

        self.shapes = []
        self.nodes_info = {'shapes': []}
        self.store_info = None

    def addNode(self, node):
        """
        将新建的顶点图元添加至scene中，同时添加到储存顶点的list中

        Args:
            node(QgraphicsItem): 新建的顶点图元

        """
        self.nodes.append(node)
        self.addItem(node)

    def removeNode(self, node):
        """
        将需要删除的顶点图元从scene和储存的list中移除

        Args:
            node(QgraphicsItem): 需要移除的顶点图元

        """
        self.nodes.remove(node)
        self.removeItem(node)

        for edge in self.edges.copy():
            if edge.start_item is node or edge.end_item is node:
                self.removeEdge(edge)
                self.update()

    def addEdge(self, edge):
        """
        将新建的边添加到scene和储存边的list中

        Args:
            edge(QGraphicsPathItem): 新建的边

        """
        self.edges.append(edge)
        self.addItem(edge)

    def removeEdge(self, edge):
        """
        将删除的边从scene和储存边的list中移除

        Args:
            edge(QGraphicsPathItem): 需要删除的边

        """
        self.removeItem(edge)
        self.edges.remove(edge)
        self.update()

    def addNodesInfo(self, label, group_id):
        """
        将新建的图形信息添加到暂时储存的dictionary中

        Args:
            label(str): 标签名
            group_id(int): 分组编号

        Returns:
            list:所有的顶点图元

        """
        all_info_temp = {'label': label, 'points': self.nodes.copy(), 'group_id': group_id,
                         'shape_type': self.nodes[0].shape_type, 'flags': {}}
        self.nodes_info['shapes'].append(all_info_temp)
        self.edges = []
        self.nodes = []
        return all_info_temp['points']
