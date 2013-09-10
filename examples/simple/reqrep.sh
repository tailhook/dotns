#!/bin/sh

killjobs() {
    kill $(jobs -p)
}
trap killjobs 1 2 15 0

export NN_NAME_SERVICE=ipc://./run/name_service

echo "Running reqrep topology with pid $$"

python -m dotns --dot-file examples/simple/topology.dot --bind $NN_NAME_SERVICE --verbose &
sleep 1

echo starting
NN_OVERRIDE_HOSTNAME=worker NN_APPLICATION_NAME=worker1 nanocat --rep --topology topology -Done &
NN_OVERRIDE_HOSTNAME=worker NN_APPLICATION_NAME=worker2 nanocat --rep --topology topology -Dtwo &

sleep 1
echo "We have done initialization. Let's query the cluster"
echo "NN_NAME_SERVICE=$NN_NAME_SERVICE nanocat --req --topology topology -D hello -A -i1"
nanocat --req --topology topology -D hello -A -i1
