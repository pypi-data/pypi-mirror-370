#!/bin/bash -e
################################################################################
##  File:  sim-start.sh
##  Desc:  Start the Composabl Sim Wrapper
################################################################################
PATH_SIM=${1:-/composabl/sim}
SIM_CONFIG_JSON=${2:-"{}"}

HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"1337"}

# Start the Sim Client Wrapper
echo "$0: Starting the Sim Wrapper"
python3 /opt/composabl/main.py --path $PATH_SIM --config $SIM_CONFIG_JSON --port $PORT --host $HOST
