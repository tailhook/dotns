#!/bin/sh

export NN_NAME_SERVICE=ipc://./run/name_service

echo "Running reqrep topology with pid $$"

python -m dotns --dot-file examples/twodc/topology.dot --bind $NN_NAME_SERVICE --verbose &
sleep 1

NN_OVERRIDE_HOSTNAME=felicia  NN_APPLICATION_NAME=felicia_2     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=felicia  NN_APPLICATION_NAME=felicia_1     nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=florence NN_APPLICATION_NAME=florence_1    nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=florence NN_APPLICATION_NAME=florence_2    nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gina     NN_APPLICATION_NAME=gina_output   nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gina     NN_APPLICATION_NAME=gina_input    nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=laura    NN_APPLICATION_NAME=laura_device  nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=lisa     NN_APPLICATION_NAME=lisa_device   nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=wally_2       nanocat --rep    --topology topology -Dwally_2 &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=wally_lb      nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=wally    NN_APPLICATION_NAME=wally_1       nanocat --rep    --topology topology -Dwally_1 &
NN_OVERRIDE_HOSTNAME=wilson   NN_APPLICATION_NAME=wilson_2      nanocat --rep    --topology topology -Dwilson_2 &
NN_OVERRIDE_HOSTNAME=wilson   NN_APPLICATION_NAME=wilson_1      nanocat --rep    --topology topology -Dwilson_1 &
NN_OVERRIDE_HOSTNAME=warren   NN_APPLICATION_NAME=warren        nanocat --rep    --topology topology -Dwarren &
NN_OVERRIDE_HOSTNAME=wayne    NN_APPLICATION_NAME=wayne         nanocat --rep    --topology topology -Dwayne &
NN_OVERRIDE_HOSTNAME=wilfred  NN_APPLICATION_NAME=wilfred       nanocat --rep    --topology topology -Dwilfred &
NN_OVERRIDE_HOSTNAME=willy    NN_APPLICATION_NAME=willy         nanocat --rep    --topology topology -Dwilly &
NN_OVERRIDE_HOSTNAME=faith    NN_APPLICATION_NAME=faith_2       nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=faith    NN_APPLICATION_NAME=faith_1       nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gloria   NN_APPLICATION_NAME=gloria_output nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=gloria   NN_APPLICATION_NAME=gloria_input  nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=lora     NN_APPLICATION_NAME=lora_device   nanodev --reqrep --topology topology &
NN_OVERRIDE_HOSTNAME=winnie   NN_APPLICATION_NAME=winnie        nanocat --req    --topology topology -D winnie &
NN_OVERRIDE_HOSTNAME=winston  NN_APPLICATION_NAME=winston       nanocat --req    --topology topology -D winston &

while [ "$(jobs)" != "" ]; do
    sleep 1
done
