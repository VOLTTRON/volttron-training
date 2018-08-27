#!/bin/sh

# Start a Jupyter server on the indicated port

JUPYTER_PORT=$1

source $VOLTTRON_ROOT/env/bin/activate
cd $VOLTTRON_ROOT/examples/JupyterNotebooks
jupyter notebook --ip 0.0.0.0 --port ${JUPYTER_PORT} --no-browser --allow-root &
