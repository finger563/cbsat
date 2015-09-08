.. _design_time:

=====================
 Design Time Results
=====================

These results provide a methodology and a means for application
developers and system integrators to determine conservative, precise,
tightly bounded performance metrics for distributed networked
applications and systems at design time.  The contributions of this
work are broken into sections by topic:

* :ref:`periodic_system_analysis`
* :ref:`periodic_analysis_proof`
* :ref:`nc_comparison`
* :ref:`tdma_analysis`
* :ref:`compositional_analysis`
* :ref:`delay_analysis`
* :ref:`routing_analysis`

.. _periodic_system_analysis:

Periodic System Analysis
========================

One subset of systems which we would like to analyze are periodic
systems, since many systems in the real world exhibit some form of
periodicity, e.g. satellites in orbit, traffic congestion patterns,
power draw patterns.  We define systems to be periodic if the data
production rate (or consumption rate) of the system is a periodic
function of time.  The time-integral of these periodic data
consumption/production rates is the cumulative data
production/consumption of the system.  These cumulative functions are
called *repeating*.

Given that the required data profile and system data service profile
are *repeating*, we must determine the periodicity of the output
profile.  If we can show that the output profile similarly repeats,
then we can show that the system has no unbounded buffer growth.
First, let us look at the profile behavior over the course of its
first two periods of activity.

We will examine two systems, *system (1)* and *system (2)*.  Firstly,
examine *(1)*, shown below (note: you can click on the images to open
them in a larger format):

+---------------------------------------------------+-----------------------------------------------------+
| System *(1)* Bandwidth for 1 Period               | System *(1)* Data for 1 Period                      |
+===================================================+=====================================================+
| .. image:: /images/results/1-period-system-bw.png | .. image:: /images/results/1-period-system-data.png |
|    :height: 200                                   |    :height: 200                                     |
+---------------------------------------------------+-----------------------------------------------------+

+---------------------------------------------------+-----------------------------------------------------+
| System *(1)* Bandwidth for 2 Periods              | System *(1)* Data for 2 Periods                     |
+===================================================+=====================================================+
| .. image:: /images/results/2-period-system-bw.png | .. image:: /images/results/2-period-system-data.png |
|    :height: 200                                   |    :height: 200                                     |
+---------------------------------------------------+-----------------------------------------------------+

We notice that for this example system, the second period output
profile is not an exact copy of the first (most easily seen by
examining the bandwidth plots), and yet the required buffer size is
still the same as it was when analyzing the system over one period.
Furthermore, by running the analysis over even larger number of
periods, we can determine (not plotted here for space and
readability), that the predicted buffer size does not change no matter
how many periods we analyze for this system.

Let us look at a system where this is not the case before we begin the
analysis of such system characteristics.

+-----------------------------------------------------+-------------------------------------------------------+
| System *(2)* Bandwidth for 1 Period                 | System *(2)* Data for 1 Period                        |
+=====================================================+=======================================================+
| .. image:: /images/results/1-period-unstable-bw.png | .. image:: /images/results/1-period-unstable-data.png |
|    :height: 200                                     |    :height: 200                                       |
+-----------------------------------------------------+-------------------------------------------------------+

+-----------------------------------------------------+-------------------------------------------------------+
| System *(2)* Bandwidth for 2 Periods                | System *(2)* Data for 2 Periods                       |
+=====================================================+=======================================================+
| .. image:: /images/results/2-period-unstable-bw.png | .. image:: /images/results/2-period-unstable-data.png |
|    :height: 200                                     |    :height: 200                                       |
+-----------------------------------------------------+-------------------------------------------------------+

Notice in system *(2)*, the first period analysis predicted the same
buffer size and delay as system *(1)*, but when analyzing two periods
the predicted buffer size changed.  Clearly the behavior of the system
is changing between these two periods.  If we continue to analyze more
periods of system *(2)*, as we did with system *(1)*, we'll find the
unfortunate conclusion that the predicted buffer size increases with
every period we add to the analysis.

We have discovered a system level property that can be calculated from
these profiles, but we must determine what it means and how it can be
used.  First, we see that in system *(1)*, the predicted required
buffer size does not change regarless of the number of periods over
which we analyze the system.  Second, we see that for system *(2)*,
the predicted required buffer size changes depending on how many
periods of activity we choose for our analysis window.  Third, we see
that the second period of system *(2)* contains the larger of the two
predicted buffer sizes.  These observations (with our understanding of
deterministic periodic systems) lead us to the conclusion: system
*(2)* can no longer be classified as periodic, since its behavior is
not consistent between its periods.  Furthermore, because the required
buffer size predicted for system system *(2)* continually increases,
we can determine that the system is in fact *unstable* due to
unbounded buffer growth.  

