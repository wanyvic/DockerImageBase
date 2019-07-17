#!/bin/bash
# MINER_ADDRESS="address"
# MINER_WORKER="worker"
# MINER_POOL="pool"
# MINER_POOL1="pool"
# MINER_POOL2="pool"
# MINER_TYPE="MGD"
/usr/local/bin/start.sh >/dev/null &
case $MINER_TYPE in
MGD)
    echo "miner type: mgd"
    export MINER_PATH="/root/MassGridMiner_0.2.1_Ubuntu/bfgminer"
    export TERMINFO=/usr/share/terminfo
    export TERM=xterm
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MINER_PATH/.libs/
    MINER_BIN="$MINER_PATH/bfgminer"
    MINER_ARGS=''
    if [ -n "$MINER_ADDRESS" ]; then
        MINER_ARGS="$MINER_ARGS -u $MINER_ADDRESS"
        if [ -n "$MINER_WORKER" ]; then
            MINER_ARGS="$MINER_ARGS.$MINER_WORKER"
        fi
        if [ -n "$MINER_POOL" ]; then
            MINER_ARGS="$MINER_ARGS -o stratum+tcp://$MINER_POOL"
        elif [ -n "$MINER_POOL1" ]; then
            MINER_ARGS="$MINER_ARGS -o stratum+tcp://$MINER_POOL1"
        fi
        MINER_ARGS="$MINER_ARGS -p x -S opencl:auto --eexit 1"
        echo "$MINER_BIN $MINER_ARGS >/dev/null"
        cd $MINER_PATH
        $MINER_BIN $MINER_ARGS > /dev/null
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
        echo "$MINER_BIN $MINER_ARGS >/dev/null"
        $MINER_BIN $MINER_ARGS >/dev/null
    fi
    ;;
*)
    echo "Other command!"  
    ;;
esac
