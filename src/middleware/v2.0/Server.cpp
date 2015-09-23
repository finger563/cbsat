#include "Server.hpp"

int main(int argc, char **argv) {
  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  std::string outputFile = options.outputFile;

  long messageBitLength = options.bitLength;
  long messageStrLength = ceil((double)messageBitLength/8.0f);
  char *messageData = new char[messageStrLength+2];

  Network::NetworkProfile profile;
  std::string profileFile = options.tgFile;  
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize TG profile!\n");
    return -1;
  }

  Connection* interface;
  if ( options.ip.find(".") != std::string::npos )
    interface = new IPV4_Connection();
  else
    interface = new IPV6_Connection();
  interface->serverIP = options.ip;
  interface->serverPort = options.port;
  if ( interface->Initialize(true,false) != 0 ) {
    TG_LOG("ERROR: Couldn't initialize interface!\n");
    return -1;
  }

  double timerDelay = 0;
  timespec timeout, remaining;
  long id = 0;

  while ( true ) {
    memset(messageData,0,messageStrLength+2);

    if ( interface->Receive(messageData,messageStrLength) > 0 ) {

      Network::Message msg;
      long id = atol(messageData);

      if ( id >=0 ) {
	msg.TimeStamp();
	msg.Id(id);
	msg.Bytes(strlen(messageData));
	append_data(outputFile,msg);
      }

      timerDelay = profile.Delay(msg.Bits(),msg.FirstEpochTime());
      if ( timerDelay > 0 ) {
	double fractpart,intpart;
	fractpart = modf(timerDelay,&intpart);
	timeout.tv_sec = (unsigned long long)(intpart);
	timeout.tv_nsec = (unsigned long)(fractpart*1000000000.0);
	int return_code = nanosleep (&timeout, &remaining);
      }
    }
  }
}

long precision = 30;// for file output
int append_data(std::string fname, Network::Message& data) {
  std::ofstream file(fname.c_str(),std::ofstream::app);
  if ( !file.is_open() )
    return -1;
  file << data.Id() << "," << std::setprecision(precision)
       << data.LastDoubleTime() << ","
       << data.Bits()
       << "\n";
  file.close();
  return 0;
}
