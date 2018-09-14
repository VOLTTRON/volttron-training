#!/bin/sh

CONTAINER_NAME=$1
PORT=$2
VC_PORT=$3

PWD=`pwd`
LOCAL_IP=$(getent hosts $(hostname) | awk '{print $1}')

cat > $PWD/config << EOF
volttron-central-address = http://$LOCAL_IP:$VC_PORT
vip-address = tcp://$LOCAL_IP:$PORT
instance-name = "tcp://$LOCAL_IP:$PORT"
bind-web-address = http://$LOCAL_IP:$VC_PORT
EOF

sudo docker run \
    -d \
    -v $PWD/config:/home/volttron/volttron/config \
    -e VOLTTRON_HOME=/home/volttron/$CONTAINER_NAME \
    --name=$CONTAINER_NAME \
    --net=host \
    --memory="512m" \
    -it hackathon
