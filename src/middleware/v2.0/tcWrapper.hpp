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

class Options {
public:
  std::string interface;
  std::string profile;

  Options() {
    interface = "eth0";
    profile = "node_profile.csv";
  }

  int Parse(int argc, char **argv) {
    
    for (int i=0; i < argc; i++)
      {
	if (!strcmp(argv[i], "--profile"))
	  {
	    profile = argv[i+1];
	  }
	if (!strcmp(argv[i], "--interface"))
	  {
	    interface = argv[i+1];
	  }
	if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
		   "\t\t -p <profile name>\n"
		   "\t\t -i <interface name>\n"
		   ,argv[0]);
	    return -1;
	  }
      }
    return 0;
  }
  
  void Print() {
    TG_LOG("Options():\n");
    TG_LOG("\t profile name\t\t: %s\n",this->profile.c_str());
    TG_LOG("\t interface name\t\t: %s\n",this->interface.c_str());
  }
};

#endif
