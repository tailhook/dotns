#!/bin/sh

export NN_NAME_SERVICE=ipc://./run/name_service

echo "Running reqrep topology with pid $$"

python -m dotns --dot-file examples/simple/topology.dot --bind $NN_NAME_SERVICE --verbose &
sleep 1

echo starting
NN_OVERRIDE_HOSTNAME=worker NN_APPLICATION_NAME=worker1 nanocat --rep --topology topology -Done &
NN_OVERRIDE_HOSTNAME=worker NN_APPLICATION_NAME=worker2 nanocat --rep --topology topology -Dtwo &

while [ "$(jobs)" != "" ]; do
    sleep 1
done
