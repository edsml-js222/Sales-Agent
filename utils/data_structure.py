from typing import Union
class Vertex():
    """用于表示话术节点的顶点类"""
    def __init__(self, index, content):
        self.index = index
        self.content = content

def nodes_to_vets(nodes: list[list[int, str]]) -> list["Vertex"]:
    vets = [Vertex(node[0], node[1]) for node in nodes]
    return vets

class DirectGraphAdjList():
    """基于邻接表实现的有向图"""
    def __init__(self, edges: list[list[Vertex, str]]):
        # define adj list
        self.adj_list = dict[Vertex, dict[str, Vertex]]()
        # define the intention list each node can have  
        self.intention_list = dict[Vertex, list[str]]()
        for edge in edges:
            self.add_vertex(edge[0])
            self.add_edge(edge[0], edge[1], edge[2])
    
    def add_vertex(self, vet: Vertex):
        if vet in self.adj_list:
            return
        self.adj_list[vet] = {}
        self.intention_list[vet] = []
    
    def add_edge(self, vet_1: Vertex, vet_2: Vertex, intention: str):
        if vet_1 not in self.adj_list or vet_1 == vet_2:
            raise ValueError()
        self.adj_list[vet_1][intention] = vet_2
        self.intention_list[vet_1].append(intention)

    def print(self):
        """print the adj list"""
        print("话术节点表: ")
        for vertex in self.adj_list:
            vet_edges = {key: val.index for (key, val) in self.adj_list[vertex].items()}
            print(f"{vertex.index} -- {vet_edges}")




if __name__ == '__main__':
    nodes = [
        [1, "您好，这里是深圳艺星医疗整形医院。请问您之前有打过瘦脸针吗？"],
        [2, "请问您是男士还是女士，今年多大年龄呢？"],
        [3, "瘦脸针是针对咬肌肥大的医美技术，非常安全，一周见效，效果很好的，可以放心。您微信多少我加您，给您详细介绍下，我们现在瘦脸针做活动的"],
        [4, "那可以给您预约过来实际面诊医生看看呢，可以吗？"],
        [5, "您是有什么顾虑么？我们现在特价580，预约来院还送一次光子嫩肤的"],
        [6, "我们现在特价580，预约来院还送一次光子嫩肤的"],
        [7, "您是在深圳哪个区呢，您今天有空的话在市区可以申请一次免费打车接您过来面诊医生实际了解下。面诊咨询都是免费的，可以评估下您咬肌情况，您对方案和价格都满意再考虑做"],
        [8, "好的，那留个联系方式n可以先加个您的微信 我把具体定位发给您 还有我们医院介绍, 我帮您预约下时间"],
        [9, " 好的那您时间方便的话，过来之前可以拨打0755-12345678预约面诊医生时间，然后按预约时间过来就好。到时候见"],
        [10, "好的，再见"],
    ]
    vets = nodes_to_vets(nodes=nodes)
    # check vets
    # for vet in vets:
    #     print(vet.index)
    #     print(vet.content)
    #     print(vet)
    edges = [
        [vets[0], vets[1], "肯定"],
        [vets[0], vets[2], "否定"],
        [vets[0], vets[9], "拒绝"],
        [vets[1], vets[3], "all"],
        [vets[2], vets[3], "all"],
        [vets[3], vets[4], "拒绝"],
        [vets[3], vets[5], "肯定"],
        [vets[4], vets[6], "all"],
        [vets[5], vets[6], "all"],
        [vets[6], vets[7], "肯定"],
        [vets[6], vets[8], "拒绝"],
        [vets[6], vets[8], "其他"],
        [vets[7], vets[8], "拒绝"],
        [vets[7], vets[8], "其他"],
        [vets[7], vets[9], "留资"],
        [vets[8], vets[9], "all"]
    ]

    graph = DirectGraphAdjList(edges)
    graph.print()


    