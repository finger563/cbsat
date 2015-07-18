#ifndef NETWORK_BUFFER_HPP
#define NETWORK_BUFFER_HPP

#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <time.h>

#include <pthread.h>

#include <algorithm>    // std::swap
#include <memory>
#include <vector>
#include <queue>
#include <string>
#include <iomanip>
#include <streambuf>
#include <fstream>

#include "Message.hpp"

class NetworkBuffer {
private:
  std::queue<Message*> buffer;
  long size;
  long capacity;
  long maxSize;
public:
  NetworkBuffer( long _capacity = 0 ) {
    capacity = _capacity;
    size = 0;
    maxSize = 0;
  }

  ~NetworkBuffer(){ }

  NetworkBuffer (const NetworkBuffer &s)
  : size(s.size),
  capacity(s.capacity),
  maxSize(s.maxSize),
  buffer(s.buffer)
  {
  }

  NetworkBuffer & operator= (const NetworkBuffer &s)
  {
    if (&s != this)
    {
      NetworkBuffer tmp (s);
      swap (tmp);
    }
    return  *this;
  }

  NetworkBuffer* clone() const {
    return new NetworkBuffer( *this );
  }

  void swap (NetworkBuffer &s) {
    std::swap (size, s.size);
    std::swap (capacity, s.capacity);
    std::swap (maxSize, s.maxSize);
    std::swap (buffer, s.buffer);
  }

  long MaxSize() const {
    return maxSize;
  }

  long Size() const {
    return size;
  }

  long Capacity() const {
    return capacity;
  }
  void Capacity(long _capacity) {
    capacity = _capacity;
  }

  int Push(Message* data) {
    if ( data == NULL )
      return -1;
    int retVal = -1;
    if ( capacity == 0 || data->Bits() <= (capacity-size) ) {
      size += data->Bits();
      if (size > maxSize && buffer.size() > 1)
        maxSize = size;
      buffer.push(data);
      retVal = 0;
    }
    return retVal;
  }

  int Pop(Message *&data) {
    int retVal = -1;
    if ( size > 0 && buffer.size() > 0) {
      data = buffer.front();
      buffer.pop();
      size = size - data->Bits();
      retVal = 0;
    }
    return retVal;
  }
};

#endif
