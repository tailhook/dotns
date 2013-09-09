import re
import ast


TOKEN_RE = re.compile(r"""
    (?P<keyword> graph|digraph|subgraph)
    | (?P<name>\w+(?:\:\w+)*)
    | (?P<delim>[\[\]=,;\{\}\n])
    | (?P<arrow>[-][\>-])
    | (?P<comment>//.*\n)
    | (?P<quote>")
    | (?P<anglebracket>\<)
    """, re.X)
QUOTED_RE = re.compile(r"""
    [^"]*
    #(?<!\\)
    "
    """, re.X)


class Node(object):

    def __init__(self, name):
        self.name = name
        self.prop = {}


class Edge(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end


class GraphBase(object):

    def add_node(self, name):
        if not name in self.nodes:
            self.nodes[name] = Node(name)
        return self.nodes[name]

    def set_node_properties(self, name, props):
        self.add_node(name).prop.update(props)


class Subgraph(GraphBase):

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.nodes = {}
        self.prop = {}


class AnonymousSubgraph(object):

    def __init__(self):
        self.nodes = set()
        self.prop = {}

    def add_node(self, name):
        self.nodes.add(name)


class Digraph(GraphBase):

    def __init__(self, name):
        self.name = name
        self.edges = []
        self.nodes = {}
        self.subgraphs = []


class Parser(object):

    def __init__(self, file):
        self._data = file.read()
        self._pos = 0

    def _tok_comment(self, match, val):
        return ()

    def _tok_quote(self, match, val):
        m = QUOTED_RE.match(self._data, self._pos)
        if not m:
            raise ValueError("Unclosed quotes")
        self._pos = m.end()
        yield 'quoted', val + m.group(0)

    def _tok_anglebracket(self, match, val):
        lev = 1
        for i in range(self._pos, len(self._data)):
            c = self._data[i]
            if c == '<':
                lev += 1
            elif c == '>':
                lev -= 1
            if lev == 0:
                break
        start = self._pos
        self._pos = i + 1
        yield 'angled', self._data[start:self._pos]

    def _retoken(self):
        while True:
            match = TOKEN_RE.search(self._data, self._pos)
            if match is None:  # eof
                sep = self._data[self._pos:].strip()
                if sep.strip():
                    raise ValueError("Unexpected token {!r}".format(sep[:16]))
                break
            npos = match.start()
            sep = self._data[self._pos:npos].strip()
            if sep.strip():
                raise ValueError("Unexpected token {!r}".format(sep[:16]))
            self._pos = npos
            yield match

    def _tokenize(self):
        for match in self._retoken():
            # TODO(tailhook) check tokenizer
            for gname, tok in match.groupdict().items():
                if tok is not None:
                    break
            else:
                raise RuntimeError("Something wrong")
            meth = getattr(self, '_tok_' + gname, None)
            self._pos += len(tok)
            if meth is None:
                yield gname, tok
            else:
                yield from meth(match, tok)


    def parse_one(self):
        self._tokeniter = self._tokenize()
        try:
            return next(self._parse_graph())
        except ValueError as e:
            raise ValueError("{} at line {}".format(e.args[0],
                self._data.count('\n', 0, self._pos)+1))

    def _assert_token(self, tname, tvalue=None):
        name, value = next(self._tokeniter)
        if name != tname:
            raise ValueError("Unexpected token {!r}".format(tvalue))
        elif tvalue is not None and (isinstance(tvalue, tuple) and
            value not in tvalue or tvalue != value):
            raise ValueError("Expected {!r} but {!r} found"
                .format(tvalue, value))
        return value

    def _parse_arrow(self, tvalue, subvalue):
        pass

    def _parse_value(self):
        valuetype, value = next(self._tokeniter)
        if valuetype == 'quoted':
            value = ast.literal_eval(value)
        elif valuetype == 'name':
            pass
        elif valuetype == 'anglebracket':
            value = value[1:-1]
        else:
            raise ValueError("Unexpected {!r}".format(value[:16]))
        return value

    def _parse_edges(self, node, edge_type):
        if edge_type == '--':
            self.e = Edge()


    def _parse_properties(self):
        result = {}
        while True:
            nametype, name = next(self._tokeniter)
            if nametype == 'delim':
                if name == ']':
                    return result
                elif name == ',':
                    continue  # comma allowed, just skip it
                else:
                    raise ValueError("Unexpected {!r}".format(name))
            if nametype != 'name':
                raise ValueError("Unexpected {!r}".format(name))
            self._assert_token('delim', '=')
            result[name] = self._parse_value()


    def _parse_graph_body(self, g):
        for tname, tvalue in self._tokeniter:
            if tname == 'name':
                subname, subvalue = next(self._tokeniter)
                if subname == 'delim':
                    if subvalue == '\n':
                        g.add_node(tvalue)
                    elif subvalue == '=':
                        g.prop[tvalue] = self._parse_value()
                        etype, evalue = next(self._tokeniter)
                        if etype != 'delim':
                            raise ValueError("Unexpected {!r}".format(evalue))
                        if evalue == '}':
                            break
                        if evalue not in ('\n', ';'):
                            raise ValueError("Unexpected {!r}".format(evalue))
                    elif subvalue == '{':
                        g1 = AnonymousSubgraph(g)
                        self._parse_graph_body(g1)
                    elif subvalue == '[':
                        props = self._parse_properties()
                        g.set_node_properties(tvalue, props)
                    else:
                        raise ValueError("Unexpected {!r}".format(subvalue))
                    continue
                elif subname == 'name':
                    raise NotImplementedError()
                elif subname == 'arrow':
                    for edge in self._parse_edges(tvalue, subvalue):
                        g.edges.append(edge)
                    continue
            elif tname == 'keyword':
                if tvalue == 'subgraph':
                    name = self._assert_token('name')
                    self._assert_token('delim', '{')
                    g1 = Subgraph(name, g)
                    self._parse_graph_body(g1)
                    continue
            elif tname == 'delim':
                if tvalue == '}':
                    break
                elif tvalue == '\n':
                    continue
            raise ValueError("Unexpected {!r}".format(tvalue))

    def _parse_graph(self):
        self._assert_token('keyword', 'digraph')
        g = Digraph(self._assert_token('name'))
        self._assert_token('delim', '{')
        self._parse_graph_body(g)
        yield g


if __name__ == '__main__':
    import sys
    Parser(sys.stdin).parse_one()
