.. _getting-started:

Getting Started
===============

.. _network-performance-analysis:
Network Performance Analysis 
----------------------------

This work is based off of Network Calculus,
and aims to provide more precise modeling and
performance prediction for networked, distributed
applications.

Background
^^^^^^^^^^
Network Calculus models application network data production
and system network data service *curves*.  These curves
describe how the data is produced or serviced as a function
of *time-window size*.  

The Analysis Tool
-----------------

The analysis tool is a python library which implements both
the Network Calculus and MAReN techniques described
:ref:`above<network-performance-analysis>`.

Installation
^^^^^^^^^^^^

1. Download the analysis tool from the CBSAT repo:

 * `Github <https://github.com/finger563/cbsat/releases>`_


The Middleware
--------------

.. note:: The middleware is C++ and supports Linux.

Compilation
^^^^^^^^^^^

1. To Build the client and server test of the middleware, run from a terminal:
   ``make``


Congratulations!  The set-up of the analysis tool and the middleware
are complete!   
