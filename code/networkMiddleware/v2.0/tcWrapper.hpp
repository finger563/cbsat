#ifndef TCWRAPPER_HPP
#define TCWRAPPER_HPP

#include <unistd.h>
#include <sys/types.h>
#include <time.h>
#include <errno.h>

#include <math.h>
#include <string>

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
    
    if ( argc < 2 )
      return 0;
    int c;
    char str[256];
    sprintf(str,"%s",argv[1]);
    if ( argc > 2 ) {
      for (int i=2;i<argc;i++) {
	sprintf(str,"%s %s",str,argv[i]);
      }
    }
    char *p = strtok(str,"-");
    while (p != 0) {
      switch (p[0])
	{
	case 'p':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  this->profile = p+2;
	  break;
	case 'i':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  this->interface = p+2;
	  break;
	case '?':
	default:
	  TG_LOG("usage: \n\t%s\n"
		 "\t\t -p <profile name>\n"
		 "\t\t -i <interface name>\n"
		 ,argv[0]);
	  return -1;
	}
      p = strtok(NULL,"-");
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
