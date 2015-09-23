#ifndef CLIENT_HPP
#define CLIENT_HPP

#include <math.h>
#include <queue>

#include "log_macro.hpp"
#include "ConnectionSubsys.hpp"
#include "Message.hpp"
#include "NetworkProfile.hpp"

#include <string>

void *sendFunc(std::string data);
void labelMessage(long index);
int write_data(std::string fname);
int append_data(std::string fname, Network::Message* data);


class Options {
public:
  char ip[256];
  long port;
  long bitLength;
  double runTime;
  int numPeriods;
  char tgFile[256];
  char bufferFile[256];
  char outputFile[256];

  Options() {
    this->port = 7777;
    this->bitLength = 4096;
    this->runTime = -1;
    this->numPeriods = 1;
    sprintf(this->ip,"2001:470:489e::3");
    sprintf(this->outputFile,"clientOutput.csv");
    sprintf(this->tgFile, "./tg_profile.csv");
    sprintf(this->bufferFile, "./namek_crm_config.csv" );
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
	case 'P':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  sprintf(this->tgFile,"%s",p+2);
	  break;
	case 'B':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  sprintf(this->bufferFile,"%s",p+2);
	  break;
	case 'o':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  sprintf(this->outputFile,"%s",p+2);
	  break;
	case 'i':
	  for (int i=0;i<=strlen(p+2);i++) {
	    if ( (p+2)[i] == ' ' ) {
	      (p+2)[i] = 0;
	      break;
	    }
	  }
	  sprintf(this->ip,"%s",p+2);
	  break;
	case 'p':
	  this->port = atoi(p+2);
	  break;
	case 'b':
	  this->bitLength = atoi(p+2);
	  break;
	case 'N':
	  this->numPeriods = atoi(p+2);
	  break;
	case 'T':
	  this->runTime = atof(p+2);
	  break;
	case '?':
	default:
	  TG_LOG("usage: \n\t%s\n"
		 "\t\t -P <TG profile filename>\n"
		 "\t\t -B <buffer profile filename>\n"
		 "\t\t -N <number of periods to run>\n"
		 "\t\t -T <length of time to run>\n"
		 "\t\t -o <output file filename>\n"
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
    TG_LOG("\t tg profile filename\t\t: %s\n",this->tgFile);
    TG_LOG("\t buffer profile filename\t: %s\n",this->bufferFile);
    TG_LOG("\t number of periods to run\t: %u\n",this->numPeriods);
    TG_LOG("\t length of time to run\t\t: %f\n",this->runTime);
    TG_LOG("\t output filename\t\t: %s\n",this->outputFile);
    TG_LOG("\t server ipv6 address\t\t: %s\n",this->ip);
    TG_LOG("\t server port number\t\t: %lu\n",this->port);
    TG_LOG("\t bits in message\t\t: %lu\n",this->bitLength);
  }
};

#endif
