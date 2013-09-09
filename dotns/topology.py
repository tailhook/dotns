class Topology(object):

    def __init__(self, graph):
        self.graph = graph
        self.hosts = [gr.name[len('cluster_'):]
            for gr in graph.all_subgraphs
            if 'ip' in gr.prop]
        self.processes = [node.name for node in graph.all_nodes]

    def resolve(self, appname, host):
        print("APPNAME", appname, "HOST", host)

    @property
    def pairs(self):
        for gr in self.graph.all_subgraphs:
            grname = gr.name[len('cluster_'):]
            if 'ip' not in gr.prop:
                continue
            for node in gr.nodes.values():
                yield grname, node.name
