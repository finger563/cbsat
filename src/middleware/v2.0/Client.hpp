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
  long port;
  long bitLength;
  double runTime;
  int numPeriods;
  std::string ip;
  std::string tgFile;
  std::string outputFile;

  Options() {
    this->port = 7777;
    this->bitLength = 4096;
    this->runTime = -1;
    this->numPeriods = 1;
    this->ip = "10.1.1.2";
    this->outputFile = "clientOutput.csv";
    this->tgFile = "./tg_profile.csv";
  }

  int Parse(int argc, char **argv) {
    for (int i=0; i < argc; i++)
      {
	if (!strcmp(argv[i], "--profile"))
	  {
	    this->tgFile = argv[i+1];
	  }
	if (!strcmp(argv[i], "--output_file"))
	  {
	    this->outputFile = argv[i+1];
	  }
	if (!strcmp(argv[i], "--ip"))
	  {
	    this->ip = argv[i+1];
	  }
	if (!strcmp(argv[i], "--port"))
	  {
	    this->ip = atoi(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--message_bit_length"))
	  {
	    this->bitLength = atoi(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--num_periods"))
	  {
	    this->numPeriods = atoi(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--run_time"))
	  {
	    this->runTime = atof(argv[i+1]);
	  }
	if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
		   "\t\t --profile <TG profile filename>\n"
		   "\t\t --num_periods <number of periods to run>\n"
		   "\t\t --run_time <length of time to run>\n"
		   "\t\t --output_file <output file filename>\n"
		   "\t\t --ip <ipv6 address of server>\n"
		   "\t\t --port <port number of server>\n"
		   "\t\t --message_bit_length <# bits in message>\n"
		   ,argv[0]);
	    return -1;
	  }
      }
    return 0;
  }
  
  void Print() {
    TG_LOG("Options():\n");
    TG_LOG("\t tg profile filename\t\t: %s\n",this->tgFile.c_str());
    TG_LOG("\t number of periods to run\t: %u\n",this->numPeriods);
    TG_LOG("\t length of time to run\t\t: %f\n",this->runTime);
    TG_LOG("\t output filename\t\t: %s\n",this->outputFile.c_str());
    TG_LOG("\t server ip address\t\t: %s\n",this->ip.c_str());
    TG_LOG("\t server port number\t\t: %lu\n",this->port);
    TG_LOG("\t bits in message\t\t: %lu\n",this->bitLength);
  }
};

#endif
