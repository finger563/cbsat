#ifndef SERVER_HPP
#define SERVER_HPP

#include <math.h>
#include <string>

#include "log_macro.hpp"
#include "ConnectionSubsys.hpp"
#include "Message.hpp"

int append_data(std::string fname, Network::Message& data);

class Options {
public:
  std::string ip;
  std::string outputFile;
  long port;
  long bitLength;

  Options() {
    this->port = 7777;
    this->bitLength = 4096;
    this->ip = "2001:470:489e::3";
    this->outputFile = "serverOutput.csv";
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
	case 'o':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  this->outputFile = p+2;
	  break;
	case 'i':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  this->ip = p+2;
	  break;
	case 'p':
	  this->port = atoi(p+2);
	  break;
	case 'b':
	  this->bitLength = atoi(p+2);
	  break;
	case '?':
	default:
	  TG_LOG("usage: \n\t%s\n"
		 "\t\t -o <filename for data output file>\n"
		 "\t\t -i <ipv6 address of server>\n"
		 "\t\t -p <port number of server>\n"
		 "\t\t -b <# bits in message>\n"
		 ,argv[0]);
	  return -1;
	}
      p = strtok(NULL,"-");
    }
    return 0;
  }
  
  void Print() {
    TG_LOG("Options():\n");
    TG_LOG("\t output filename\t\t: %s\n",this->outputFile.c_str());
    TG_LOG("\t server ipv6 address\t\t: %s\n",this->ip.c_str());
    TG_LOG("\t server port number\t\t: %lu\n",this->port);
    TG_LOG("\t bits in message\t\t: %lu\n",this->bitLength);
  }
};

#endif
