#ifndef TCWRAPPER_HPP
#define TCWRAPPER_HPP

#include <unistd.h>
#include <sys/types.h>
#include <time.h>
#include <errno.h>

#include <math.h>
#include <string>
#include <sstream>

#include "NetworkProfile.hpp"
#include "log_macro.hpp"

void setTCLatency( double latency,
		   std::string interface, std::string parent, std::string handle );

void setTC( uint64_t bandwidth, uint64_t ceil, uint64_t buffer, uint64_t bucket,
	    std::string interface, std::string parent, std::string handle, bool useTBF = true, int priority = -1 );

void forkTC( std::string tc_args );

class Options {
public:
  std::string interface;
  std::string parent;
  std::string handle;
  std::string profile;
  bool isRouter;
  bool useTBF;
  uint64_t buffer;
  uint64_t bucket;

  Options() {
    interface = "eth0";
    parent = "1:";
    handle = "1:1";
    profile = "node_profile.csv";
    isRouter = false;
    useTBF = true;
    buffer = 10000;
    bucket = 100;
  }

  int Parse(int argc, char **argv) {
    
    for (int i=0; i < argc; i++)
      {
	if (!strcmp(argv[i], "--profile"))
	  {
	    profile = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--buffer"))
	  {
	    buffer = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--bucket"))
	  {
	    bucket = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--use_tbf"))
	  {
	    useTBF = true;
	  }
	else if (!strcmp(argv[i], "--use_htb"))
	  {
	    useTBF = false;
	  }
	else if (!strcmp(argv[i], "--buffer"))
	  {
	    buffer = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--is_router"))
	  {
	    isRouter = true;
	  }
	else if (!strcmp(argv[i], "--interface"))
	  {
	    interface = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--parent"))
	  {
	    parent = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--handle"))
	  {
	    handle = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
		   "\t\t --profile <profile name>\n"
		   "\t\t --is_router (this node is a router node)\n"
		   "\t\t --use_tbf (TC filter is TBF)\n"
		   "\t\t --use_htb (TC filter is HTB)\n"
		   "\t\t --buffer <buffer size>\n"
		   "\t\t --bucket <buffer size>\n"
		   "\t\t --interface <interface name>\n"
		   "\t\t --parent <parent TC object>\n"
		   "\t\t --handle <handle TC object>\n"
		   ,argv[0]);
	    return -1;
	  }
      }
    return 0;
  }
  
  void Print() {
    TG_LOG("Options():\n");
    TG_LOG("\t profile name\t\t: %s\n", profile.c_str());
    TG_LOG("\t is router?\t\t: %d\n", isRouter);
    TG_LOG("\t use tbf?\t\t: %d\n", useTBF);
    TG_LOG("\t buffer\t\t\t: %d\n", buffer);
    TG_LOG("\t bucket\t\t\t: %d\n", buffer);
    TG_LOG("\t interface name\t\t: %s\n", interface.c_str());
    TG_LOG("\t parent name\t\t: %s\n", parent.c_str());
    TG_LOG("\t handle name\t\t: %s\n", handle.c_str());
  }
};

#endif
