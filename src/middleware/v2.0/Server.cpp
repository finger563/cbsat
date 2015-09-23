#include "Server.hpp"

long messageBitLength;
long messageStrLength;
char *messageData;
std::string outputFile;
IPV6_Connection interface;

Network::NetworkProfile profile;

void *recvFunc(Network::Message* data) {
  if ( data != NULL )
    {
      memset(messageData,0,messageStrLength+2);
      if ( interface.receive(messageData,messageStrLength) > 0 )
	{
	  long id = atol(messageData);
	  if ( id >=0 )
	    {
	      data->TimeStamp();
	      data->Id(id);
	      data->Bytes(strlen(messageData));
	      append_data(outputFile,*data);
	    }
	}
    }
  else
    return (void *)NULL;
}

int main(int argc, char **argv) {
  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  outputFile = options.outputFile;

  messageBitLength = options.bitLength;
  messageStrLength = ceil((double)messageBitLength/8.0f);
  messageData = new char[messageStrLength+2];

  std::string profileFile = options.tgFile;  
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize TG profile!\n");
    return -1;
  }

  interface.serverIP = options.ip;
  interface.serverPort = options.port;
  if ( interface.Initialize(true,false) != 0 ) {
    TG_LOG("ERROR: Couldn't initialize interface!\n");
    return -1;
  }

  double timerDelay = 0;
  timespec timeout, remaining;
  long id = 0;

  while ( true ) {
    memset(messageData,0,messageStrLength+2);

    if ( interface.receive(messageData,messageStrLength) > 0 ) {

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
