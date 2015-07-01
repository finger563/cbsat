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

namespace NetworkMiddleware {

  static NetworkBuffer buffer;
  NetworkProfile profile;
  timespec nextSendTime;

  static pthread_t threadSend;
  static bool threadSendDie;
  static pthread_cond_t threadSendCV;
  static pthread_mutex_t threadSendMutex;

  static pthread_t threadRecv;
  static bool threadRecvDie;
  static pthread_cond_t threadRecvCV;
  static pthread_mutex_t threadRecvMutex;

  static uint64_t new_conn_id = 1;
  static std::map<uint64_t,IPV6_Connection*> data_conns;
  static std::map<uint64_t,IPV6_Connection*> oob_conns;
  
  void *dataRecvThread(void * arg){
  }

  void *dataSendThread(void * arg){
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
	int retVal =
	  data_conns[data->connection_id]->send(data->Buffer().c_str(),
						data->Bytes());
	if ( retVal <= 0 )
	  TG_LOG("Couldn't send message %lu on connection %lu\n",
		 data->Id(),
		 data->connection_id);
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

  int Init()
  {
    // CREATE OOB RECV THREAD HERE
    // CREATE DATA RECV THREAD HERE
    // CREATE DATA SEND THREAD HERE ( ONE BUFFER OR WHAT?)
  }

  int InitClient( NetworkProfile p,
		  std::string serverIP,
		  int serverPort,
		  long capacity = 0 ) {
    uint64_t conn_id = new_conn_id++;
    data_conns[conn_id] = new IPV6_Connection();
    data_conns[conn_id]->serverIP = serverIP;
    data_conns[conn_id]->serverPort = serverPort;
    if ( data_conns[conn_id]->Initialize(false,false) != 0 )
      {
	TG_LOG("ERROR:: could't initialize data interface to %s : %d",
	       data_conns[conn_id]->serverIP.c_str(),
	       data_conns[conn_id]->serverPort);
	return -1;
      }

    oob_conns[conn_id] = new IPV6_Connection();
    oob_conns[conn_id]->serverIP = serverIP;
    oob_conns[conn_id]->serverPort = serverPort+1;
    if ( oob_conns[conn_id]->Initialize(false,false) != 0 )
      {
	TG_LOG("ERROR:: could't initialize oob interface to %s : %d",
	       data_conns[conn_id]->serverIP.c_str(),
	       data_conns[conn_id]->serverPort);
	return -1;
      }

    nextSendTime.tv_sec = 0;
    nextSendTime.tv_nsec = 0;
    buffer.Capacity(capacity);
    profile = p;
    if (!profile.Initialized()) {
      TG_LOG("WARNING: couldn't initialize buffer profile!\n");
      TG_LOG("\tActing as a pass-through buffer!\n");
      new_conn_id--;
      data_conns.erase(new_conn_id);
      return 0;
    }
    else {
      threadSendDie = false;
      pthread_mutex_init (&threadSendMutex, NULL);
      pthread_cond_init (&threadSendCV, NULL);
      pthread_create(&threadSend, NULL, NetworkMiddleware::dataSendThread, (void *)NULL);
      TG_LOG("Created client MW thread %lu\n",
	     threadSend);
      return conn_id;
    }
  }

  int InitServer( NetworkProfile p, long capacity = 0 ) {
    buffer.Capacity(capacity);
    profile = p;
    if (!profile.Initialized()) {
      TG_LOG("WARNING: couldn't initialize buffer profile!\n");
      TG_LOG("\tActing as a pass-through buffer!\n");
    }
    else {
      threadRecvDie = false;
      pthread_mutex_init (&threadRecvMutex, NULL);
      pthread_cond_init (&threadRecvCV, NULL);
      pthread_create(&threadRecv, NULL, NetworkMiddleware::dataRecvThread, (void *)NULL);
      TG_LOG("Created server MW thread %lu\n",
	     threadRecv);
    }
    return 0;
  }

  int Exit() {
    if ( profile.Initialized() == true ) {
      threadSendDie = true;
      threadRecvDie = true;
      int retVal;

      TG_LOG("Joining thread %lu\n",
	     threadSend);
      pthread_join(threadSend,(void **)&retVal);
      TG_LOG("exited join thread!\n");
      pthread_mutex_destroy(&threadSendMutex);
      pthread_cond_destroy(&threadSendCV);

      TG_LOG("Joining thread %lu\n",
	     threadRecv);
      pthread_join(threadRecv,(void **)&retVal);
      TG_LOG("exited join thread!\n");
      pthread_mutex_destroy(&threadRecvMutex);
      pthread_cond_destroy(&threadRecvCV);

      std::map<uint64_t,IPV6_Connection*>::iterator it;
      for (it=data_conns.begin();it!=data_conns.end();it++)
	{
	  if (it->second != NULL) {
	    it->second->Close();
	    delete it->second;
	  }
	}
      for (it=oob_conns.begin();it!=oob_conns.end();it++)
	{
	  if (it->second != NULL) {
	    it->second->Close();
	    delete it->second;
	  }
	}
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
      int retVal =
	data_conns[data->connection_id]->send(data->Buffer().c_str(),
					      data->Bytes());
      if ( retVal <= 0 )
	TG_LOG("Couldn't send message %lu on connection %lu\n",
	       data->Id(),
	       data->connection_id);
    }
    return retVal;
  }
}

#endif
