Enhancements:
-------------
* Middleware:
  * Server side receive middleware
  * Enable out-of-band communication between servers & clients
    * Communication of profiles?
    * Allow receiver to stop sender
* Sever Functionality:
  * reads all profiles for all clients connected
  * checks all incoming client data against the client's profile
  * sends STOP command to client if client has been deemed a threat

Questions:
----------
* What do we do about server (receiver)?
* How to create process specific buffers?
	* Singleton instance used by each process
	* each process has single buffer?
* how to properly meter out data from the buffer
	* break up packets?

Goals:
------
* enforce application (process) network traffic profiles
* measure each packet's latency 
* measure each buffer's size as a function of time
* enforce system network traffic profile (tc?)
* vanilla linux: i.e. UDP

Architecture:
-------------
* underlying send layer uses UDP
* applications call a MW level send call 
	* send call places data into a buffer
	* buffer management:
		* (possibly) rejects insertion
		* (possibly) delays transmission
		* tracks stats

Need to Create:
---------------
* Client traffic generation (port)
* Server reception/measurement (port)
* Client side architecture:
	* process-specific buffers and management code
	* connection setup/teardown

Client Middleware:
------------------
* Read in standard Network Profile (port)
* configure buffer space (packet based?)
* create egress thread
* When application invokes send():
	* check time for input rejection
	* get buffer lock()
	* check buffer space for input rejection
	* insert into buffer (single packet?)
	* if !(buffer_has_data): send cond var to egress thread
	* release buffer lock()
* egress thread:
	* if (buffer_has_data)
		* get buffer lock
		* pop data off the buffer (profile based)
		* release buffer lock
		* calc next pop time
		* wait until pop time
	* else
		* wait for cond var from input thread