.. _periodic_analysis_proof:

Proving the Minimum Analysis for System Stability
-------------------------------------------------

Let us now formally prove the assertion about system periodicity and
stability which has been stated above.  We will show that our analysis
results provide quantitative measures about the behavior of the system
and we will determine for how long we must analyze a system to glean
such behaviors.

Typically, periodicity is defined for functions as the equality:

.. math:: x(t) = x(t + k * T), \forall k \in \mathbb{N} > 0

but for our type of system analysis this cannot hold since we deal
with cumulative functions (of data vs. time).  Instead we must define
a these functions to be **repeating**, where a function is repeating
*iff*:

.. math:: x(0) &= 0 \text{  and}\\
	  x(t + k * T) &= x(t) + k * x(T), \forall k \in \mathbb{N} > 0

Clearly, a repeating function :math:`x` is **periodic** *iff*
:math:`x(T)=0`.  Note that repeating functions like the cumulative
data vs. time profiles we deal with, are the result of **integrating**
*periodic* functions, like the periodic bandwidth vs. time profiles we
use to describe application network traffic and system network
capacity.  All periodic functions, when integrated, produce repeating
functions and similarly, all repeating functions, when differentiated,
procduce periodic functions.

Now we will consider a deterministic, *repeating* queuing system
providing a data service function :math:`S` to input data function
:math:`I` to produce output data function :math:`O`, where these
functions are *cumulative data versus time*.  At any time :math:`t`,
the amount of data in the system's buffer is given by :math:`B_t`.
After servicing the input, the system has a remaining capacity
function :math:`R`.

* :math:`S[t]` : the service function of the system, cumulative data
  service capacity versus time
* :math:`I[t]` : the input data to the system, cumulative data versus
  time
* :math:`O[t]` : the output data from the system, cumulative data
  versus time
* :math:`B[t]` : the amount of data in the system's buffer at time
  :math:`t`, i.e. :math:`I[t]-O[t]`
* :math:`R[t]` : the remaining service capacity of the system after
  servicing :math:`I`, i.e. :math:`S[t] - O[t]`

Because :math:`S` and :math:`I` are deterministic and repeating, they
increase deterministically from period to period, i.e. given the
period :math:`T_I` of :math:`I`,

.. math:: \forall t, \forall n \in \mathbb{N} > 0 : I[t + n*T_I] =
          I[t] + n*I[T_I]

Similarly, given the period :math:`T_S` of :math:`S`,

.. math:: \forall t, \forall n \in \mathbb{N} > 0 : S[t + n*T_S] =
          S[t] + n*S[T_S]

We can determine the hyperperiod of the system as the :math:`lcm` of
input function period and the service function period, :math:`T_p =
lcm(T_S,T_I)`.

At the start of the system, :math:`t=0`, the system's buffer is empty,
i.e.  :math:`B[0] = 0`.  Therefore, the amount of data in the buffer
at the end of the first period, :math:`t=T_p`, is the amount of data
that entered the system on input function :math:`I` but was not able
to be serviced by :math:`S`.  At the start of the next period, this
data will exist in the buffer.  Data in the buffer at the start of the
period can be compared to the system's remaining capacity :math:`R`,
since the remaining capacity of the system indicates how much extra
data it can transmit in that period.  Consider the scenario that the
system's remaining capacity :math:`R` is less than the size of the
buffer, i.e. :math:`R[T_p] < B[T_p]`.  In this scenario,
:math:`B[2*T_p] > B[T_p]`, i.e. there will be more data in the buffer
at the end of the second period than there was at the end of the first
period.  Since the system is deterministic, for any two successive
periods, :math:`n*T_p` and :math:`(n+1)*T_p`, :math:`B[n*T_p] >
B[(n+1)*T_p]`, which extends to:

.. math::
   B[m*T_p] > B[n*T_p], \forall m>n>0

implying that:

.. math::
   B[t] < B[t + k*T_p], \forall k \in \mathbb{N} > 0

