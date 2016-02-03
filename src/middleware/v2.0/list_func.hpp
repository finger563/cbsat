// note: timespec here is whatever representation you have in your
// CPN; this could be integer or whatever, but it must support
// modulus. and should be able to store floating point values or
// handle conversion from floaint point.
double Delay(INTEGER dataLenBits,
	     TIMESPEC sentTime,
	     TIMESPEC period,
	     LIST resources) {
  // expects a size of data, a current time, and a profile defintion
  // profile has a period (unsigned long in this case I suppose)
  // profile has a resources list, where each resource has an
  // associated time, bandwidth, and data value; the data in an entry
  // is the data at the **end** of the entry

  TIMESPEC offset = sentTime % period;

  // Need to find what the bandwidth, start, and start_data are for
  // the current profile interval.

  // The start is a the latest time point in the profile that is less
  // than the current time.

  // The start_data is the amount of data that has been sent
  // (according to the profile!) by the start time of the current
  // interval.  this corresponds to the data value of the previous
  // interval.

  // The bandwidth is the current interval's bandwidth; it is constant
  // from the start time of the current interval until the start time
  // of the next interval.
  TIMESPEC start = resources.back().time;
  INTEGER offsetData = resources.back().data;
  INTEGER bandwidth = resources.back().bandwidth;
  int res_id = resources.size() - 1;
  for (int i=0;i<resources.size();i++) {
    if ( resources[i].time > offset ) {
      res_id = i;
      start = resources[i-1].time;
      bandwidth = resources[i-1].bandwidth;
      offsetData = resources[i-1].data;
      break;
    }
  }

  // offsetData is the actual amount of data that has been sent
  // (according to the profile!) by sentTime
  offsetData += (INTEGER)((double)(offset-start)*((double)bandwidth));

  // Now that we know exactly where (time, data) = (sentTime,
  // offsetData) in the profile we are, we need to figure out exactly
  // how long it will take us to send the data

  // timeDiff is an accumulator which contains the amount of time it
  // will take to send the data.  It is the time difference between
  // sentTime and when the last bit of data will have been sent.
  TIMESPEC timeDiff = 0;

  // dataInPeriod is the total amount of data that can have been sent
  // by the end of the period
  INTEGER dataInPeriod = resources.back().data;
  
  INTEGER numPeriods = dataLenBits / dataInPeriod;
  if ( numPeriods > 0 ) { // will take more than numPeriods to send data
    timeDiff += (TIMESPEC)(numPeriods * period);
  }

  // dataToEnd is the amount of data that can be sent before the end
  // of the period
  INTEGER dataToEnd = dataInPeriod - offsetData;
  // modData is the amount of data that has to be sent in the last
  // period of transmission; this may be the first/only period if the
  // data is smaller than one period's worth of data.
  INTEGER modData = dataLenBits % dataInPeriod;
  if ( dataToEnd < modData ) { // will have to cycle back to beginning to send data
    timeDiff += period - offset;
    offsetData = 0;
    offset = 0;
    res_id = 0;
    modData = modData - dataToEnd;
  }

  // This code works for all cases; It simply takes the modData (which
  // is the actual amount of data which will be sent now that the
  // periodicity has been taken into account) and the current resource
  // ID (res_id) and iterates through the profile accumulating into timeDiff
  INTEGER remainder = modData;
  if ( (resources[res_id].data - offsetData) <= modData ) {
    remainder = modData - (resources[res_id].data - offsetData);
    timeDiff += resources[res_id++].time - offset;
    while ( (resources[res_id].data - offsetData) < modData ) {
      remainder = modData - (resources[res_id].data - offsetData);
      timeDiff += resources[res_id].time - resources[res_id-1].time;
      res_id++;
    }
  }
  res_id--;

  // By this point, we've taken care of every complete interval if any
  // exist.  now we take care of the remainder data that is left over
  // after the most recent complete interval.
  timeDiff += (TIMESPEC) (double)remainder / (double)resources[res_id].bandwidth;

  return timeDiff;
}
