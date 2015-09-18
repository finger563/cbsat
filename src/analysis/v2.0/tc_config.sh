#!/bin/bash

TC=/sbin/tc

DEV=eth1

if [[ "$1" = "prio" ]]
then
    CEIL=170
    DOWNLINK=768
else
    CEIL=370
    DOWNLINK=2048
fi

if [[ "$1" = "status" ]]
then
    $TC -s qdisc ls dev $DEV
    $TC -s class ls dev $DEV
exit
fi

# clean existing down- and uplink qdiscs, hide errors
$TC qdisc del dev $DEV root    2> /dev/null > /dev/null
$TC qdisc del dev $DEV ingress 2> /dev/null > /dev/null

if [[ "$1" = "stop" ]]
then
    exit
fi

###### uplink

$TC qdisc add dev ${DEV} root handle 1: netem delay 100ms
$TC qdisc add dev ${DEV} parent 1:1 handle 11: tbf rate 20kbit burst 20kB peakrate 20kbit mtu 1500
$TC qdisc add dev ${DEV} parent 11:1 handle 111: prio
$TC qdisc add dev ${DEV} parent 111:1 handle 1111: pfifo
$TC qdisc add dev ${DEV} parent 111:2 handle 1112: pfifo
$TC filter add dev ${DEV} parent 111: prio 1 protocol ip u32 match ip src 10.1.1.1 flowid 111:1
$TC filter add dev ${DEV} parent 111: prio 1 protocol ip u32 match ip src 10.1.1.2 flowid 111:2
