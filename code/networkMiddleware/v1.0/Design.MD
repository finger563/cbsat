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
* How do we get middlewares to know about each other?
* How do we spawn socket connections to new middlewares?
* Do we match a profile to each flow (connection)?
* Or do we match a profile to a process (multiple flows)?
* What do we do about server (receiver)?

* Need to move the interface code into the middleware:
  * Remove explicit connection handling from application code
  * provide simple interface for passing data / amount of data
  * provide simple interface for receiving data / amount of data
  

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
