from collections import defaultdict


def first(iterable):
    return next(iter(iterable))


class Topology(object):

    def __init__(self, graph):
        self.graph = graph
        self.hosts = {gr.name[len('cluster_'):]: gr
            for gr in graph.all_subgraphs
            if 'ip' in gr.prop}
        self.processes = {node.name: node for node in graph.all_nodes}
        self.addresses = defaultdict(list)
        self._minport = defaultdict(lambda: 10000)
        self._app_to_ip = {}
        self._prepare_addresses()
        import pprint; pprint.pprint(self.addresses)

    def _alloc_bind(self, app):
        ip = self._app_to_ip[app]
        port = self._minport[ip]
        self._minport[ip] += 1
        addr = 'bind:tcp://{}:{}'.format(ip, port)
        self.addresses[app].append(addr)
        return addr

    def _connect_to(self, app):
        for a in self.addresses[app]:
            if a.startswith('bind:'):
                return 'connect:' + a[len('bind:'):]
        raise AssertionError("Can't find an address")

    def _prepare_addresses(self):
        from_mapping = defaultdict(set)
        to_mapping = defaultdict(set)
        for edge in self.graph.all_edges:
            es = edge.start
            ee = edge.end
            if ':' in es:
                es = es[:es.index(':')]
            if ':' in ee:
                ee = ee[:ee.index(':')]
            from_mapping[es].add(ee)
            to_mapping[ee].add(es)

        self._app_to_ip = app_to_ip = {}
        for gr in self.graph.all_subgraphs:
            grname = gr.name[len('cluster_'):]
            if 'ip' not in gr.prop:
                continue
            ip = gr.prop['ip']
            for node in gr.nodes.values():
                app_to_ip[node.name] = ip

        for app, targets in from_mapping.items():
            if app == 'client':  # special app, never binds
                for tgt in targets:
                    self._alloc_bind(tgt)
                    self.addresses[app].append(self._connect_to(tgt))
                continue
            if len(targets) == 1:  # we have one connection
                tgt = first(targets)
                if len(to_mapping[tgt]) > 1:  #one to many
                    if tgt not in self.addresses:
                        self._alloc_bind(tgt)
                    self.addresses[app].append(self._connect_to(tgt))
                else:  # one to one
                    self._alloc_bind(app)
                    self.addresses[tgt].append(self._connect_to(app))
            elif len(targets) > 1:  # we have many connections
                if any(len(to_mapping[tgt]) > 1 for tgt in targets):
                    # many to many
                    if app in to_mapping:  # we are device
                        self._alloc_bind(app)
                        for tgt in targets:
                            self.addresses[tgt].append(self._connect_to(app))
                    else:
                        raise NotImplementedError(app)
                else:
                    self._alloc_bind(app)
                    for tgt in targets:
                        self.addresses[tgt].append(self._connect_to(app))

    def resolve(self, hostname, appname):
        if hostname not in self.hosts:
            return self.addresses['client']   # everything unknown are clients
        return self.addresses[appname]

    @property
    def pairs(self):
        for gr in self.graph.all_subgraphs:
            grname = gr.name[len('cluster_'):]
            if 'ip' not in gr.prop:
                continue
            for node in gr.nodes.values():
                yield grname, node.name
