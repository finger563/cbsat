.. _run_time:

Run Time Results
================

Middleware-integrated Measurement, Detection, and Enforcement
-------------------------------------------------------------

We have implemented these features based on our design-time results:

* Traffic generators according to profile generated into sender code
* Receiver service according to profile generated into receiver code
* Measurement of output traffic on sender side and input traffic on
  server side generated into code
* Detection of anomalous sending on sender side
* Mitigation of anoumalous sending on sender side
* Detection of anomalous sending on receiver side
* Push back to sender middleware through out-of-band channel for
  anomaly detection on server side

We have implemented our 

We shown experimentally that, for example, a server side buffer size
of 400000 bits, which would normally grow to 459424 bits because of
excessive data pumps on the sender side, is kept to 393792 by
utilizing this out-of-band channel and secure middleware.
    
