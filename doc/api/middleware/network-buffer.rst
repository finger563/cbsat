Network Buffer
==============

.. cpp:class:: NetworkBuffer

   A network profile contains a sorted list of time- and data-contiguous entries of type :cpp:class:`ResourceEntry`.  The profiles are periodic with a specific epoch-centric start-time.

   .. method:: MaxSize ( )

      Return the maximum size that the buffer has reached.

      :rtype: long

   .. method:: Size ( )

      Return the current size of the buffer.

      :rtype: long

   .. method:: Capacity ( )

      Return the capacity of the buffer.

      :rtype: long

   .. method:: Capacity ( _capacity )

      Set the capacity of the buffer.

      :param in long _capacity: new capacity for the buffer
      :rtype: void

   .. method:: Push ( data )

      Add data to the buffer if :math:`data.size < (capacity - size)`.  Return 0 on success, -1 on failure.

      :param in Message* data: message to be added to the buffer
      :rtype: int

   .. method:: Pop (data)

      Returns 0 for successful data retrieval from the buffer, -1 otherwise.

      :param in-out Message*& data: Message pointer to data retrieved
      :rtype: int