meaning that the amount of data in the buffer versus time is *not
periodic*, therefore the amount of data in the system's buffer
increases every period, i.e. the system has *unbounded buffer growth*.

If however, there is enough remaining capacity in the system to
service the data in the buffer, i.e. :math:`R[T_p] >= B[T_p]`, then
:math:`B[2*T_p] = B[T_p]`.  This relation means that if the remaining
capacity of the system that exists after all the period's required
traffic has been serviced is equal to or larger than the size of the
buffer at the end of the period, then in the next period the system
will be able to service fully both the data in the buffer and the
period's required traffic.  Since both the period's traffic and the
buffer's data will have been serviced in that period, the amount of
data in the buffer at the end of the period will be the same as the
amount of data that was in the buffer at the start of the
period. Similarly to above, since the system is deterministic, for any
two successive periods, :math:`n*T_p` and :math:`(n+1)*T_p`,
:math:`B[(n+1)*T_p] = B[n*T_p]`.  This extends to:

.. math::
   B[m*T_p] = B[n*T_p], \forall m,n > 0

which implies that:

.. math::
   B[t] = B[t + k*T_p], \forall k \in \mathbb{N} > 0

meaning that the amount of data in the buffer versus time is a
*periodic function*, therefore the buffer size does not grow between
periods, and the system has a *finite buffer*.

If we are only concerned with buffer growth, we do not need to
calculate :math:`R`, and can instead infer buffer growth by comparing
the values of the buffer at any two period-offset times during the
steady-state operation of the system (:math:`t >= T_p`).  This means
that the system buffer growth check can resolve to :math:`B[2*T_p] ==
B[T_p]`.  This comparison abides by the conditions above, with
:math:`m=2` and :math:`n=1`.

.. _nc_comparison:
      
Comparison with NC/RTC
======================

To show how our analysis techniques compare to other available
methods, we developed our tools to allow us to analyze the input
system using Network Calculus/Real-Time Calculus techniques as well as
our own.  Using these capabilities, we can directly compare the
analysis results to each other, and then finally compare both results
to the measurements from the actual system.

Taking the results from our published work, where our methods
predicted a buffer size of 64000 bits / 8000 bytes, we show that
Network Calculus predicts a required buffer size of 3155000 bits.

.. _fig-bandwidth:

.. figure:: /images/results/maren_namek_bw.png
   :align: center
   :height: 400px
   :width: 400px

   Bandwidth profile describing the system and application.

.. _fig-data-pnpp:

.. figure:: /images/results/maren_namek_data.png
   :align: center
   :height: 400px
   :width: 400px

   Analysis of the system with our tools.
	
.. _fig-data-nc:

.. figure:: /images/results/nc_namek_data.png
   :align: center
   :height: 400px
   :width: 400px

   Network-Calculus based analysis of the system.

:num:`Figure #fig-bandwidth` shows the bandwidth profile describing
the bandwidth versus time for the example system.  :num:`Figure
#fig-data-pnpp` shows the data versus time profile (time-integrated
from :num:`Figure #fig-bandwidth`) as analyzed by :math:`PNP^2`.
:num:`Figure #fig-data-nc` shows the same system analyzed using
Network Calculus.

The major drawback for Network Calculus that our work aims to solve is
the disconnect from the real system that stems from using an approach
based on time-window analysis.  Such an approach leads to dramatically
under-approximating the capacity of the network while simultaneously
over-approximating the utilization of the network, since a known drop
in network performance which is expected and handled by the
application cannot be accurately modeled.  In our case, the system is
using a system profile which can service data during the period from
:math:`0\le t\le 7` seconds with a period of 10 seconds.  The
application is designed around this constraint and only produces data
during that interval.  Because our technique directly compares when
the application produces data to when the system can service the data,
we are able to derive more precise performance prediction metrics than
Network Calculus, which compares the 3 seconds of system downtime to
the 3 seconds of maximum application data production.

We developed software which produces data according to a supplied
input profile and configured the system's network to provide the
bandwidth profile described in the system configuration profile.
Using this experimental infrastructure, we were able to measure the
transmitted traffic profile, the received traffic profile, the latency
experienced by the data, and the transmitter's buffer requirements.
The results are displayed in the table below:

