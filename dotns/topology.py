from collections import defaultdict


def first(iterable):
    return next(iter(iterable))


classification = {
    'NN_REQ': 'source',
    'NN_REP': 'sink',
    'NN_PUSH': 'source',
    'NN_PULL': 'sink',
    'NN_PUB': 'source',
    'NN_SUB': 'sink',
    }


class Topology(object):

    def __init__(self, graph):
        self.graph = graph
        self.hosts = {gr.name[len('cluster_'):]: gr
            for gr in graph.all_subgraphs
            if 'ip' in gr.prop}
        self.processes = {node.name: node for node in graph.all_nodes}
        self.source_addresses = defaultdict(list)
        self.sink_addresses = defaultdict(list)
        self._minport = defaultdict(lambda: 10000)
        self._traverse_hosts()
        self._prepare_addresses()

    def print_addresses(self):
        for k, lst in self.source_addresses.items():
            print('SOURCE', *k)
            for a in lst:
                print('   ', a)
        for k, lst in self.sink_addresses.items():
            print('SINK', *k)
            for a in lst:
                print('   ', a)


    def _alloc_bind(self, host):
        ip = self._host_to_ip[host]
        port = self._minport[ip]
        self._minport[ip] += 1
        addr = 'tcp://{}:{}'.format(ip, port)
        return addr

    def _connect_to(self, app):
        for a in self.addresses[app]:
            if a.startswith('bind:'):
                return 'connect:' + a[len('bind:'):]
        raise AssertionError("Can't find an address")

    def _traverse_hosts(self):
        self._host_to_ip = host_to_ip = {}
        self._node_to_pair = nodepairs = {}
        for gr in self.graph.all_subgraphs:
            if not gr.name.startswith('cluster_') or 'ip' not in gr.prop:
                continue
            host = gr.name[len('cluster_'):]
            host_to_ip[host] = gr.prop['ip']
            for node in gr.nodes.values():
                nodepairs[node.name] = (host, node.appname)

    def _prepare_addresses(self):
        from_mapping = defaultdict(set)
        to_mapping = defaultdict(set)
        all_connections = defaultdict(
            lambda: (defaultdict(set), defaultdict(set)))
        for edge in self.graph.all_edges:
            es = edge.start
            ee = edge.end
            if ':' in es:
                es = es[:es.index(':')]
            if ':' in ee:
                ee = ee[:ee.index(':')]
            pri = all_connections[int(edge.prop.get('priority', 1))]
            pri[0][es].add(ee)
            pri[1][ee].add(es)

        for priority, (from_mapping, to_mapping) in all_connections.items():
            for source, sinks in from_mapping.items():
                if source == 'client':  # client never bind
                    for sink in sinks:
                        shost, sapp = self._node_to_pair[sink]
                        addr = self._alloc_bind(shost)
                        # Only source addresses have (useful meaning of) priority
                        caddr = 'connect:{}:{}'.format(priority, addr)
                        baddr = 'bind:1:{}'.format(addr)
                        self.source_addresses[None, 'client'].append(caddr)
                        self.sink_addresses[shost, sapp].append(baddr)
                else:  # but sources are usually bound (except client)
                    shost, sapp = self._node_to_pair[source]
                    addr = self._alloc_bind(shost)
                    # Only source addresses have (useful meaning of) priority
                    baddr = 'bind:{}:{}'.format(priority, addr)
                    caddr = 'connect:1:{}'.format(addr)
                    self.source_addresses[shost, sapp].append(baddr)
                    for sink in sinks:
                        pair = self._node_to_pair[sink]
                        self.sink_addresses[pair].append(caddr)


    def resolve(self, hostname, appname, socktype):
        if classification[socktype] == 'source':
            if hostname not in self.hosts:
                # everything unknown are clients
                return self.source_addresses[None, 'client']
            return self.source_addresses[hostname, appname]
        else:
            return self.sink_addresses[hostname, appname]

    @property
    def pairs(self):
        for gr in self.graph.all_subgraphs:
            grname = gr.name[len('cluster_'):]
            if 'ip' not in gr.prop:
                continue
            for node in gr.nodes.values():
                yield grname, node.appname
