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
    rate 1Mbit peakrate 1001kbit mtu 8192 latency 100s burst 154000000

# FILTER APPLICATION TRAFFIC VERSUS NON APP TRAFIC
$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip src 10.1.1.0/24 flowid 1:1

$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip dst 10.1.1.0/24 flowid 1:1

$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip dst 192.168.122.2 flowid 1:1

$TC filter add dev ${DEV} protocol ip parent 1: prio 1 u32 \
    match ip dst 192.168.122.4 flowid 1:1

$TC filter add dev ${DEV} protocol ip parent 1: prio 2 u32 \
    match ip src 192.168.122.0/24 flowid 1:2