+---------------------+--------------+-------------------------------+
|                     | Predicted    | Measured (:math:`\mu,\sigma`) |
+=====================+==============+===============================+
| Buffer Delay (s)    | 0.0625       | (0.06003 , 0.00029)           |
+---------------------+--------------+-------------------------------+
| Time of Delay (s)   | 3.0          | (2.90547 , 0.00025)           |
+---------------------+--------------+-------------------------------+
| Buffer Size (bytes) | 8000         | (7722.59 , 36.94)             |
+---------------------+--------------+-------------------------------+

.. _tdma_analysis:
	
Analysis of TDMA Scheduling
===========================

Medium channel access (MAC) protocols are used in networking systems
to govern the communication between computing nodes which share a
network communications medium.  They are designed to allow reliable
communication between the nodes, while maintaining certain goals, such
as minimizing network collisions, maximizing bandwidth, or maximizing
the number of nodes the network can handle.  Such protocols include
Time Division Multiple Access (TDMA), which tries to minimize the
number of packet collisions; Frequency Division Multiple Access
(FDMA), which tries to maximize the bandwidth available to each
transmitter; and Code Division Multiple Access (CDMA) which tries to
maximize the number of nodes that the network can handle.  We will not
discuss CDMA in the scope of this work.

In FDMA, each node of the network is assigned a different transmission
frequency from a prescribed frequency band allocated for system
communications.  Since each node transmits on its own frequency,
collisions between nodes transmitting simultaneously are reduced.
Communications paradigms of this type, i.e. shared medium with
collision-free simultaneous transmission between nodes, can be modeled
easily by our MAReN modeling paradigm described above, since the
network resource model for each node can be developed without taking
into account the transmissions of other nodes.

In TDMA, each node on the network is assigned one or more time-slots
per communications period in which only that node is allowed to
transmit.  By governing these timeslots and having each node agree
upon the slot allocation and communications period, the protocol
ensures that at a given time, only a single node will be transmitting
data, minimizing the number of collisions due to multiple simultaneous
transmitters.  In such a medium access protocol, transmissions of each
node affect other nodes' transmission capability.  Because these
transmissions are scheduled by TDMA, they can be explicitly integrated
into the system network resource model.

TDMA transmission scheduling has an impact on the timing
characteristics of the applications' network communications.  Because
applications' network data production is decoupled from their node's
TDMA transmission time slot, buffering may be required when an
application on one node tries to send data on the network during the
transmission slot of a different node.  In this case, the data would
need to be buffered on the application's node and would therefore
incur additional buffering delay.  If this TDMA schedule is not
integrated into the analysis of the network resources, the additional
buffer space required may exceed the buffer space allocation given to
the application or the buffering delay may exceed the application's
acceptable latency.

So far, the description of the system provided network service profile
(:math:`p[t]=y`), has been abstracted as simply the available
bandwidth as a function of time integrated to produce the amount of
data serviced as a function of time. We show how to model and analyze
the network's lower-level TDMA MAC protocol using our network modeling
semantics.  We then derive general formulas for determining the affect
TDMA has on buffer size and delay predictions.

As an example TDMA system which benefits from our analysis techniques,
consider an application platform provided by a fractionated satellite
cluster.  A fractionated satellite cluster consists of many small
satellites that may each have different hardware, computing, and
communications capabilities.  These capabilities are provided to
distributed components of the satellite cluster's applications.  Such
a system has the combined challenges of (1) being expensive to
develop, test, and deploy, (2) being very difficult to repair or
replace in the event of failure, and (3) having to support
mixed-criticality and possibly multiple levels of security
applications.  For this system, the network between these satellites
is a precious resource shared between each of the applications'
components in the cluster.  To ensure the stability of the network
resources, each satellite has a direct connection to every other
satellite and is assigned a slot in the TDMA schedule during which the
satellite may transmit.  Each TDMA slot has a sinusoidally
time-varying bandwidth profile which may differ from the other TDMA
slot bandwidth profiles.  The time-varying profile of the slot
bandwidth comes from the coupling between the radios' inverse-squared
bandwidth-as-a-function-of-distance and the satellites' sinusoidal
distance-as-a-function-of-orbital-position.

Such a system and applications necessitates design-time guarantees
about resource utilization and availability.  Applications which
utilize the satellite network need assurances that the network
resources they require during each part of the orbital period will be
satisfied.  To provide these assurances, we provide the application
developers and system integrators the ability to specify and analyze
the network profiles as (possibly periodic) functions of time.
Furthermore, the requirement for accurate predictions necessitates the
incorporation of the TDMA scheduling and bandwidth profiling into the
network modeling and analysis tools.

