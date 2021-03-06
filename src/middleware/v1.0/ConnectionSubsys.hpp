#ifndef CONNECTION_SUBSYS_HPP
#define CONNECTION_SUBSYS_HPP

#include <sys/ioctl.h>
#include <linux/sockios.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <ifaddrs.h>

#include <cstring>
#include <algorithm>
#include <memory>
#include <string>

#include "log_macro.hpp"

class Connection {
public:
  bool isServer;
  bool hasReturnPath;
  std::string serverIP;
  int bufferSize;
  int serverPort;
  int receiveTimeout;
  
  Connection (bool returnPath)
    : hasReturnPath (returnPath),
      bufferSize (0),
      receiveTimeout (1)
  {
  }

  Connection (const Connection &s)
    : hasReturnPath (s.hasReturnPath),
      isServer (s.isServer),
      bufferSize (s.bufferSize),
      serverIP (s.serverIP),
      serverPort (s.serverPort),
      receiveTimeout (s.receiveTimeout)
  {
  }

  Connection & operator= (const Connection &s) 
  {
    if (&s != this)
      {
	Connection tmp(s);
	swap (tmp);
      }
    return *this;
  }

  virtual void swap (Connection &s) 
  {
    std::swap (isServer, s.isServer);
    std::swap (hasReturnPath, s.hasReturnPath);
    std::swap (bufferSize, s.bufferSize);
    std::swap (serverPort, s.serverPort);
    std::swap (receiveTimeout, s.receiveTimeout);
    std::swap (serverIP, s.serverIP);
  }

  virtual Connection* clone() const 
  {
    return new Connection( *this );
  }

  int Initialize(bool server, bool returnPath = true ) {
    isServer = server;
    hasReturnPath = returnPath;
    if (isServer) {
      return InitializeServer();
    }
    else {
      return InitializeClient();
    }
  }

  virtual long Send(const char *buffer, long len) {
    TG_LOG("Error: you called the base class virtual send function\n");
    return -1;
  }
  virtual long Receive(char *buffer, long len) {
    TG_LOG("Error: you called the base class virtual receive function\n");
    return -1;
  }

  virtual int InitializeServer() {
    TG_LOG("Error: you called the base class server Connection initialization\n");
    return -1;
  }
  virtual int InitializeClient() {
    TG_LOG("Error: you called the base class client Connection initialization\n");
    return -1;
  }
};

class IPV6_Connection : public Connection {
public:
  int sockfd;
  struct sockaddr_in6 local_addr;
  struct sockaddr_in6 remote_addr;

  IPV6_Connection()
    : Connection(true)
  {
    serverPort = 7777;
    receiveTimeout = 5;
    serverIP = "2001:470:489e::3";
  }

  IPV6_Connection(const IPV6_Connection &s)
    : Connection(s),
      sockfd(s.sockfd),
      local_addr(s.local_addr),
      remote_addr(s.remote_addr)
  {
  }

  IPV6_Connection & operator= (const IPV6_Connection &s)
  {
    if (&s != this)
      {
        IPV6_Connection tmp (s);
        swap (tmp);
      }
    return *this;
  }

  virtual IPV6_Connection* clone() const 
  {
    return new IPV6_Connection( *this );
  }

  virtual void swap (IPV6_Connection &s)
  {
    std::swap (sockfd, s.sockfd);
    std::swap (local_addr, s.local_addr);
    std::swap (remote_addr, s.remote_addr);
  }

  ~IPV6_Connection() 
  {
    close(sockfd);
  }

  virtual long send(const char *buffer, long len) {
    long bytes;
    if ((bytes = sendto(sockfd, buffer, len, 0, (struct sockaddr *) &remote_addr, sizeof(remote_addr))) == -1 ) {
      int errsv = errno;
      TG_LOG("ERROR : Couldn't send : %s\n", strerror(errsv) );
    }
    int size;
    int error = ioctl(sockfd, SIOCOUTQ, &size);
    if ( size > bufferSize ) 
      bufferSize = size;
    return bytes;
  }

