import re

re.compile("""
    (?P<kw> graph
        | subgraph)
    | (?P<delim>[]=,;{})
    | (?P<comment>//.*\n)
    | (?P<quote>")
    | (?P<anglebracket><)
    | (?P<newline>\n)
    """, re.X


class Node(object):

    def __init__(self, name):
        self.name = name


class Edge(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end


class Graph(object):

    def __init__(self):
        self.edges = []
        self.nodes = {}


class Parser(object):

    def __init__(self, file):
        self._file = file

    def _tokenize(self):
        for match in self._tokeniter:
            # TODO(tailhook) check tokenizer
            for gname, tok in match.groups():
                if tok is None:
                    continue
                break
            yield from getattr(self, '_tok_' + gname)(tok)


    def parse(self, file):
        for token in self._tokenize():
            print(token)