TDMA schedules can be described by their period, their number of
slots, and the bandwidth available to each slot as a function of time.
For simplicity of explanation, we assume that each node only gets a
single slot in the TDMA period and all slots have the same length, but
the results are valid for all static TDMA schedules.  Note that each
slot still has a bandwidth profile which varies as a function of time
and that each slots may have a different bandwidth profile.  In a
given TDMA period (:math:`T`), the node can transmit a certain number
of bits governed by its slot length (:math:`t_{slot}`) and the slot's
available bandwidth (:math:`bw_{slot}`).  During the rest of the TDMA
period, the node's available bandwidth is :math:`0`.  This scheduling
has the effect of amortizing the node's slot bandwidth into an
effective bandwidth of :math:`bw_{effective} = bw_{slot} *
\dfrac{t_{slot}}{T}`.  The addition of the TDMA scheduling can affect
the buffer and delay calculations, based on the slot's bandwidth, the
number of slots, and the slot length.  The maximum additional delay is
:math:`\Delta_{delay} = T - t_{slot}`, and the maximum additional
buffer space is :math:`\Delta_{buffer} = \Delta_{delay} *
bw_{effective}`.  These deviations are shown below.  Clearly,
:math:`\Delta_{delay}` is bounded by :math:`T` and
:math:`\Delta_{buffer}` is governed by :math:`t_{slot}`.  Therefore,
because :math:`t_{slot}` is dependent on :math:`T`, minimizing
:math:`T` minimizes both the maximum extra delay and maximum extra
buffer space.

+---------------------------------------------------+-----------------------------------------------------+
| In-Phase TDMA profile vs abstract                 | Out-of-Phase TDMA Profile vs abstract               |
+===================================================+=====================================================+
| .. image:: /images/results/tdma_phase0.png        | .. image:: /images/results/tdma_phase1.png          |
|    :height: 200                                   |    :height: 200                                     |
+---------------------------------------------------+-----------------------------------------------------+

Following from this analysis, we see that if: (1) the TDMA effective
bandwidth profile is provided as the abstract system network service
profile, and (2) the TDMA period is much smaller than the duration of
the shortest profile interval; then the system with explicit modeling
of the TDMA schedule has similar predicted application network
characteristics as the abstract system.  Additionally, the maximum
deviation formulas derived above provide a means for application
developers to analyze the their application on a TDMA system without
explicitly integrating the TDMA model into the system profile model.

.. _compositional_analysis:

Compositional Analysis
======================

Now that we have precise network performance analysis for aggregate
flows or singular flows on individual nodes of the network, we must
determine how best to compose these flows and nodes together to
analyze the overal system.  The aim of this work is to allow the flows
from each application to be analyzed separately from the other flows
in the network, so that application developers and system integrators
can derive meaningful perfomance predictions for specific
applications.  

We have implemented min-plus calculus based compositional operations
for the network profiles which allow us to compose and decompose
systems based on functional components.  For network flows, this means
we can analyze flows individually to determine per-flow performance
metrics or we can aggregate flows together to determine aggregate
performance.

The composition is priority based, with each flow receiving a unique
priority.  This priority determines the oder in which the flows are
individually analyzed, with the system's remaining capacity being
provided to the flow with the next highest priority.  This is similar
to the modular performance analysis provided by Real-Time Calculus.

The basis for this priority-based interaction is the QoS management
provided by many different types of networking infrastructure.
DiffServ's DSCP provides one mechanism to implement this
priority-based transmission and routing.

We are finalizing the design and code for tests which utilize the DSCP
bit(s) setting on packet flows to show that such priority-based
analysis techniques are correct for these types of systems.

.. _delay_analysis:

Delay Analysis
==============

When dealing with queueing systems (esp. networks) where precise
design-time guarantees are required, the delay in the links of the
network must be taken into account.

The delay is modeled as a continuous function of latency (seconds)
versus time.  In the profiles, the latency is specified discretely as
:math:`(time, latency)` pairs, and is interpolated linearly between
successive pairs.

Using these latency semantics, the delay convolution of a profile
becomes

.. math::
   r[t + \delta[t]] = l[t]

Where

* :math:`l[t]` is the *link* profile describing the data as a function
  of time as it enters the link
* :math:`\delta[t]` is the *delay* profile describing the latency as a
  function of time on the link
