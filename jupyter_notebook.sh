#!/bin/sh

# Within the indicated running Docker container, start a Jupyter server on the indicated port

CONTAINER_NAME=$1
JUPYTER_PORT=$2
docker exec -it $CONTAINER_NAME bash -c "source start_jupyter_server.sh ${JUPYTER_PORT}"
