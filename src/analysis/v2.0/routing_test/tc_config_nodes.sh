#!/bin/bash

TC=/sbin/tc

DEV=eth0

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

$TC qdisc add dev ${DEV} root handle 1: prio

$TC qdisc add dev ${DEV} parent 1:1 handle 11: netem delay 100ms
$TC qdisc add dev ${DEV} parent 1:2 handle 12: pfifo

$TC qdisc add dev ${DEV} parent 11:1 handle 111: tbf \
    rate 1Mbit burst 10kb latency 100000ms peakrate 1.01mbit minburst 1540
echo "set qdiscs up"

# FILTER APPLICATION TRAFFIC VERSUS NON APP TRAFIC
$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip dst 10.1.1.2 flowid 1:1
$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip dst 10.1.1.4 flowid 1:1
echo "set priority filters up"

$TC filter add dev ${DEV} protocol ip parent 1: prio 2 u32 \
    match ip src 192.168.122.0/24 flowid 1:2
$TC filter add dev ${DEV} protocol ip parent 1: prio 2 u32 \
    match ip src 10.1.1.0/24 flowid 1:2
echo "set other filters up"
