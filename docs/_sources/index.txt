Precise Network Performance Prediction
======================================

.. CBSAT contains the relevant code for design-time network performance
   analysis and run-time network traffic generation, measurement,
   detection, and management.  It has been incorporated for both
   design-time analysis of models and run-time management of networked
   applications into `ROSMOD <http://github.com/rosmod/rosmod-pkg.git>`_.

   The documentation has been broken down into varoius sections by
   relevance.  The starting point is the :ref:`getting-started` page
   which provides an overview of the parts of the project, and should
   point you to the specific section relevant to your interests.

This documentation covers the background, theory, and results for my
research, *Precise Network Performance Prediction*, (:math:`PNP^2`),
the aim of which is to provide design-time analysis of distributed
cyber-physical systems' (CPS) and their applications' network
performance.  The type of network performance we will focus on
predicting is the application buffer size requirements and the
application network traffic buffering delay.  These factors were
chosen because they relate directly to how well the application
traffic is serviced by the system and they directly affect resource
utilization of the application on the system.

Because the buffering resources available to applications may be fixed
by the system, application developers need to know at design time
whether or not the application's data production versus data
consumption will overflow the application's allotted buffer space.  By
analyzing these systems, developers can assess these conditions at
design-time and try to mitigate any predicted overflows before
deploying the applications. 

Furthermore, buffering delay/latency is an important metric for
determining application network performance because in many of these
CPS, interactions and computation have deadlines that must be met, for
instance in an attitude control system where the physical dynamics of
the system determine the required reaction time of the software from
sensing to calculation to actuation.  Developers need guarantees that
such reaction times can be met, and for distributed systems, the
buffering latency and transmission latency for network data affects
these reaction times.  

Such design-time performance analysis and feedback is critical to the
development of robust safety- or mission-critical applications.

.. toctree::
   :includehidden:
   :maxdepth: 2

   background
   math
   results


.. getting-started
   theory-results
   users
   developers

:ref:`genindex`
