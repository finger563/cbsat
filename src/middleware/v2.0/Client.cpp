
#include "Client.hpp"

int main(int argc, char **argv) {

  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  Network::NetworkProfile profile;
  std::string profileFile = options.tgFile;  
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize TG profile!\n");
    return -1;
  }

  std::string outputFile = options.outputFile;
  long messageBitLength = options.bitLength;
  long messageStrLength = ceil((double)messageBitLength/8.0f);
  double runTime = ( options.runTime > 0 ) ? options.runTime : profile.period*options.numPeriods ;

  Connection* interface;
  if ( options.ip.find(".") != std::string::npos )
    interface = new IPV4_Connection();
  else
    interface = new IPV6_Connection();
  interface->serverIP = options.ip;
  interface->serverPort = options.port;
  if ( interface->Initialize(false) != 0 ) {
    TG_LOG("ERROR: Couldn't initialize interface!\n");
    return -1;
  }

  double timerDelay = 0;
  timespec timeout, remaining;

  double timeDiff = 0;
  timespec startTime;
  clock_gettime(CLOCK_REALTIME,&startTime);

  long id = 0;
  std::vector<Network::Message*> messages;

  while (true) {
    Network::Message* data = new Network::Message(messageBitLength, id++);
    messages.push_back(data);      
    data->TimeStamp();
    
    interface->Send( data->Buffer().c_str(),
		     data->Bytes() );

    timeDiff = (double)(data->FirstEpochTime().tv_sec - 
			startTime.tv_sec);
    timeDiff += (double)(data->FirstEpochTime().tv_nsec - 
			 startTime.tv_nsec)/1000000000.0f;

    if ( timeDiff >= runTime )
      break;

    timerDelay = profile.Delay(data->Bits(),data->FirstEpochTime());
    if ( timerDelay > 0 ) {
      double fractpart,intpart;
      fractpart = modf(timerDelay,&intpart);
      timeout.tv_sec = (unsigned long long)(intpart);
      timeout.tv_nsec = (unsigned long)(fractpart*1000000000.0);
      int return_code = nanosleep (&timeout, &remaining);
    }
  }

  double maxLatency = 0;
  double latency = 0;
  for (long i=0; i<messages.size(); i++) {
    std::vector<timespec> times(messages[i]->EpochTimes());
    latency = (double)(times.back().tv_sec - times.front().tv_sec);
    latency += ((double)(times.back().tv_nsec - times.front().tv_nsec)/1000000000.0f);
    if ( latency > maxLatency )
      maxLatency = latency;
  }

  Network::write_data(outputFile.c_str(), messages);

  for ( long i=0; i<messages.size(); i++) {
    if ( messages[i] != NULL )
      delete messages[i];
  }
  messages.clear();

  TG_LOG("Max bits in UDP socket buffer: %d\n",
	 interface->bufferSize*8);
  TG_LOG("Max message latency: %f seconds\n",
	 maxLatency);
}
