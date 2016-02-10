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
  unsigned long long buffer = options.buffer;
  bool useTBF = options.useTBF;

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
	  if ( useTBF )
	    setTC(bandwidth, ceil_bandwidth, latency, buffer, interface, parent, handle, useTBF);
	  else
	    {
	      setTC(bandwidth, bandwidth, latency, buffer, interface, parent, handle, useTBF);
	      std::string sub_handle = parent + "10";
	      setTC(bandwidth, bandwidth, latency, buffer, interface, handle, sub_handle, useTBF, 0);
	      sub_handle = parent + "20";
	      setTC(10, bandwidth, latency, buffer, interface, handle, sub_handle, useTBF, 1);
	    }
	}
      else
	{
	  if ( useTBF )
	    setTC(bandwidth, ceil_bandwidth, latency, buffer, interface, parent, handle, useTBF);
	  else
	    {
	      setTC(bandwidth, bandwidth, latency, buffer, interface, parent, handle, useTBF);
	      std::string sub_handle = parent + "10";
	      setTC(bandwidth, bandwidth, latency, buffer, interface, handle, sub_handle, useTBF);
	    }
	}
    }
  }
}

// Forks/Execs to call TC for setting HTB bandwidth
void setTC( unsigned long long bandwidth, unsigned long long ceil, double latency, unsigned long long buffer,
	    std::string interface, std::string parent, std::string handle, bool useTBF, int priority )
{
  std::string tc_binary = "/sbin/tc";
  char buff_str[100];
  sprintf(buff_str,"%llu",buffer);
  char bw_str[100];
  sprintf(bw_str,"%llu",bandwidth);
  char ceil_str[100];
  sprintf(ceil_str,"%llu",ceil);
  char prio_str[10];
  sprintf(prio_str, "%d",priority);

  std::string tc_args;
  
  if ( useTBF )
    {
      tc_args = "qdisc replace dev " + interface
	+ " parent " + parent + " handle " + handle + " tbf rate "
	+ bw_str + "bit peakrate " + ceil_str + "bit burst " + buff_str + "b latency 100000ms mtu 1540 ";
    }
  else
    {
      tc_args = "class replace dev " + interface
	+ " parent " + parent + " classid " + handle + " htb rate "
	+ bw_str + "bit ceil " + ceil_str + "bit burst " + buff_str;
      if ( priority >= 0 )
	tc_args += " prio " + std::string(prio_str);
    }

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
