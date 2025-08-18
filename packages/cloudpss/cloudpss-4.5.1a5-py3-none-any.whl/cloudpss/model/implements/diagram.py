from .component import Component
from typing import Optional
import uuid


class DiagramImplement(object):
    """
        拓扑实现
    """

    def __init__(self, diagram: dict = {}):
        """
            初始化
        """
        for k, v in diagram.items():
            if k == 'cells':
                self.__dict__[k] = v
                for key, val in v.items():
                    v[key] = Component(val)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(DiagramImplement, self).__getattribute__(attr)

    def toJSON(self):
        """
            类对象序列化为 dict
            :return: dict

            >>>> diagram.toJSON()
        """
        cells = {}
        for key, val in self.cells.items():
            cells[key] = val.toJSON()
        diagram = {**self.__dict__, 'cells': cells}
        return diagram

    def getAllComponents(self):
        """
            获取所有元件

            :return: dict<Component>

            >>>> diagram.getAllComponents()
        """

        return self.cells
    
    def addComponent(
        self,
        definition: str,
        label: str,
        args: dict = {},
        pins: dict = {},
        canvas: Optional[str] = None,
        position: Optional[dict] = None,
        size: Optional[dict] = None,
    ) -> Component:
        """
        添加元件

        :param definition 元件定义， 连接线没有definition
        :param label 元件标签
        :param args 元件参数数据，连接线没有参数数据
        :param pins 元件引脚数据，连接线没有引脚数据
        :param canvas 元件所在图纸数据
        :param position 元件位置数据, 连接线没有位置数据
        :param size 元件大小数据，连接线没有大小数据

        :return: Component

        >>>> diagram.addComponent(args)
        """
        id = "comp_" + str(uuid.uuid4())
        shape = "diagram-component"
        definition = definition
        label = label or definition
        args = args.copy()
        pins = pins.copy()
        props = {"enabled": True}
        context = {}
        canvas or self.canvas[0].get("key", "canvas_0")
        position = position.copy() if position else {"x": 0, "y": 0}
        size = size.copy() if size else None
        zIndex = 0
        style = {
            "--fill": "var(--spectrum-global-color-gray-100)",
            "--fill-opacity": 1,
            "--font-family": "var(--spectrum-global-font-family-base, Arial, Helvetica, sans-serif)",
            "--stroke": "var(--spectrum-global-color-gray-900)",
            "--stroke-opacity": 1,
            "--stroke-width": 2,
            "--text": "var(--spectrum-global-color-gray-900)",
            "--text-opacity": 1,
        }
        diagram = {
            "id": id,
            "shape": shape,
            "definition": definition,
            "label": label,
            "args": args,
            "pins": pins,
            "props": props,
            "context": context,
            "canvas": canvas,
            "position": position,
            "size": size,
            "zIndex": zIndex,
            "style": style,
        }
        component = Component(diagram)
        self.cells[id] = component
        return component

    def removeComponent(self, key: str) -> bool:
        """
        删除元件

        :param key: str
        :return: bool

        >>>> diagram.removeComponent(key)
        """
        component = self.cells.get(key)
        if not component:
            return False
        position = component.position.copy()
        del self.cells[key]
        for edge in self.cells.values():
            if edge.shape == "diagram-edge":
                if edge.source.get("cell") == key:
                    edge.source = position.copy()
                    position["x"] += 5
                    position["y"] += 5

                if edge.target.get("cell") == key:
                    edge.target = position.copy()
                    position["x"] += 5
                    position["y"] += 5
        return True

    def updateComponent(self, key: str, args: dict) -> bool:
        """
        更新元件

        :param key: str
        :param args: dict
        :return: bool

        >>>> diagram.updateComponent(key)
        """
        component = self.cells.get(key)
        if not component:
            return False
        for k, v in self.cells.items():
            if k == key:
                v.__dict__.update(args)
                return True
