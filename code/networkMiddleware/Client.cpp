
#include "Client.hpp"

NetworkProfile profile, bufferProfile;
static std::vector <Message*> messages;
IPV6_Connection interface;

double maxLatency=0;

long messageBitLength;
long messageStrLength;
static long id = 0;

long precision = 30;// for file output

int main(int argc, char **argv) {
  timespec timeout, remaining;

  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  std::string profileFile = options.tgFile;  
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize TG profile!\n");
    return -1;
  }

  std::string outputFile = options.outputFile;
  messageBitLength = options.bitLength;
  messageStrLength = ceil((double)messageBitLength/8.0f);
  double runTime = ( options.runTime > 0 ) ? options.runTime : profile.period*options.numPeriods ;

  std::string bufferProfileFile = options.bufferFile;
  bufferProfile.initializeFromFile(bufferProfileFile.c_str());

  if ( NetworkMiddleware::InitClient(bufferProfile,options.ip,options.port) != 0 ) {
    TG_LOG("ERROR: couldn't initialize network middleware!\n");
    return -1;
  }

  double timeDiff = 0;
  timespec startTime;
  clock_gettime(CLOCK_REALTIME,&startTime);

  while (true) {
    Message* data = new Message(messageBitLength, id, 0);
    messages.push_back(data);      
    data->TimeStamp();
    NetworkMiddleware::send(data);

    timeDiff = (double)(data->FirstEpochTime().tv_sec - 
			startTime.tv_sec);
    timeDiff += (double)(data->FirstEpochTime().tv_nsec - 
			 startTime.tv_nsec)/1000000000.0f;

    if ( timeDiff >= runTime )
      break;

    double timerDelay = profile.Delay(data->Bits(),data->FirstEpochTime());
    id++;
    if ( timerDelay > 0 ) {
      double fractpart,intpart;
      fractpart = modf(timerDelay,&intpart);
      timeout.tv_sec = (unsigned long long)(intpart);
      timeout.tv_nsec = (unsigned long)(fractpart*1000000000.0);
      int return_code = nanosleep (&timeout, &remaining);
    }
  }

  NetworkMiddleware::Exit();

  double maxLatency = 0;
  double latency = 0;
  for (long i=0; i<messages.size(); i++) {
    std::vector<timespec> times(messages[i]->EpochTimes());
    latency = (double)(times.back().tv_sec - times.front().tv_sec);
    latency += ((double)(times.back().tv_nsec - times.front().tv_nsec)/1000000000.0f);
    if ( latency > maxLatency )
      maxLatency = latency;
  }

  write_data(outputFile);

  for ( long i=0; i<messages.size(); i++) {
    if ( messages[i] != NULL )
      delete messages[i];
  }
  messages.clear();

  TG_LOG("Max bits in UDP socket buffer: %d\n",
	 interface.bufferSize*8);
  TG_LOG("Max bits in middleware buffer: %lu\n",
	 NetworkMiddleware::buffer.MaxSize());
  TG_LOG("Max message latency: %f seconds\n",
	 maxLatency);
}

int write_data(std::string fname) {
  for (long i=0;i<messages.size();i++) {
    if ( append_data(fname,messages[i]) == -1 ) {
      TG_LOG("Couldn't append message %lu to file %s\n",i,fname.c_str());
    }
  }  
  return 0;
}

int append_data(std::string fname, Message* data) {
  std::ofstream file(fname.c_str(), std::ofstream::app);
  if ( !file.is_open() ) {
    TG_LOG("ERROR: Couldn't open %s for appending!\n",fname.c_str());
    return -1;
  }
  file << data->Id() << "," << std::setprecision(precision)
       << data->FirstDoubleTime() << ","
       << data->LastDoubleTime() << ","
       << data->Bits()
       << "\n";
  file.close();
  return 0;
}
