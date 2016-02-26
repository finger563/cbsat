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
  uint64_t buffer = options.buffer;
  uint64_t bucket = options.bucket;
  bool useTBF = options.useTBF;

  Network::NetworkProfile profile;
  std::string profileFile = options.profile;
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize node profile!\n");
    return -1;
  }

  uint64_t bandwidth;
  double latency;
  timespec remainingTime, wakeTime;
  while ( true ) {
    if ( profile.getNextInterval( wakeTime, bandwidth, latency ) == 0 ) {
      TG_LOG("Sleeping until %lu.%09lu\n", wakeTime.tv_sec, wakeTime.tv_nsec);
      while ( clock_nanosleep( CLOCK_REALTIME, TIMER_ABSTIME, &wakeTime, &remainingTime ) == EINTR )
	{
	  TG_LOG("WHO HAS AWOKEN ME FROM MY SLUMBER?!\n");
	}

      TG_LOG("Setting latency to %fs\n", latency);
      setTCLatency(latency, interface, "1:1", "11:");

      TG_LOG("Setting bandwidth to %d bps\n",bandwidth);

      if (bandwidth == 0)
	bandwidth = 10;

      uint64_t ceil_bandwidth = bandwidth;
      ceil_bandwidth = (uint64_t)((double)bandwidth * 1.01f);
      if ( ceil_bandwidth == bandwidth )
	ceil_bandwidth++;

      if ( isRouter )
	{
	  if ( useTBF )
	    setTC(bandwidth, ceil_bandwidth, buffer, bucket, interface, parent, handle, useTBF);
	  else
	    {
	      setTC(bandwidth, bandwidth, buffer, bucket, interface, parent, handle, useTBF);
	      std::string sub_handle = parent + "10";
	      setTC(bandwidth, bandwidth, buffer, bucket, interface, handle, sub_handle, useTBF, 0);
	      sub_handle = parent + "20";
	      setTC(10, bandwidth, buffer, bucket, interface, handle, sub_handle, useTBF, 1);
	    }
	}
      else
	{
	  if ( useTBF )
	    setTC(bandwidth, ceil_bandwidth, buffer, bucket, interface, parent, handle, useTBF);
	  else
	    {
	      setTC(bandwidth, bandwidth, buffer, bucket, interface, parent, handle, useTBF);
	      std::string sub_handle = parent + "10";
	      setTC(bandwidth, bandwidth, buffer, bucket, interface, handle, sub_handle, useTBF);
	    }
	}
    }
  }
}

// Forks/Execs to call TC for setting HTB bandwidth
void setTC( uint64_t bandwidth, uint64_t ceil, uint64_t buffer, uint64_t bucket,
	    std::string interface, std::string parent, std::string handle, bool useTBF, int priority )
{
  std::string tc_args;
  if ( useTBF )
    {
      tc_args = "qdisc change "
	"dev " + interface + " "
	"parent " + parent + " "
	"handle " + handle + " tbf "
	"rate " + std::to_string(bandwidth) + "bit "
	"burst " + std::to_string(bucket) + "b "
	"limit " + std::to_string(buffer) + "k ";
    }
  else
    {
      tc_args = "class change "
	"dev " + interface + " "
	"parent " + parent + " "
	"classid " + handle + " htb "
	"rate " + std::to_string(bandwidth) + "bit "
	"ceil " + std::to_string(ceil) + "bit ";
      if ( priority >= 0 )
	tc_args += "prio " + std::to_string(priority);
    }
  forkTC(tc_args);
}

void setTCLatency( double latency,
		   std::string interface, std::string parent, std::string handle )
{
  std::string tc_args;
  
  tc_args = "qdisc change "
    "dev " + interface + " "
    "parent " + parent + " "
    "handle " + handle + " netem "
    "delay " + std::to_string((uint64_t)(latency*1000)) + "ms ";
  forkTC(tc_args);
}

void forkTC(std::string tc_args)
{
  std::string tc_binary = "/sbin/tc";
  TG_LOG("  cmd: %s\n", tc_args.c_str());
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
