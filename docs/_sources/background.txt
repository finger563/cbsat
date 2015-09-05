Background: Network Performance Analysis
========================================

Networking systems have been developed for over half a century and the
analysis of processing networks and communications networks began even
earlier.  As computing power has increased, the field of network
performance analysis at design-time has evolved into two main
paradigms: (1) network performance testing of the applications and
system to be deployed to determine performance and pitfalls, and (2)
analytical models and techniques to provide application network
performance guarantees based on those models.  The first paradigm
generally involves either arbitrarily precise network simulation, or
network emulation, or sub-scale experiments on the actual system.  The
second paradigm focuses on formal models and methods for composing and
analyzing those models to derive performance predictions.

We focus on the second paradigm, using models for predicting network
performance at design-time.  This focus comes mainly from the types of
systems to which we wish to apply our analysis: safety- or
mission-critical distributed cyber-physical systems, such as
satellites, or autonomous vehicles.  For such systems, resources come
at a premium and design-time analysis must provide strict guarantees
about run-time performance and safety before the system is ever
deployed.  

For such systems, probabilistic approaches do not provide high enough
confidence on performance predictions since they are based on
statistical models.  Therefore, we must use deterministic analysis
techniques to analyze these systems.  

.. _network_calc:

Network Calculus
----------------

Network Calculus provides a modeling and analysis paradigm for
deterministically analyzing networking and queueing systems.  Its
roots come from the desire to analyze network and queuing systems
using similar techniques as traditiional electrical circuit systems,
i.e. by analyzing the *convolution* of an *input* function with a
*system* function to produce an *output* function.  Instead of the
convolution mathematics from traditional systems theory, Network
Calculus is based on the concepts of *(min,+)-calculus*, which we will
not cover here for clarity, but for which an explanation can be found
in my proposal and thesis.

By using the concepts of *(min,+)-calculus*, Network Calculus provides
a way to model the application network requirements and system network
capacity as functions, not of time, but of *time-window size*.  Such
application network requirements become a cumulative curve defined as
the *maximum arrival curve*.  This curve represents the cumulative
amount of data that can be transmitted as a function of time-window
size.  Similarly, the system network capacity becomes a cumulative
curve defined as the *minimum service curve*. These curves bound the
application requirements and system service capacity.

.. figure:: images/background/nc_arrival_curve.png
   :align: center
   :width: 400px

   Network Calculus arrival curve (:math:`\alpha`)

.. figure:: images/background/nc_service_curve.png
   :align: center
   :width: 400px

   Network Calculus service curve (:math:`\beta`)

Network calculus uses *(min,+)-calculus convolution* to compose the
application requirement curve with the system service curve.  The
output of this convolution is the maximum data arrival curve for the
output flow from the node providing the service.  By analyzing these
curves, bounds on the application's required buffer size and buffering
delay can be determined.

.. figure:: images/background/nc_bounds.png
   :align: center
   :width: 400px

   Schematic deptiction of the buffer size (vertical difference) and
   delay (horizontal difference) calculations in Network Calculus.

With these bounds and the convolution, developers can make
*worst-case* performance predictions of the applications on the
network.  These bounds are *worst-case* because the curves are
functions of *time-window size*, instead of directly being functions
of time.  This distinction means that the worst service period
provided by the system is directly compared with the maximum data
production period of the application.  Clearly such a comparison can
lead to over-estimating the buffer requirements if the application's
maximum data production does not occur during that period.  

.. _rtc:

Real Time Calculus
------------------

Real-Time Calculus is based on Network Calculus and extends their work
to allow for compositional system analysis.
