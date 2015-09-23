#ifndef SERVER_HPP
#define SERVER_HPP

#include <math.h>
#include <string>

#include "log_macro.hpp"
#include "ConnectionSubsys.hpp"
#include "Message.hpp"
#include "NetworkProfile.hpp"

int append_data(std::string fname, Network::Message& data);

class Options {
public:
  std::string ip;
  std::string outputFile;
  std::string tgFile;
  long port;
  long bitLength;

  Options() {
    this->port = 7777;
    this->bitLength = 4096;
    this->ip = "10.1.1.2";
    this->outputFile = "serverOutput.csv";
    this->tgFile = "receiver.csv";
  }

  int Parse(int argc, char **argv) {
    for (int i=0; i < argc; i++)
      {
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
	if (!strcmp(argv[i], "--help"))
	  {
	    TG_LOG("usage: \n\t%s\n"
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
    TG_LOG("\t profile filename\t\t: %s\n",this->tgFile.c_str());
    TG_LOG("\t output filename\t\t: %s\n",this->outputFile.c_str());
    TG_LOG("\t server ip address\t\t: %s\n",this->ip.c_str());
    TG_LOG("\t server port number\t\t: %lu\n",this->port);
    TG_LOG("\t bits in message\t\t: %lu\n",this->bitLength);
  }
};

#endif
