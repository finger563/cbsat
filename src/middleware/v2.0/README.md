# Using the Network Middleware

This README covers the building, configuration, and usage of the
networking middleware modules `TC Wrapper`, `Sender`, `Receiver`,
`Client`, `Server`.  These modules provide functionality for network
traffic management and generation.

These modules require network profiles to be provided to them
(generally through an API or through the command line).  These
profiles have the form:

```csv
# period = <period in seconds>
# start = <start time in seconds>
# priority = <priority of the profile>
# uuid = <uuid of the profile>
< time (s), bandwidth (bps), max bandwidth (bps), latency (ms) >
```

## TC Wrapper

The TC Wrapper is an automated utility for configuring the linux
advanced routing and traffic control (TC) utilities.  These utilities
allow the configuration of prioritized network queues and filters with
various options, including bandwidth and latency enforcement on
outgoing traffic.  The TC Wrapper is a convenience utility for
configuring a token bucket filter (TBF) or heirarchical token buket
filter (HTB) that already exists in the system according to a network
profile.  Following the profile, the TC Wrapper configures the
following parameters for these filters as a function of time:

* Bandwidth (bits/sec)
* Buffer Size (bits)
* Latency (ms)

### Building

Build the TC Wrapper by issuing `make tcWrapper`.

### Configuration

The machine on which TC Wrapper is run must be preconfigured with TC
to have either a Token Bucket Filter (TBF) or a Heirarchical Token
Bucket Filter (HTB).  These filters are specified with a parent node
and a handle ID, in addition to configuration parameters such as
bandwidth, buffer size, and latency.

Such TC configuration can be configured for instance through the
following command:

```bash
sudo tc qdisc del dev $INTERFACE root
sudo tc qdisc add dev $INTERFACE root handle 1: tbf\
	rate 100Mbit peakrate 101Mbit mtu 8192 latency 1ms burst 1540
```

where `$INTERFACE` corresponds to the network interface, e.g. `eth0`.  In this example, the `parent` of the TBF is `root` and the `handle` is `1:`

Some example configurations for TC configuration can be found in this repository in various `tc_config*.sh` scripts, in subfolders of the [analysis subfolder](../../analysis/v2.0/).

The TC Wrapper is configured through the command line through the
following options:

```bash
--profile      <profile name>
--is_router    (this node is a router node)
--use_tbf      (TC filter is TBF)
--use_htb      (TC filter is HTB)
--buffer       <buffer size>
--interface    <interface name>
--parent       <parent TC object>
--handle       <handle TC object>
```

### Usage

The TC Wrapper must be run as `root`, and the arguments available to be interpreted by the program are described above.  TC Wrapper will continue to regulate the interface according to the profile until it is cancelled or killed.  The interface's filter should be removed at the end of the experiment by calling

```bash
sudo tc qdisc del dev $INTERFACE root
```

## Sender

### Building

The sender is a library to be used in other code and as such does not
have a build target.

### Configuration

### Usage

## Receiver

### Building

The receiver is a library to be used in other code and as such does
not have a build target.

### Configuration

### Usage

## Client

### Building

Build the Client by issuing `make client`.

### Configuration

### Usage

## Server

### Building

Build the Server by issuing `make server`.

### Configuration

### Usage
