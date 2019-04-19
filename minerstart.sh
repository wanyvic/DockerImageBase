#!/bin/bash
# MINER_ADDRESS="address"
# MINER_WORKER="worker"
# MINER_POOL="pool"
# MINER_TYPE="MGD"
case $MINER_TYPE in
MGD)
    echo "miner type: mgd"
    MINER_PATH="/root/MassGridMiner_0.2.1_Ubuntu_docker/bfgminer"
    export TERMINFO=/usr/share/terminfo
    export TERM=xterm-basic
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MINER_PATH/.libs/
    MINER_BIN="$MINER_PATH/bfgminer" 
    MINER_ARGS=''
    if [ -n "$MINER_ADDRESS" ]; then
        MINER_ARGS="$MINER_ARGS -u $MINER_ADDRESS"
        if [ -n "$MINER_WORKER" ]; then
            MINER_ARGS="$MINER_ARGS.$MINER_WORKER"
        fi
        if [ -n "$MINER_POOL" ]; then
            MINER_ARGS="$MINER_ARGS -o stratum1+tcp://$MINER_POOL"
        fi
        MINER_ARGS="$MINER_ARGS -p x -S opencl:auto --eexit"
        echo "setsid $MINER_BIN $MINER_ARGS >/dev/null &"
        setsid $MINER_BIN $MINER_ARGS >/dev/null &
    fi
    ;;
ETH)
    echo "miner type: eth"
    MINER_PATH="/root/ethminer"
    MINER_BIN="$MINER_PATH/ethminer" 
    MINER_ARGS=''
    if [ -n "$MINER_ADDRESS" ]; then
        MINER_ARGS="$MINER_ARGS -P stratum1+tcp://$MINER_ADDRESS"
        if [ -n "$MINER_WORKER" ]; then
            MINER_ARGS="$MINER_ARGS.$MINER_WORKER"
        fi
        if [ -n "$MINER_POOL" ]; then
            MINER_ARGS="$MINER_ARGS@$MINER_POOL"
        fi
        MINER_ARGS="$MINER_ARGS -U"
        echo "setsid $MINER_BIN $MINER_ARGS >/dev/null &"
        setsid $MINER_BIN $MINER_ARGS >/dev/null &
    fi   
    ;;
*)
    echo "Other command!"  
    ;;
esac