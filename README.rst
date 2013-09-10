=====
Dotns
=====

It's experimental name service for nanomsg. The nanomsg branch that is going
to work with this is::

http://github.com/tailhook/nanomsg

The project is research project only and neither is nor intended to be
production ready name service


Running
=======

Basic usage is::

    python3 -m dotns --bind tcp://127.0.0.1:1111 --dot-file examples/simple/topology.dot

There are a few examples that run name service and imaginary cluster of nodes::

    ./examples/simple/reqrep.sh
    ./examples/prio/reqrep.sh
    ./examples/twodc/reqrep.sh

(the last one is the most comprehensive so the most interesting)


