#include <vector>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <math.h>

class ResourceEntry {
public:
  unsigned long long time;          // sec
  unsigned long long bandwidth;     // bits / sec
  unsigned long long data;          // bits

  ResourceEntry(unsigned long long t, unsigned long long b, unsigned long long d) : time(t), bandwidth(b), data(d) {}

  std::string toString() {
    char charBuf[100];
    sprintf(charBuf,"%llu, %llu, %llu",
	    time, bandwidth, data);
    std::string retStr = charBuf;
    return retStr;
  }
};

unsigned long long getDataAtTime(unsigned long long, ResourceEntry, std::vector<ResourceEntry>);
unsigned long long getTimeAtData(unsigned long long, ResourceEntry, std::vector<ResourceEntry>);

unsigned long long Delay(unsigned long long data,
			 unsigned long long start,
			 unsigned long long period,
			 std::vector<ResourceEntry> resources)
{
  unsigned long long offsetData = getDataAtTime(start % period,
						resources.front(),
						std::vector<ResourceEntry>(resources.begin() + 1,
									   resources.end())
						);
  if ( (data % resources.back().data) > (resources.back().data - offsetData) )
    { // (data % resources.back().data) will go through the end of the period
      return (data / resources.back().data) * period + (period - start%period) +
	getTimeAtData((data % resources.back().data) - (resources.back().data-offsetData),
		      resources.front(),
		      std::vector<ResourceEntry>(resources.begin() + 1, resources.end()));
    }
  else
    { // (data % resource.back().data) will not go through the end of the period
      return (data / resources.back().data) * period +
	getTimeAtData((data % resources.back().data) + offsetData,
		      resources.front(),
		      std::vector<ResourceEntry>(resources.begin() + 1, resources.end())) - start;
    }
}

unsigned long long getTimeAtData(unsigned long long data,
				 ResourceEntry prev,
				 std::vector<ResourceEntry> resources)
{
  if (prev.data <= data and resources[0].data >= data)
    return resources[0].time + (data - prev.data) / resources[0].bandwidth;
  else if (prev.data > data)
    return resources[0].time - (prev.data - data) / prev.bandwidth;
  else
    return getTimeAtData(data,
			 resources[0],
			 std::vector<ResourceEntry>(
						    resources.begin() + 1,
						    resources.end()
						    )
			 );
}

unsigned long long getDataAtTime(unsigned long long time,
				 ResourceEntry prev, std::vector<ResourceEntry> resources)
{
  if (prev.time <= time and resources[0].time >= time)
    return prev.data - prev.bandwidth * (resources[0].time - time);
  else
    return getDataAtTime(time,
			 resources[0],
			 std::vector<ResourceEntry>(
						    resources.begin() + 1,
						    resources.end()
						    )
			 );
}

int main(int argc, char** argv)
{
  std::vector<ResourceEntry> resources;
  resources.push_back( ResourceEntry(0000000, 90,   90000000) );
  resources.push_back( ResourceEntry(1000000, 87,  177000000) );
  resources.push_back( ResourceEntry(2000000, 94,  271000000) );
  resources.push_back( ResourceEntry(3000000, 100, 371000000) );
  resources.push_back( ResourceEntry(4000000, 90,  461000000) );
  resources.push_back( ResourceEntry(5000000, 110, 571000000) );
  resources.push_back( ResourceEntry(6000000, 120, 691000000) );
  resources.push_back( ResourceEntry(7000000, 0,   691000000) );
  resources.push_back( ResourceEntry(8000000, 0,   691000000) );
  resources.push_back( ResourceEntry(9000000, 0,   691000000) );

  unsigned long long delay;
  unsigned long long start = 500000, data = 100;
  for (int i=0; i < argc; i++)
    {
      if (!strcmp(argv[i], "--start"))
	start = atol(argv[i+1]);
      if (!strcmp(argv[i], "--data"))
	data = atol(argv[i+1]);
    }
  delay = Delay(data, start, 9000000, resources);
  unsigned long long end = delay + start;
  std::cout << "Start: " << start << std::endl;
  std::cout << "Data:  " << data << std::endl;
  std::cout << "Delay: " << delay << std::endl;
  std::cout << "End:   " << end << std::endl;
  return 0;
}