* :math:`r[t]` is the *received* profile describing the data as a
  function of time as it is received at the end of the link

When analyzing delay in a periodic system, it is important to
determine the effects of delay on the system's periodicity.  We know
that the period of the periodic profiles is defined by the time
difference between the start of the profile and the end of the
profile.  Therefore, we can show that if the time difference between
the **start time** of the *received* profile and the **end time** of
the *received* profile is the same as the **period** of the *link*
profile, the periodicity of the profile is unchanged.

* :math:`T_p` is the period of the *link* profile
* :math:`r[t + \delta[t]]` is the beginning of the *received* profile
* :math:`r[(t + T_p) + \delta[(t + T_p)]]` is the end of the
  *received* profile
    

We determine the condition for which :math:`(t_{end}) - (t_{start}) =
T_p`:

.. math::
   (T_p + t + \delta[T_p + t]) - (t + \delta[t]) &= T_p \\
   T_p + \delta[T_p + t] - \delta[t] &= T_p \\
   \delta[T_p + t] - \delta[t] &= 0\\
   \delta[T_p + t] &= \delta[t]

Which is just confirms that the periodicity of the delayed profile is
unchanged *iff* the latency profile is **periodic**, i.e.

.. math:: \delta[t] = \delta[t + k*T_p], \forall k\in\mathbb{N} > 0

.. _routing_analysis:

Routing Analysis
================

By incorporating both the latency analysis with the compositional
operations we developed, we can perform system-level analysis of flows
which are routed by nodes of the system.  In this paradigm, nodes can
transmit/receive their own data, i.e. they can host applications which
act as data sources or sinks, as well as act as routers for flows from
and to other nodes.  To make such a system amenable to analysis we
must ensure that we know the routes the flows will take at design
time, i.e. the routes in the network are static and known or
calculable.  Furthermore, we must, for the sake of flow composition as
decribed above, ensure that each flow has a priority that is unique
within the network which governs how the transmitting and routing
nodes handle the flow's data.

We have extended our network analysis tool to support such system
analysis by taking as input:

* the sender flows and receiver functions in the network
* the provided service of each node in the network
* the network configuration specifying the nodes in the network and
  the routes in the network

where a flow is defined by:

* Node ID of the profile
* Kind of the flow
* Period of the flow
* Flow type of the profile 
* Priority of the flow
* flow properties vs time profile

and a route is specified as a list of node IDs starting with the
source node ID and ending with the destination node ID.  Any flows
which have the respective source and destination IDs must travel along
the path specified by the respective route.

We can then run the following algorithm to iteratively analyze the
flows and the system

.. code-block:: C#

  analyze( profiles )
  {
    profiles = sorted(profiles, priority)
    for required in profiles
    {
      transmitted_nodes = []
      for receiver in required.receivers()
      {
        route = required.route()
	for node in route
	{
	  if node in transmitted_nodes and multicast == true
	  {
	    continue
	  }
	  provided = node.provided
	  [output, remaining, received] = convolve(required, provided)
	  node.provided = remaining
	  required = received
	  transmitted_nodes.append(node)
	}
	[recv_output, recv_remaining, ] = convolve(required, receiver)
      }
    }
  }


.. .. figure:: /images/results/algorithm.png
..	    :height: 600px
..	    :width: 600px

In this algorithm, the remaining capacity of the node is provided to
each profile with a lower priority iteratively.  Because of this
iterative recalculation of node provided profiles based on routed
profiles, we directly take into account the effect of multiple
independent flows traversing the same router; the highest priority
flow receives as much bandwidth as the router can give it, the next
highest priority flow receives the remaining bandwidth, and so on.

We take care of matching all senders to their respective receivers,
and ensure that if the system supports multicast, a no retransmissions
occur; only nodes which must route the flow to a new part of the
network retransmit the data.  However, if the system does not support
multicast, then the sender must issue a separate transmission, further
consuming network resources.  In this way, lower-level transport
capabilities can be at least partially accounted for by our analysis.

We have implmented these functions for statically routed network
analysis into our tool, which automatically parses the flow profiles,
the network configuration and uses the algorithm and the implemented
mathematics to iteratively analyze the network.  Analytical results
for example systems will be provided when the experimental results can
be used as a comparison.

We are finishing the design and development of code which will allow
us to run experiments to validate our routing analysis results.  They
will be complete in the next two weeks.

