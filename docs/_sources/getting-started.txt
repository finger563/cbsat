.. _getting-started:

Getting Started
===============

.. note::
   This page and many of the others that are part of this
   documentation use terminology such as *profiles*, *convolution*,
   *network analysis*, etc.  These terms are used without explanation in
   many places to simplify much of the documentation.  Readers are
   encouraged to read through all of :ref:`theory` for a complete
   understanding of these terms as well as the rest of the theory and
   background which acts as the foundation for all of this work.

This repository code and its documentation covers a novel technique
for analyzing and predicting network performance of distributed
applications, called **Precise Performance Prediction for Networks**
(**P3N**), which has been implemented into a design-time analysis tool
that analyzes application and system models. Furthermore, a run-time
library has been developed which enables application code to generate
network traffic that adheres to a specified network profile.  Metrics
about this traffic are automatically recorded for offline analysis.
Furthermore the library enables management of such networked
applications by forcing them to adhere to their profiles; in this way
it acts as a lightweight layer on top of the communications middleware
layer used by the applications on the system.  Finally, anomalous
traffic can be detected by receivers and disabled through out-of-band
(OOB) communication to the sender-side middleware.

* :ref:`theory` : for readers interested in learning the theory behind
  this analysis and implementation; covers all of the relevant
  background, theory, and results pertaining to **P3N**.
* :ref:`users` : for readers interested in using **P3N**; provides an
  explanation the interfaces provided by the tools and walks through
  some examples to demonstrate how they can be used.
* :ref:`developers` : for readers interested in extending this work or
  learning more about the complete implementation of the theory;
  provides a launching point which directs them to the APIs that have
  been developed for interfacing between the code's modules.
