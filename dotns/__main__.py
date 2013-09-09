import argparse
import os.path
from functools import partial

from . import nanomsg
from . import dot
from . import topology


TOPOLOGIES = {}


def serve_request(req, verbose=False):
    if verbose:
        print("dotns: Got request:", repr(req))
    _req, host, appname, topology = req.decode('ascii').split()
    assert _req == 'REQUEST'
    result = list(TOPOLOGIES[topology].resolve(host, appname))
    if verbose:
        print("dotns: Result:", ';'.join(result))
    return '\n'.join(result).encode('ascii')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--dot-file', metavar="PATH",
        help='The file name to get topology from '
             "(it's base name is also a name of the topology)",
        required=True)
    ap.add_argument('-v', '--verbose',
        help='The file name to get topology from',
        default=False, action='store_true')
    ap.add_argument('-b', '--bind',
        help='The nanomsg address to bind to for name requests',
        required=True)
    ap.add_argument('--print-hosts',
        help='Print all host names in the topology file and exit',
        default=False, action='store_true')
    ap.add_argument('--print-apps',
        help='Print all app names in the topology file and exit',
        default=False, action='store_true')
    ap.add_argument('--print-host-app-pairs',
        help='Print all host-app pairs in the topology file and exit',
        default=False, action='store_true')

    options = ap.parse_args()
    with open(options.dot_file, 'rt') as f:
        graph = dot.Parser(f).parse_one()

    tname = os.path.basename(os.path.splitext(options.dot_file)[0])
    TOPOLOGIES[tname] = topology.Topology(graph)

    if options.print_hosts:
        for h in TOPOLOGIES[tname].hosts:
            print(h)
    elif options.print_apps:
        for p in TOPOLOGIES[tname].processes:
            print(p)
    elif options.print_host_app_pairs:
        for h, a in TOPOLOGIES[tname].pairs:
            print(h, a)
    else:
        nanomsg.reply_service(options.bind,
            partial(serve_request, verbose=False))


if __name__ == '__main__':
    main()