  virtual long receive(char *buffer, long len) {
    socklen_t remote_addr_len = sizeof(remote_addr);
    long bytes;
    if ((bytes = recvfrom(sockfd, buffer, len,0,(struct sockaddr *)&remote_addr, &remote_addr_len)) == -1) {
      int errsv = errno;
      TG_LOG("ERROR: Haven't received response! : %s!\n", strerror(errsv));
    }
    return bytes;
  }

  virtual int InitializeServer() {
    TG_LOG("Initializing IPV6 Server\n");
    if ((sockfd = socket(AF_INET6, SOCK_DGRAM, 0)) <0) {
      int errsv = errno;
      TG_LOG("ERROR opening socket : %s\n", strerror(errsv));
      return -1;
    }

    int optval = 1;
    int retval = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&optval , sizeof(optval))!=0) {
      TG_LOG("ERROR setting sockopt : %d, %s\n",retval, strerror(retval));
      return -1;
    }
    
    local_addr.sin6_family = AF_INET6;
    local_addr.sin6_port = htons(serverPort);
    local_addr.sin6_scope_id = 0;
    
    if ( (retval = inet_pton(AF_INET6, serverIP.c_str(), (void *)&(local_addr.sin6_addr.s6_addr))) !=1) {
      TG_LOG("ERROR: inet_pton : %d, %s\n",retval, strerror(retval));
      return -1;
    }  
    
    if (bind(sockfd,(struct sockaddr *)&local_addr, sizeof(local_addr))<0) {
      TG_LOG("Couldn't bind!");
      close(sockfd);
      return -1;
    }
    
    struct timeval tv;
    tv.tv_sec = receiveTimeout;
    tv.tv_usec = 0;
    if ( (retval=setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO,&tv,sizeof(tv))) < 0) {
      TG_LOG("Couldn't set sockopts : %d, %s\n",retval, strerror(retval));
      close(sockfd);
      return -1;
    }

    TG_LOG ( "Waiting on %s:%d\n",serverIP.c_str(),serverPort);
    return 0;
  }
  
  virtual int InitializeClient() {
    TG_LOG("Initializing IPV6 Client\n");
    if ((sockfd = socket(AF_INET6, SOCK_DGRAM, 0)) <0) {
      int errsv = errno;
      TG_LOG("ERROR opening socket : %s\n", strerror(errsv));
      return -1;
    }
  
    int optval = 1;
    int retval = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&optval , sizeof(optval))!=0) {
      int errsv = errno;
      TG_LOG("ERROR setting sockopt : %s\n", strerror(errsv));
      return -1;
    }
  
    remote_addr.sin6_family = AF_INET6;
    remote_addr.sin6_port = htons(serverPort);
    remote_addr.sin6_scope_id = 0;
    
    if ( (retval = inet_pton(AF_INET6, serverIP.c_str(), (void *)&(remote_addr.sin6_addr.s6_addr))) !=1) {
      TG_LOG("ERROR: inet_pton : %d\n",retval);
      return -1;
    }
  
    struct timeval tv;
    tv.tv_sec = receiveTimeout;
    tv.tv_usec = 0;
    if ( (retval=setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO,&tv,sizeof(tv))) < 0) {
      TG_LOG("Couldn't set sockopts : %d, %s\n",retval, strerror(retval));
      close(sockfd);
      return -1;
    }
    TG_LOG ( "Connecting to %s:%d\n",serverIP.c_str(),serverPort);
    return 0;
  }  

  void *get_in_addr(struct sockaddr *sa){
    if (sa->sa_family == AF_INET){
      return &(((struct sockaddr_in*)sa)->sin_addr);
    }
    return &(((struct sockaddr_in6*)sa)->sin6_addr);
  }

  u_short get_in_port(struct sockaddr *sa)
  {
    if (sa->sa_family == AF_INET) {
      return ((struct sockaddr_in*)sa)->sin_port;
    }

    return ((struct sockaddr_in6*)sa)->sin6_port;
  }

};

#endif
