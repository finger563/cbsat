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

void setTC( unsigned long long bandwidth, unsigned long long ceil, double latency, unsigned long long buffer,
	    std::string interface, std::string parent, std::string handle, bool useTBF = true, int priority = -1 );

class Options {
public:
  std::string interface;
  std::string parent;
  std::string handle;
  std::string profile;
  bool isRouter;
  bool useTBF;
  unsigned long long buffer;

  Options() {
    interface = "eth0";
    parent = "11:1";
    handle = "111:";
    profile = "node_profile.csv";
    isRouter = false;
    useTBF = true;
  }

  int Parse(int argc, char **argv) {
    
    for (int i=0; i < argc; i++)
      {
	if (!strcmp(argv[i], "--profile"))
	  {
	    profile = argv[i+1];
	  }
	if (!strcmp(argv[i], "--buffer"))
	  {
	    buffer = atoi(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--use_tbf"))
	  {
	    useTBF = true;
	  }
	if (!strcmp(argv[i], "--use_htb"))
	  {
	    useTBF = false;
	  }
	if (!strcmp(argv[i], "--buffer"))
	  {
	    buffer = atoi(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--is_router"))
	  {
	    isRouter = true;
	  }
	if (!strcmp(argv[i], "--interface"))
	  {
	    interface = argv[i+1];
	  }
	if (!strcmp(argv[i], "--parent"))
	  {
	    parent = argv[i+1];
	  }
	if (!strcmp(argv[i], "--handle"))
	  {
	    handle = argv[i+1];
	  }
	if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
		   "\t\t --profile <profile name>\n"
		   "\t\t --is_router (this node is a router node)\n"
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
    TG_LOG("\t buffer\t\t\t: %llu\n", buffer);
    TG_LOG("\t interface name\t\t: %s\n", interface.c_str());
    TG_LOG("\t parent name\t\t: %s\n", parent.c_str());
    TG_LOG("\t handle name\t\t: %s\n", handle.c_str());
  }
};

#endif
