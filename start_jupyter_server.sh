#!/bin/sh

# Switch users to the VOLTTRON user and start a Jupyter server on the indicated port

JUPYTER_PORT=$1
su $VOLTTRON_USER -c "source start_jupyter.sh ${JUPYTER_PORT}"
