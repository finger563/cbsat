#include "tcWrapper.hpp"

NetworkProfile profile;

int main(int argc, char **argv) {
  Options options;
  if ( options.Parse(argc,argv) == -1 )
    return -1;
  options.Print();

  std::string interface  = options.interface;
  std::string profileFile = options.profile;
  if ( profile.initializeFromFile(profileFile.c_str()) != 0 ) {
    TG_LOG("ERROR: couldn't initialize node profile!\n");
    return -1;
  }

  unsigned long long bandwidth;
  unsigned long long latency;
  timespec remainingTime, wakeTime;
  int pid = 1;
  while ( true ) {
    if ( profile.getNextInterval( wakeTime, bandwidth, latency ) == 0 ) {
      TG_LOG("Sleeping until %lu.%09lu\n", wakeTime.tv_sec, wakeTime.tv_nsec);
      while ( clock_nanosleep( CLOCK_REALTIME, TIMER_ABSTIME, &wakeTime, &remainingTime ) == EINTR ) {
	TG_LOG("WHO HAS AWOKEN ME FROM MY SLUMBER?!\n");
      }

      TG_LOG("Setting bandwidth to %llu bps and latency to %llu ms\n",bandwidth, latency);

      char tcCommand[256];
      sprintf( tcCommand,
	       "qdisc replace dev %s root tbf rate %llu.0bit latency %llu.0ms burst 1540", 
	       interface.c_str(),
	       bandwidth,
	       latency);

      char *pch;
      char *tc_argv[50];

      int num_args = 1;

      tc_argv[0] = (char*)malloc(strlen("/sbin/tc")+1);
      sprintf(tc_argv[0],"/sbin/tc");

      pch = strtok(tcCommand," ");
      while ( pch != NULL && num_args < 50 ) {
	tc_argv[num_args] = (char*)malloc(strlen(pch)+1);
	sprintf(tc_argv[num_args],"%s",pch);
	num_args++;
	pch = strtok(NULL," ");
      }

      tc_argv[num_args] = (char *)NULL;

      pid = vfork();
      if ( pid == 0 ) { // child
	int tc_ret_val = execv(tc_argv[0],tc_argv);
	TG_LOG("ERROR: execv failed with retval: %d\n",tc_ret_val);
	exit(1);
      }
      else if ( pid > 0 ) { // parent
	for (int i=0;i<num_args;i++) {
	  free(tc_argv[i]);
	}
      }
      else { // error
	TG_LOG("ERROR: could not spawn child to run tc!\n");
      }
    }
  }
}
