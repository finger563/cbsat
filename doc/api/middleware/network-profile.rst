Network Profile
===============

.. cpp:class:: profileMemBuf

   This structuture creates a stream buffer for parsing csv profile files.

.. cpp:class:: ResourceEntry

   .. attribute:: time
   
      Contains the start time for the resource entry.
   
      :rtype: float

   .. attribute:: bandwidth

      The bandwidth (bps) which is constant from the start of the entry to its end.
   
      :rtype: unsigned long long
			  
   .. attribute:: data

      The cumulative data (bits) which have been sent by the end of this resource entry. Includes all summation of all previous entries' data.
   
      :rtype: unsigned long long
			  
   .. attribute:: latency

      The latency (ms) for network traffic during this entry.
   
      :rtype: unsigned long long
			  
.. cpp:class:: NetworkProfile

   A network profile contains a sorted list of time- and data-contiguous entries of type :cpp:class:`ResourceEntry`.  The profiles are periodic with a specific epoch-centric start-time.

   .. attribute:: resources

      :rtype: std\:\:vector<:class:`ResourceEntry`>

   .. attribute:: start_time

      :rtype: timespec

   .. attribute:: period

      :rtype: double

   .. method:: initializeFromFile (fname)

      Load in the profile specified by *fname*.  Return 0 on success, -1 on error.

      :param const char* fname: The filename containing a csv-delimited profile
      :rtype: int

   .. method:: initializeFromString (buffer)

      Load in the profile contained in *buffer*.  Return 0 on success, -1 on error.

      :param char* buffer: A string buffer containing the csv-delimited profile
      :rtype: int

   .. method:: initializeFromIStream (stream)

      Load in the profile contained in *stream*.  Return 0 on success, -1 on error.

      :param std\:\:istream& stream: An istream containing the csv-delimited profile
      :rtype: int

   .. method:: getOffset (t)

      Returns the difference between *t* and the profile's start time, modulo the profile's period.

      :param out timespec& t: epoch-centric time value
      :rtype: double

   .. method:: getNextInterval (start, bandwidth, latency)

      Returns as output parameters the next interval by comparing the current system epoch time to the profile's start epoch time.  IF the profile has not been properly initialized, the call fails and returns -1, else it fills the output parameters and returns 0.

      :param out timespec& start: epoch time when the next interval starts
      :param out unsigned long long& bandwidth: bandwidth during the next interval
      :param out unsigned long long& latency: latency value for the next interval
      :rtype: int

   .. method:: Delay (dataLen, sentTime)

      Returns the amount of time the program has to wait before sending again.  This is calculated based using the input *dataLengh* that was last transmitted at *sentTime*, and takes into account the current system itme.  

      :param in unsigned long dataLen: size of the message that was last sent
      :param in timespec sentTime: epoch time the message of length dataLen was sent
      :rtype: double

   .. method:: Initialized ( )

      Returns true if the profile was properly initialized, false otherwise.
   
      :rtype: bool
