#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#include <string.h>

#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <time.h>
#include <math.h>
#include <algorithm>    // std::swap
#include <memory>
#include <vector>
#include <iomanip>
#include <streambuf>
#include <fstream>

namespace Network {
  static double EpochToDouble(timespec t) {
    double retTime = 
      (double)t.tv_sec + 
      ((double)t.tv_nsec)/(double)1000000000.0;
    return retTime;
  }

  class Message {
  public:  
    std::string buffer;
    uint64_t bits;
    uint64_t id;
    uint64_t connection_id;
    std::vector<timespec> times;
    Message ()
      : bits(0),
	id(0),
	connection_id(0)
    {
    }

    Message ( uint64_t len, uint64_t i, uint64_t conn_id=0 )
      : bits (len),
	id(i),
	connection_id(conn_id)
    {
      buffer = std::string(this->Bytes()+2,'A');
      uint64_t templen = 256;
      char temp[templen];
      memset(temp,0,templen);
      sprintf(temp,"%lu",id);
      templen = strlen(temp);
      if (templen <= this->Bytes())
	std::copy(temp,temp+templen, buffer.begin());
      else
	std::copy(temp,temp+this->Bytes(),buffer.begin());
    }

    Message (const Message &s)
      : bits(s.bits),
	id(s.id),
	buffer(s.buffer),
	times (s.times)
    {
    }

    Message & operator= (const Message &s)
    {    
      if (&s != this)
	{
	  Message tmp (s);
	  swap (tmp);
	}
      return  *this;
    }

    void swap (Message &s)
    {
      std::swap (bits, s.bits);
      std::swap (id, s.id);
      std::swap (buffer, s.buffer);
      std::swap (times, s.times);
    }

    void TimeStamp() { 
      timespec time;
      clock_gettime(CLOCK_REALTIME, &time);
      times.push_back(time);
    }

    std::string Buffer() const {
      return buffer;
    }

    int NumTimes() const { return times.size(); }

    std::vector<double> DoubleTimes() const {
      std::vector<double> retTimes;
      double time = 0;
      for (int i=0;i<times.size();i++) {
	time = Network::EpochToDouble(times[i]);
	retTimes.push_back( time );
      }
      return retTimes;
    }

    double FirstDoubleTime() const {
      return Network::EpochToDouble(times.front());
    }

    double LastDoubleTime() const {
      return Network::EpochToDouble(times.back());
    }

    std::vector<timespec> EpochTimes() const {
      std::vector<timespec> retTimes(times);
      return retTimes;
    }

    timespec FirstEpochTime() const {
      timespec retTime = times.front();
      return retTime;
    }

    timespec LastEpochTime() const {
      timespec retTime = times.back();
      return retTime;
    }

    void Clear() { buffer.clear(); }

    uint64_t Id() const { return id; }
    void Id(uint64_t i) { id = i; }

    uint64_t Bits() const { return bits; }
    void Bits(uint64_t b) { bits = b; }

    uint64_t Bytes() const { return ceil((double)bits/8.0f); }
    void Bytes(uint64_t B) { bits = B*8; }

    std::string ToString() const {
      std::string retStr;
      retStr += std::to_string(Id()) + ",";
      for (int i=0; i < times.size(); i++) {
	std::string s = "000000000";
	std::string n = std::to_string(times[i].tv_nsec);
	n.length() <= 9 ? s.replace(9 - n.length(), n.length(), n) : s = n;
	retStr += std::to_string(times[i].tv_sec) + "." + s + ",";
      }
      retStr += std::to_string(Bits());
      return retStr;
    }
  };
};

#endif
