#include "tcWrapper.hpp"

// Main function: loops forever-> sleep, setTC, sleep, setTC, ...
int main(int argc, char **argv) {
  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  std::string interface  = options.interface;
  std::string parent = options.parent;
  std::string handle = options.handle;
  bool isRouter = options.isRouter;

  Network::NetworkProfile profile;
  std::string profileFile = options.profile;
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize node profile!\n");
    return -1;
  }

  unsigned long long bandwidth;
  double latency;
  timespec remainingTime, wakeTime;
  while ( true ) {
    if ( profile.getNextInterval( wakeTime, bandwidth, latency ) == 0 ) {
      TG_LOG("Sleeping until %lu.%09lu\n", wakeTime.tv_sec, wakeTime.tv_nsec);
      while ( clock_nanosleep( CLOCK_REALTIME, TIMER_ABSTIME, &wakeTime, &remainingTime ) == EINTR )
	{
	  TG_LOG("WHO HAS AWOKEN ME FROM MY SLUMBER?!\n");
	}

      TG_LOG("Setting bandwidth to %llu bps and latency to %fs\n",bandwidth, latency);

      if (bandwidth == 0)
	bandwidth = 10;

      unsigned long long ceil_bandwidth = bandwidth;
      ceil_bandwidth = (unsigned long long)((double)bandwidth * 1.01f);
      if ( ceil_bandwidth == bandwidth )
	ceil_bandwidth++;

      if ( isRouter )
	{
	  setTC(bandwidth, ceil_bandwidth, latency, interface, "11:1", "2:");
	  //setTC(bandwidth, bandwidth, latency, interface, "2:", "2:1");
	  //setTC(bandwidth, bandwidth, latency, interface, "2:1", "2:10", 0);
	  //setTC(bandwidth, bandwidth, latency, interface, "2:1", "2:20", 1);
	}
      else
	{
	  setTC(bandwidth, ceil_bandwidth, latency, interface, parent, handle);
	}
    }
  }
}

// Forks/Execs to call TC for setting HTB bandwidth
void setTC( unsigned long long bandwidth, unsigned long long ceil, double latency,
	    std::string interface, std::string parent, std::string handle, int priority )
{
  std::string tc_binary = "/sbin/tc";
  char bw_str[100];
  sprintf(bw_str,"%llu",bandwidth);
  char ceil_str[100];
  sprintf(ceil_str,"%llu",ceil);
  char prio_str[10];
  sprintf(prio_str, "%d",priority);

  std::string tc_args = "qdisc replace dev " + interface
    + " parent " + parent + " handle " + handle + " tbf rate "
    + bw_str + "bit peakrate " + ceil_str + "bit burst 2kb latency 100000ms minburst 1500";

#if 0
  std::string tc_args = "class replace dev " + interface
    + " parent " + parent + " classid " + handle + " htb rate "
    + bw_str + "bit ceil " + ceil_str + "bit"; // burst 10000000";
  if ( priority >= 0 )
    tc_args += " prio " + std::string(prio_str);
#endif

  // FORK
  pid_t parent_pid = getpid();
  pid_t my_pid = fork();
  if ( my_pid == -1 )
    {
      TG_LOG("ERROR: COULDNT FORK\n");
    }
  else if ( my_pid == 0 ) // child
    {
      std::vector<std::string> string_args;
      string_args.push_back(tc_binary);
      std::string s;
      std::istringstream f(tc_args);
      while ( getline(f, s, ' ') )
	{
	  string_args.push_back(s);
	}
      // build args
      char *args[string_args.size() + 1]; // must be NULL terminated
      args[string_args.size()] = NULL;
      for (int i=0; i < string_args.size(); i++)
	{
	  args[i] = new char[string_args[i].length()];
	  sprintf(args[i], "%s", string_args[i].c_str());
	}
      // EXECV
      execvp(args[0], args);
      TG_LOG("ERROR: EXEC COULDN'T COMPLETE\n");
    }
}
