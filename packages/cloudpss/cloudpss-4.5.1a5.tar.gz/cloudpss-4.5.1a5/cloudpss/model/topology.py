import asyncio
import json

from ..utils import request, graphql_request


class ModelTopology():
    """
        项目拓扑类

        通过 该类的静态方法 fetch 获取一个拓扑实例

        实例变量说明：

        components 摊平后的拓扑元件，参数和引脚不再保留表达式的形式，如果元件为拓扑实现，并有读取权限时将被展开

        mappings   拓扑分析后的一些映射数据


    """
    __modelTopologyQuery = """
            query($a:ModelTopologyInput!){
            modelTopology(input:$a){
                components
                mappings
            }}
        """
    __All__ = ['ModelTopology']

    def __init__(self, topology: dict = {}):
        self.__dict__.update(topology)

    def toJSON(self):
        """
            将类转换为 dict 数据
        """
        data = {**self.__dict__}

        return data

    @staticmethod
    def dump(topology, filePath, indent=None):
        """
            以 JSON 格式保存数据到指定文件

            :params: topology 拓扑实例
            :params: file 文件路径
            :params: indent json 格式缩进
        """
        data = topology.toJSON()
        f = open(filePath, 'w', encoding='utf-8')
        json.dump(data, f, indent=indent)
        f.close()
        
    @staticmethod
    def fetch(hash, implementType, config, maximumDepth=None, **kwargs):
        """
            获取拓扑

            :params: hash 
            :params: implementType 实现类型
            :params: config 参数方案
            :params: maximumDepth 最大递归深度，用于自定义项目中使用 diagram 实现元件展开情况

            : return: 拓扑实例

            >>> data = ModelTopology.fetch('','emtp',{})

        """
        args = {} if config is None else config['args']
        variables = {
            "a": {
                'hash': hash,
                'args': args,
                'acceptImplementType': implementType,
                'maximumDepth': maximumDepth
            }
        }
        data = graphql_request(ModelTopology.__modelTopologyQuery, variables, **kwargs)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

        return ModelTopology(data['data']['modelTopology'])
        
    


