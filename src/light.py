import time
import json
import math
import urllib
import argparse
from blinkstick import blinkstick

class Service:

	lights = None
	programReader = None

	tn = None
	
	transition = None
	step = None
	
	PUPDATE = 10 #Program update period
	PCL = 0.1 #Control loop period
	
	def __init__(self,reader,n,pupdate=None,pcl=None):
		self.lights = []
		for i in range(n):
			self.lights.append(Light(blinkstick.find_first()))
		self.programReader = reader
		if pupdate:
			self.PUPDATE = pupdate
		if pcl:
			self.PCL = pcl

	def controlLoop(self):
		tupdate = None
		while True:
			t = time.time()
			if(tupdate is None or t - self.PUPDATE > tupdate):
				self.updateProgram()
				tupdate = t
	
			self.updateLights()		
			tsleep = max(self.PCL - time.time() + t,0)
			time.sleep(tsleep)
	
	def updateLights(self):
		
		t = time.time()
		
		if(self.tn == None):
			d = 0
			self.tn = t
		else:
			d = t - self.tn
			if(d > self.step):
				self.tn = t
				d = 0
				for light in self.lights:
					light.cs.incr()
		f = d/self.step
		for light in self.lights:
			light.update(f,self.transition)
	
	def updateProgram(self):
		if(self.programReader.readProgram()):
			self.transition = self.programReader.getTransition()
			self.step = self.programReader.getStep()
			self.tn = None
			for i in range(len(self.lights)):
				sequence = self.programReader.getSequence(i)
				self.lights[i].cs = ColourState(sequence)
				
		
class ProgramReader:
	
	programHash = None
	program = None
	filename = None
	
	"""
	Assume program format
	{
		"step" : 5.0,
		"transition": "LINEAR",
		"sequences": [
			[[255,255,255],[0,0,0]]
		]
	}
	"""
	
	def __init__(self,filename):
		self.filename = filename
	
	def readProgram(self):
		
		programS = self.readProgramString()
		programHash = hash(programS)
		if(programHash == self.programHash):
			return False
		else:
			self.programHash = programHash
			self.program = json.loads(programS)
			return True
	
	def readProgramString(self):
		f = urllib.urlopen(self.filename)
		programS = f.read()
		f.close()
		return programS

	def getTransition(self):
		return self.program["transition"]
	
	def getStep(self):
		return self.program["step"]
	
	def getSequence(self,i):
		if(len(self.program["sequences"]) > i):
			return self.program["sequences"][i]
		else:
			return [[0,0,0]]

class Light:
	
	cs = None
	bs = None
	
	def __init__(self,bs):
		self.bs = bs

	def update(self,f,transition):
		updateColour = self.genUpdateColour(f,transition,self.cs.current(),self.cs.next())
		self.bs.set_color(red=updateColour[0],blue=updateColour[1],green=updateColour[2])
	
	def genUpdateColour(self,f,transition,current,next):
		if transition == "LINEAR":
			updateColour = [int(current[i]*(1.0-f)+next[i]*f) for i in range(3)]
			return updateColour
		if transition == "SIN":
			x = (math.cos(f*math.pi)+1)/2
			updateColour = [int(current[i]*x+next[i]*(1.0-x)) for i in range(3)]
			return updateColour
		return current

class ColourState:
	
	i = 0
	sequence = None
	
	def __init__(self,sequence):
		self.sequence = sequence
	
	def current(self):
		return self.sequence[self.i]
	
	def next(self):
		if(len(self.sequence)-1 > self.i):
			return self.sequence[self.i+1]
		else:
			return self.sequence[0]
		
	def incr(self):
		self.i+=1
		if(self.i>=len(self.sequence)):
			self.i = 0

def main():
	parser = argparse.ArgumentParser(description='A blinkstick service.')
	parser.add_argument('--nlights', '-n', dest='nlights', nargs=1, type=int,
	                   default=1, help='number of blinksticks (default: 1)')
	parser.add_argument('--period', '-p', dest='period', nargs=1, type=float,
	                   default=0.1, help='period of the main control loop in s (default: 0.1)')
	parser.add_argument('--refresh', '-r', dest='refresh', nargs=1, type=float,
						default=0.1, help='program refresh period in s (default: 10)')
	parser.add_argument('--file', '-f', dest='file', nargs=1, required=True,
						help='the file of url to read the program from')

	args = parser.parse_args()
	
	reader = ProgramReader(args.file[0])
	service = Service(reader,args.nlights,pupdate=args.refresh,pcl=args.period)
	service.controlLoop()

if __name__ == '__main__':
	main()
