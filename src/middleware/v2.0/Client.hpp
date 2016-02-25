#ifndef CLIENT_HPP
#define CLIENT_HPP

#include <math.h>
#include <queue>

#include "log_macro.hpp"
#include "ConnectionSubsys.hpp"
#include "Message.hpp"
#include "NetworkProfile.hpp"

#include <string>

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
    port = 7777;
    bitLength = 4096;
    runTime = -1;
    numPeriods = 1;
    ip = "10.1.1.2";
    outputFile = "clientOutput.csv";
    tgFile = "./tg_profile.csv";
  }

  int Parse(int argc, char **argv) {
    for (int i=0; i < argc; i++)
      {
	if (!strcmp(argv[i], "--profile"))
	  {
	    tgFile = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--output_file"))
	  {
	    outputFile = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--ip"))
	  {
	    ip = argv[i+1];
	  }
	else if (!strcmp(argv[i], "--port"))
	  {
	    ip = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--message_bit_length"))
	  {
	    bitLength = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--num_periods"))
	  {
	    numPeriods = atoi(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--run_time"))
	  {
	    runTime = atof(argv[i+1]);
	  }
	else if (!strcmp(argv[i], "--help"))
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
    TG_LOG("\t tg profile filename\t\t: %s\n", tgFile.c_str());
    TG_LOG("\t number of periods to run\t: %u\n", numPeriods);
    TG_LOG("\t length of time to run\t\t: %f\n", runTime);
    TG_LOG("\t output filename\t\t: %s\n", outputFile.c_str());
    TG_LOG("\t server ip address\t\t: %s\n", ip.c_str());
    TG_LOG("\t server port number\t\t: %lu\n", port);
    TG_LOG("\t bits in message\t\t: %lu\n", bitLength);
  }
};

#endif
