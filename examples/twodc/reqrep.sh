#!/bin/bash

killjobs() {
    kill $(jobs -p) 2> /dev/null
}
trap killjobs 1 2 15 0

export NN_NAME_SERVICE=ipc://./run/name_service

echo "Running reqrep topology with pid $$"

mkdir run > /dev/null

python -m dotns --dot-file examples/twodc/topology.dot --bind $NN_NAME_SERVICE  --verbose &
sleep 1

NN_OVERRIDE_HOSTNAME=felicia  NN_APPLICATION_NAME=frontend_2 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=felicia  NN_APPLICATION_NAME=frontend_1 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=florence NN_APPLICATION_NAME=frontend_1 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=florence NN_APPLICATION_NAME=frontend_2 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gina     NN_APPLICATION_NAME=output     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gina     NN_APPLICATION_NAME=input      nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=laura    NN_APPLICATION_NAME=device     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=lisa     NN_APPLICATION_NAME=device     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=worker_2   nanocat --rep    --topology topology -Dwally_2  &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=device     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=worker_1   nanocat --rep    --topology topology -Dwally_1  &
NN_OVERRIDE_HOSTNAME=wilson   NN_APPLICATION_NAME=worker_2   nanocat --rep    --topology topology -Dwilson_2 &
NN_OVERRIDE_HOSTNAME=wilson   NN_APPLICATION_NAME=worker_1   nanocat --rep    --topology topology -Dwilson_1 &
NN_OVERRIDE_HOSTNAME=warren   NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -Dwarren   &
NN_OVERRIDE_HOSTNAME=wayne    NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -Dwayne    &
NN_OVERRIDE_HOSTNAME=wilfred  NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -Dwilfred  &
NN_OVERRIDE_HOSTNAME=willy    NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -Dwilly    &
NN_OVERRIDE_HOSTNAME=faith    NN_APPLICATION_NAME=frontend_2 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=faith    NN_APPLICATION_NAME=frontend_1 nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gloria   NN_APPLICATION_NAME=output     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gloria   NN_APPLICATION_NAME=input      nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=lora     NN_APPLICATION_NAME=device     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=winnie   NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -D         winnie  &
NN_OVERRIDE_HOSTNAME=winston  NN_APPLICATION_NAME=worker     nanocat --rep    --topology topology -D         winston &

sleep 1
echo "We have done initialization. You can query the cluster with the following"
echo "NN_NAME_SERVICE=$NN_NAME_SERVICE nanocat --req --topology topology -D hello -A -i1"

echo "But we will show you tree clients columns:"
echo "(Hint: you can kill processes and see how failover works)"

mknod ./run/cluster_pipe p 2> /dev/null
nanocat --req --topology topology -D hello -A -i1 > ./run/cluster_pipe &

ADDRESS_CMD=(nanocat --req --connect=$NN_NAME_SERVICE -D'REQUEST client client topology://topology NN_REQ' --raw)

dc1address=$("${ADDRESS_CMD[@]}" | grep '127.1' | sed 's/connect:1:/--connect=/g')
dc2address=$("${ADDRESS_CMD[@]}" | grep '127.2' | sed 's/connect:1:/--connect=/g')

mknod ./run/dc1_pipe p 2> /dev/null
nanocat --req $dc1address -D hello_dc2 -A -i1 > ./run/dc1_pipe &

mknod ./run/dc2_pipe p 2> /dev/null
nanocat --req $dc2address -D hello_dc1 -A -i1 > ./run/dc2_pipe &

echo "Both       DC1        DC2"
python columnize.py ./run/cluster_pipe ./run/dc1_pipe ./run/dc2_pipe
