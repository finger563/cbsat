#!/bin/bash

TC=/sbin/tc
DEV=eth0

USETBF="false"
BW=70000
DELAY=0
BUCKET=100
BUFFER=10000

PRINT_STATUS="false"
CLEAR="false"

for i in "$@"
do
    case $i in
	-p|--print)
	    PRINT_STATUS="true"
	    shift # past argument=value
	    ;;
	--clear)
	    CLEAR="true"
	    shift # past argument=value
	    ;;
	-d=*|--delay=*)
	    DELAY="${i#*=}"
	    shift # past argument=value
	    ;;
	-b=*|--bandwidth=*)
	    BW="${i#*=}"
	    shift # past argument=value
	    ;;
	-k=*|--bucket=*)
	    BUCKET="${i#*=}"
	    shift # past argument=value
	    ;;
	-f=*|--buffer=*)
	    BUFFER="${i#*=}"
	    shift # past argument=value
	    ;;
	--use_tbf)
	    USETBF="true"
	    shift # past argument with no value
	    ;;
	--use_htb)
	    USETBF="false"
	    shift # past argument with no value
	    ;;
	*)
	    # unknown option
	    ;;
    esac
    done

echo "Using options:"
echo "  use_tbf:   ${USETBF}"
echo "  bandwidth: ${BW}"
echo "  delay:     ${DELAY}"
echo "  bucket:    ${BUCKET}"
echo "  buffer:    ${BUFFER}"

if [[ "$PRINT_STATUS" = "true" ]]
then
    $TC -s qdisc ls dev $DEV
    $TC -s class ls dev $DEV
exit
fi

# clean existing down- and uplink qdiscs, hide errors
$TC qdisc del dev $DEV root    2> /dev/null > /dev/null
$TC qdisc del dev $DEV ingress 2> /dev/null > /dev/null

if [[ "$CLEAR" = "true" ]]
then
    exit
fi

let "PEAKBW=${BW}+10"
let "BW2=${BW}+${BW}"

###### uplink

$TC qdisc add dev ${DEV} root handle 1: prio
$TC qdisc add dev ${DEV} parent 1:1 handle 11: netem delay ${DELAY}ms
$TC qdisc add dev ${DEV} parent 1:2 handle 12: pfifo

if [[ "$USETBF" = "true" ]]
then
    $TC qdisc add dev ${DEV} parent 11:1 handle 2: tbf \
	rate ${BW}bit limit ${BUFFER}k burst ${BUCKET}

    $TC qdisc add dev ${DEV} parent 2: handle 21: prio
    $TC qdisc add dev ${DEV} parent 21:1 handle 211: pfifo
    $TC qdisc add dev ${DEV} parent 21:2 handle 212: pfifo
else
    $TC qdisc add dev ${DEV} parent 11:1  handle 2: htb
    $TC class add dev ${DEV} parent 2: classid 2:1 htb rate ${BW2}bit
    $TC class add dev ${DEV} parent 2:1 classid 2:10 htb rate ${BW}bit ceil ${PEAKBW}bit prio 0
    $TC class add dev ${DEV} parent 2:1 classid 2:20 htb rate ${BW}bit ceil ${PEAKBW}bit prio 1
    
    $TC qdisc add dev ${DEV} parent 2:10 handle 21: pfifo
    $TC qdisc add dev ${DEV} parent 2:20 handle 22: pfifo
fi
echo "set qdiscs up"

# FILTER APPLICATION TRAFFIC
$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip src 10.1.1.0/24 flowid 1:1

# PRIORITIZE CERTAIN APPLICATION TRAFFIC
if [[ "$USETBF" = "true" ]]
then
    $TC filter add dev ${DEV} protocol ip parent 21: prio 1 u32 \
	match ip src 10.1.1.1 flowid 21:1

    $TC filter add dev ${DEV} protocol ip parent 21: prio 2 u32 \
	match ip src 10.1.1.3 flowid 21:2
else
    $TC filter add dev ${DEV} protocol ip parent 2: prio 1 u32 \
	match ip src 10.1.1.1 flowid 2:10

    $TC filter add dev ${DEV} protocol ip parent 2: prio 2 u32 \
	match ip src 10.1.1.3 flowid 2:20
fi
echo "set application filters up"

# FILTER NON APPLICATION TRAFFIC
$TC filter add dev ${DEV} protocol ip parent 1: prio 2 u32 \
    match ip src 191.168.127.0/24 flowid 1:2
echo "set non-application filters up"

