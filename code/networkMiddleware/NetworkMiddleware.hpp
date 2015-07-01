#ifndef NETWORK_MIDDLEWARE_HPP
#define NETWORK_MIDDLEWARE_HPP

#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <time.h>

#include <pthread.h>

#include <vector>
#include <string>

#include <map>

#include "log_macro.hpp"
#include "NetworkBuffer.hpp"
#include "NetworkProfile.hpp"
#include "NetworkMiddleware.hpp"

typedef void* (*sendFunc_t)(Message* data);
typedef void* (*recvFunc_t)(Message* data);

namespace NetworkMiddleware {

  static NetworkBuffer buffer;
  NetworkProfile profile;
  timespec nextSendTime;

  static pthread_t threadSend;
  static bool threadSendDie;
  static pthread_cond_t threadSendCV;
  static pthread_mutex_t threadSendMutex;
  sendFunc_t sendFunctionPtr;

  static pthread_t threadRecv;
  static bool threadRecvDie;
  static pthread_cond_t threadRecvCV;
  static pthread_mutex_t threadRecvMutex;
  recvFunc_t recvFunctionPtr;

  std::map<uint64_t,IPV6_Connection*> data_conns;
  std::map<uint64_t,IPV6_Connection*> oob_conns;
  
  void *threadRecvFunction(void * arg){
  }

  void *threadSendFunction(void * arg){
    Message* data;
    bool sendData = false;
    double timeDiff = 0;
    timespec currentTime, condTimeout, sleepTime, remainingTime;
    sleepTime.tv_sec = 0;
    sleepTime.tv_nsec = 0;

    while (!threadSendDie) {
      if ( timeDiff > 0 ) {
        nanosleep(&sleepTime,&remainingTime);
	timeDiff = 0;
      }
      clock_gettime(CLOCK_REALTIME,&currentTime);
      condTimeout = currentTime;
      condTimeout.tv_sec += 1;
      pthread_mutex_lock(&threadSendMutex);
      if ( buffer.Size() == 0 ) {
        pthread_cond_timedwait(&threadSendCV,&threadSendMutex,&condTimeout);	
      }
      if ( buffer.Pop(data) == 0 ) {
        sendData = true;
      }
      pthread_mutex_unlock(&threadSendMutex);
      if ( sendData && data != NULL ) {
	data->TimeStamp();
        (*sendFunctionPtr)(data);
        timeDiff = profile.Delay(data->Bits(),data->LastEpochTime());
	double fractpart,intpart;
	fractpart = modf(timeDiff,&intpart);
        sleepTime.tv_sec = (unsigned long long)(intpart);
        sleepTime.tv_nsec = (unsigned long)(fractpart*1000000000.0);
        sendData = false;
      }
    }
    TG_LOG("Buffer send thread exiting!\n");
    pthread_exit(NULL);
  }

  int Init( NetworkProfile p, sendFunc_t func ,long capacity = 0 ) {
    if ( func == NULL ) {
      TG_LOG("ERROR: Send func is NULL!\n");
      return -1;
    }
    sendFunctionPtr = func;
    nextSendTime.tv_sec = 0;
    nextSendTime.tv_nsec = 0;
    buffer.Capacity(capacity);
    profile = p;
    if (!profile.Initialized()) {
      TG_LOG("WARNING: couldn't initialize buffer profile!\n");
      TG_LOG("\tActing as a pass-through buffer!\n");
    }
    else {
      threadSendDie = false;
      pthread_mutex_init (&threadSendMutex, NULL);
      pthread_cond_init (&threadSendCV, NULL);
      pthread_create(&threadSend, NULL, NetworkMiddleware::threadSendFunction, (void *)NULL);
      TG_LOG("Created thread %lu\n",
	     threadSend);
    }
    return 0;
  }

  int Exit() {
    if ( profile.Initialized() == true ) {
      threadSendDie = true;
      int retVal;
      TG_LOG("Joining thread %lu\n",
	     threadSend);
      pthread_join(threadSend,(void **)&retVal);
      TG_LOG("exited join thread!\n");
      pthread_mutex_destroy(&threadSendMutex);
      pthread_cond_destroy(&threadSendCV);
    }
  }

  int send(Message* data) {
    if ( data == NULL )
      return -1;
    int retVal = -1;
    if ( profile.Initialized() == true ) {
      //timespec currentTime;
      double timeDiff = 0;

      pthread_mutex_lock(&threadSendMutex);
      if ( buffer.Size() == 0 )
	pthread_cond_signal(&threadSendCV);
      retVal = buffer.Push(data);
      pthread_mutex_unlock(&threadSendMutex);
    
      timeDiff = profile.Delay(data->Bits(),data->FirstEpochTime());
      double fractpart,intpart;
      fractpart = modf(timeDiff,&intpart);
      clock_gettime(CLOCK_REALTIME,&nextSendTime);
      nextSendTime.tv_sec += (unsigned long long)(intpart);
      nextSendTime.tv_nsec += (unsigned long)(fractpart*1000000000.0);
      if ( nextSendTime.tv_nsec > 999999999 ) {
	nextSendTime.tv_sec += 1;
	nextSendTime.tv_nsec = nextSendTime.tv_nsec - 1000000000;
      }
    }
    else {
      (*sendFunctionPtr)(data);      
    }
    return retVal;
  }
}

#endif
