#ifndef SERVER_HPP
#define SERVER_HPP

#include <math.h>
#include <string>

#include "log_macro.hpp"
#include "ConnectionSubsys.hpp"
#include "Message.hpp"
#include "NetworkProfile.hpp"

class Options {
public:
  std::string ip;
  std::string outputFile;
  std::string tgFile;
  long port;
  long bitLength;

  Options() {
    port = 7777;
    bitLength = 4096;
    ip = "10.1.1.2";
    outputFile = "serverOutput.csv";
    tgFile = "receiver.csv";
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
	else if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
		   "\t\t --profile <TG profile filename>\n"
		   "\t\t --output_file <filename for data output file>\n"
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
    TG_LOG("\t profile filename\t\t: %s\n", tgFile.c_str());
    TG_LOG("\t output filename\t\t: %s\n", outputFile.c_str());
    TG_LOG("\t server ip address\t\t: %s\n", ip.c_str());
    TG_LOG("\t server port number\t\t: %lu\n", port);
    TG_LOG("\t bits in message\t\t: %lu\n", bitLength);
  }
};

#endif
