#! /usr/bin/env bash

source ${VOLTTRON_ROOT}/env/bin/activate

#cd ${VOLTTRON_ROOT}
#python /home/volttron/setup-platform.py

yes | cp -rf /home/volttron/volttron ${VOLTTRON_HOME}

PID=$?
echo "the pid is $PID"
if [ "$PID" == "0" ]; then
    volttron -vv -l log1
fi
