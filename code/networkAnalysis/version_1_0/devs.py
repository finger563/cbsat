'''
Design:
  * Data:
  	* size
  	* timestamp list
  	* destination
  * Buffer:
  	* list of data objects
  	* output profile
  	* size
  	* max size ( > 0 => enforcement )
  * Event:
  	* time
  	* action:
		* data = inBuffer.popData()
		* data.timestamps.append(time)
		* eventList = outBuffer.pushData(data)
	* objects (at least one is required)
		* inBuffer
		* outBuffer
'''

from networkProfile import *

EPSILON = 0.000001

class Data:
	def __init__(self, size = 0, parent = None, interface = None):
		self.size = size			# amount of data
		self.interface = interface 	# Interface to be sent out on
		self.parent = parent		# parent process who sent the data (useful for graphs)
		self.times = []				# timestamp list for each buffer entry/exit
		self.latency = 0			# calculated after transmission := <sent buffer entry> - <app buffer entry>
		return

	def __repr__(self):
		return "Data()"

	def __str__(self):
		retStr = "Data:\n"
		retStr += "size = {0}\n".format(self.size)
		retStr += "time stamps = {0}\n".format(self.times)
		return retStr

	def timeStamp(self,time):
		self.times.append(time)
		if len(self.times) > 0:
			self.latency = time - self.times[0]
		return

class DataBuffer:
	def __init__(self, capacity=0, unitSize=1, inProfile=[], outProfile=[], next=None, name="DataBuffer()"):
		self.unitSize = unitSize
		self.capacity = capacity
		self.inProfile = inProfile
		self.outProfile = outProfile
		self.next = next
		self.name = name
		self.buffer = []
		self.size = 0
		self.maxSize = 0
		self.pushTime = 0
		self.popTime = self.getNextPopTime(0,self.unitSize)
		return

	def __repr__(self):
		return self.name

	def __str__(self):
		retStr = "{0} (DataBuffer):\n\t[".format(self.name)
		retStr += "size = {0}".format(self.size)
		retStr += ", max size = {0}".format(self.maxSize)
		retStr += ", bits per unit = {0}".format(self.unitSize)
		retStr += "]\n"
		return retStr

	def addData(self,data):
		self.buffer.append(data)
		self.size += data.size
		if len(self.buffer) > 1:
			if self.size > self.maxSize:
				self.maxSize = self.size
		return

	def fillFromOutProfile(self):
		if self.outProfile != []:
			bufferedData = 0
			totalData = self.outProfile[-1].data
			remainingData = totalData
			while remainingData > 0:
				size = 0
				if remainingData > self.unitSize:
					size = self.unitSize
				else:
					size = remainingData
				newData = Data(size,parent=self.name)
				remainingData = remainingData - size
				self.addData(newData)
		return

	def getNextPopTime(self,time,size):
		nextTime = None
		if self.outProfile != []:
			i = 0
			while i < len(self.outProfile) and self.outProfile[i].start <= time:
				i += 1
			i = i - 1
			sentData = 0
			if i > 0:
				sentData = self.outProfile[i-1].data 
			sentData += int((self.outProfile[i].bandwidth*1.0)*(time*1.0 - self.outProfile[i].start*1.0))
			finalData = sentData + size
			#print time,size,i,sentData,finalData,self.outProfile[-1].data,self.name
			if round(self.outProfile[-1].data - finalData) >= 0:
				if round(self.outProfile[i].data-finalData) >=0:
					nextTime = (size*1.0)/(self.outProfile[i].bandwidth*1.0) + time
				else:
					while i < len(self.outProfile) and self.outProfile[i].data < finalData:
						i += 1
					remainingData = finalData - self.outProfile[i-1].data
					nextTime = self.outProfile[i].start + (remainingData*1.0)/(self.outProfile[i].bandwidth*1.0)
		else:
			nextTime = time
		return nextTime

	def popData(self,time):
		nextTime = None
		data = None
		if self.size > 0:
			if time >= self.popTime:
				nextTime = self.getNextPopTime(time,self.buffer[0].size)
				self.popTime = nextTime
				data = self.buffer.pop(0)
				self.size = self.size - data.size
			else:
				nextTime = self.popTime
		return data, nextTime

	def pushData(self,time,data):
		if self.inProfile == []:
			self.addData(data)
		else:
			if time < self.pushTime:
				return
			if self.maxSize == 0 or self.maxSize >= (self.size + data.size):
				if self.unitSize > 0 and data.size > self.unitSize:
					bitsRemaining = data.size
					while bitsRemaining > 0:
						newData = copy.deepcopy(data)
						if bitsRemaining > self.unitSize:
							newData.size = self.unitSize
						else:
							newData.size = bitsRemaining
						bitsRemaining = bitsRemaining - newData.size
						self.addData(newData)
				else:
					self.addData(data)
			for i in range(0,len(self.inProfile)):
				if self.inProfile[i].start > time:
					break
			i = i - 1
			sentData = 0
			if i > 0:
				sentData = self.inProfile[i-1].data + self.inProfile[i].bandwidth*(time*1.0 - self.inProfile[i].start)
			finalData = sentData + data.size
			if finalData < self.inProfile[i].data:
				self.pushTime = (data.size*1.0)/(self.inProfile[i].bandwidth*1.0) + time
			else:
				for j in range(i,len(self.inProfile)):
					if self.inProfile[j].data > finalData:
						break
				j = j - 1
				remainingData = finalData - self.inProfile[j-1].data
				self.pushTime = self.inProfile[j].start + (remainingData*1.0)/(self.inProfile[j].bandwidth*1.0)
		return

	def maxLatency(self):
		latency = 0
		for d in self.buffer:
			if d.latency > latency:
				latency = d.latency
		return latency

	def hasNoEvents(self):
		return (self.size == 0 and self.next != None)

class Event:
	def __init__(self, time=-1, inBuffer=[], outBuffer=[]):
		self.time = time
		self.inBuffer = inBuffer
		self.outBuffer = outBuffer
		return

	def __lt__(self, other):
		return self.time < other.time

	def __repr__(self):
		return "Event()"

	def __str__(self):
		retStr = "Event:\n\t["
		retStr += "time = {0}".format(self.time)
		retStr += ", "+repr(self.inBuffer)
		retStr += ", "+repr(self.outBuffer)
		retStr += "]\n"
		return retStr

	def action(self):
		eventList = []
		data, nextTime = self.inBuffer.popData(self.time)
		if nextTime != None:
			newEvent = Event(nextTime,self.inBuffer,self.outBuffer)
			eventList.append(newEvent)
		if data != None:
			data.timeStamp(self.time)
			if self.outBuffer != None:
				if self.outBuffer.hasNoEvents():
					newEvent = Event(self.time,self.outBuffer,self.outBuffer.next)
					eventList.append(newEvent)
				self.outBuffer.pushData(self.time,data)
		return eventList

class DEVS:
	def __init__(self, buffers=[]):
		self.events = []
		self.buffers = buffers
		return

	def __repr__(self):
		return "DEVS()"

	def __str__(self):
		retStr = "DEVS:\n"
		for e in self.events:
			retStr += "{0}".format(e)
		return retStr

	def setup(self):
		for b in self.buffers:
			if b.size > 0:
				newEvent = Event(0,b,b.next)
				self.events.append(newEvent)

	def step(self):
		event = self.events.pop(0)
		newEvents = event.action()
		if newEvents != None:
			for e in newEvents:
				self.events.append(e)
			self.events = sorted(self.events)
		return

	def run(self):
		while len(self.events) > 0:
			self.step()
		return

