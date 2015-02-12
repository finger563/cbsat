'''
Questions:
 * what are the semantics for putting data into the buffer?
 	* lump/burst (i.e. instantaneous datablock)
 	* rate (bps/Bps)
 * what are the semantics for emptying the buffers?
 	* lump/burst (i.e. instantaneous datablock)
 	* rate (bps/Bps)
 * what are the interesting measurements to make?
 	* sizes of each buffer (as function of time?)
 	* latency for each datum?
 	* buffer entry/exit for each datum?
 	* max latency
 	* max buffer size (app, NIC)
'''

'''
Design:
  * Server is kernel thread:
  	* acquires lock on NIC buffer
  	* acquires lock on actor buffer
  	* moves some amount of data from app buffer to NIC buffer
  	* releases lock on both buffers
  	* (waits?)
  * Client is an actor thread:
  	* acquires lock on actor buffer
  	* inserts data (dataSize) into buffer according to required profile
  	* releases lock on actor buffer
  	* waits for amount of time equal to dataSize:profile
  * NIC is a network interface thread:
  	* contains its own internal buffer to store sent items
  	* grabs lock on NIC buffer
  	* moves some amount of data from NIC buffer to internal buffer
  	* releases lock on NIC buffer
  * Node contains:
  	* some number of actors
  	* some number of servers
  	* one NIC per interface
  	* one buffer per NIC
  	* one buffer per actor
'''

import sys, os, csv, copy, glob, time, calendar
from networkProfile import *
from multiprocessing import Queue, Process, Pool, Pipe, Manager, Lock
from datetime import datetime

class Data:
	def __init__(self, size = 0, parent = -1, interface = None):
		self.size = size			# amount of data
		self.interface = interface 	# Interface to be sent out on
		self.parent = parent		# parent process who sent the data (useful for graphs)
		self.time = []				# timestamp list for each buffer entry/exit
		self.latency = 0			# calculated after transmission := <sent buffer entry> - <app buffer entry>
		return

	def timeStamp(self):
		self.time.append(time.time())
		return
		
class DataBuffer:
	def __init__(self):
		self.size = 0
		self.numEntries = 0
		self.data = []
		self.lock = Lock()
		return

	def lock():
		self.lock.acquire()
		return

	def unlock():
		self.lock.release()
		return

	def push(self,data):
		data.timeStamp()
		self.size += data.size
		self.numEntries += 1
		self.data.insert(0,data)
		return

	def pop(self):
		item = None
		if self.numEntries > 0:
			item = self.data.pop()
			item.timeStamp()
			self.numEntries = self.numEntries - 1
			self.size = self.size - item.size
		return item

class Server:
	def __init__(self, profile = []):
		self.profile = profile
		return

	def run(appBuffers, nicBuffers):
		for app,appBuffer in appBuffers.iteritems():
			data = None
			appBuffer.lock()
			data = appBuffer.pop()
			appBuffer.unlock()
		return

class Client:
	def __init__(self, profile = []):
		self.profile = profile
		return

	def run(lock, buffer):
		data = Data(size=dataSize, parent=self, interface=inft)
		buffer.lock()
		buffer.push(data)
		buffer.unlock()
		return

class NIC:
	def __init__(self, profile = []):
		self.profile = profile
		self.buffer = DataBuffer()
		self.bufferSize = 0
		return

	def run(buffer):
		data = None
		buffer.lock()
		if buffer.numEntries > 0:
			data = buffer.pop()
		buffer.unlock()
		self.buffer.push(data)
		return

class Node:
	def __init__(self, clients = [], servers = [], NICs = []):
		self.clients = clients
		self.servers = servers
		self.NICs = NICs
		self.appBuffers = {}
		self.nicBuffers = {}
		self.time = 0
		for client in clients:
			self.appBuffers[client] = DataBuffer()
		for nic in NICs:
			self.nicBuffers[nic] = DataBuffer()
		return

	def start():
		pids = []
		for nic in self.NICs:
			p = Process(target=nic.run, args=(self.nicBuffers[nic])).start()
			pids.append(p)
		for server in self.servers:
			p = Process(target=server.run, args=(self.appBuffers, self.nicBuffers)).start()
			pids.append(p)
		for client in self.clients:
			p = Process(target=client.run, args=(self.appBuffers[client])).start()
			pids.append(p)
		return
