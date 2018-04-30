#!/usr/bin/python
import dolphin
import cmd2
import sys
import time

import logging

import logging.handlers

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(message)s" )



class dshell(cmd2.Cmd):
	def __init__(self):
		self.dol = None

		cmd2.Cmd.__init__(self)
		self.debug = True
		self.prompt = "Dolphin-> "
		self.intro = "Welcome to the Dolphin modem dshell.  Type help <return>  for a list of commands "
		self.carrier = 30000
		self.logger = logging.getLogger(__name__)


	def do_startrx(self, line):
		'''
		This function enables the modem  receiver
		'''
		self.dol.startRx()
	def do_connect(self, line):
		'''
			connect <ip> <base port>

			Establish a connection to the dolphin modem at ip:baseport
		'''
		args = line.split(' ')

		if not (self.dol == None):
			del(self.dol)

		self.dol = dolphin.dolphin(args[0], int(args[1]))
		print("Connected to " + line)

		fh = logging.handlers.RotatingFileHandler('dshell.log.'+args[0]+'.'+args[1], maxBytes=1000000, backupCount=10, encoding=None, delay=False)
		logger = logging.getLogger()
		logger.handlers=[]

		logger.addHandler(fh)

	def do_getinbandenergy(self, line):
		'''
			getinbandenergy:   Reports the energy value of baseband input
		'''
		self.dol.getInbandEnergy()

	def do_range(self, line):
		'''
			range <PowerScale>

			Sends a range request using the amplitude multiplier in PowerScale.   
				.05 < PowerScale < .7
				corresponds to XXX to YYY Watts 
		'''
		self.dol.sendRange(float(line), self.carrier)


	def do_sleep(self, line):
		time.sleep(int(line))

	def do_recordstart(self, line):
		'''
			recordstart <filename> [local]
			starts a recording over the streaming TCP interface.

			where filename is the name of the file to record

			if the local flag is set, then the file records on the same computer that is 
			running the dshell.   Otherwise the file records on the target processor

		'''
		args = line.split(" ")
		filename = args[0]

		if(len(args) > 1):
			if(args[1] == 'local'):
				self.dol.recordStart(filename)
				return
		print ("Sent record start command to Target")		
		self.dol.recordStartTarget(filename)
	
	def do_recordstop(self, line):
		''' 
		stop and close an in-process recording
		'''
		args = line.split(" ")

		if(len(args) >= 1):
			if(args[0] == 'local'):
				self.dol.recordStop() 
				print ("Sent record stop command to Target")
				return

		self.dol.recordStopTarget()


	def do_setgainmode(self, line):
		'''
			setGainMode <0,1,2>
				
				GainMode 0 = High Gain Only
				GainMode 1 = Low Gain Only
				GainMode 2 = Automatic Gain Selection

		'''
		self.dol.setGainMode(int(line))

	def do_setdetectthreshold(self, line):
		'''
			set the detection threshold in DB 
		'''
		self.dol.setValueF('FHDEMOD_DetectThresholdDB', float(line))


	def do_setvaluei(self, line):
		'''
			setvaluei  <Element>

			Sets an integer value on the dolphin modem

			setvaluef UPCONVERT_Carrier 30000
		'''
		args = line.split(" ")
		self.dol.setValueI(args[0], int(args[1]))


	def complete_setvaluei(self, text, line, begidx, endidx):
		if not text:
			completions = [f for f in sorted(self.dol.intParams)]
		else:
			completions = [f for f in sorted(self.dol.intParams) if f.startswith(text)]
		return completions	

	def do_setvaluef(self, line):
		'''
			setvaluef  <Element>

			Sets a float value on the dolphin modem

			setvaluef UPCONVERT_Carrier 30000
		'''
		args = line.split(" ")
		self.dol.setValueF(args[0], float(args[1]))

	def complete_setvaluef(self, text, line, begidx, endidx):

		if not text:
			completions = [f for f in sorted(self.dol.floatParams)]
		else:
			completions = [f for f in sorted(self.dol.floatParams) if f.startswith(text)]
		return completions
	def do_getvaluei(self, Element):
		'''
			getvaluei  <Element>

			Retrieves an integer value from the dolphin modem

			getvaluei UPCONVERT_Carrier
		'''
		self.dol.getValueI(Element)
	
	def complete_getvaluei(self, text, line, begidx, endidx):
		if not text:
			completions = [f for f in sorted(self.dol.intParams)]
		else:
			completions = [f for f in sorted(self.dol.intParams) if f.startswith(text)]
		return completions


	def do_getvaluef(self, Element):
		'''
			getvaluef  <Element>

			Retrieves an float value from the dolphin modem

			getvaluei UPCONVERT_Carrier
		'''
		self.dol.getValueF(Element)

	def complete_getvaluef(self, text, line, begidx, endidx):
		if not text:
			completions = [f for f in sorted(self.dol.floatParams)]
		else:
			completions = [f for f in sorted(self.dol.floatParams) if f.startswith(text)]
		return completions

	def do_enablemsmlog(self, line):
		'''
			Enables logging of Modem State machine transitions
		'''
		self.dol.send('EnableMSMLog')

	def do_disablemsmlog(self, line):
		'''
			Enables logging of Moem State machine transitions
		'''
		self.dol.send('DisableMSMLog 0  ')

	def do_calibrate(self, line):
		self.dol.calibrate();

	def do_ver(self, line):
		self.dol.version();

	def do_setpower(self,line):
		'''
			setpower <PowerScale>

			Sets the amplitude multiplier in PowerScale.   
				.05 < PowerScale < .5
				corresponds to XXX to YYY Watts 
		'''
		self.setValueF('UPCONVERT_OutputScale', float(line))

	def do_npings(self,line):
		'''
			do_npings <count> 
		
			sends <count> pings at each power .1
		'''
		args = line.split(" ")
		if(args[0] <1):
			print 'first parameter is the ping count'
		else:

			for p in [0]:
				for x in range(1,int(args[0])):
					self.dol.sendPing(float(p))
					time.sleep(8.)

	def do_setcarrier25(self, line):
		'''
		Sets the modem carrier to 25 Khz
		'''
		self.dol.setValueI("UPCONVERT_Carrier", 25000)
		self.dol.setValueI("DOWNCONVERT_Carrier", 25000)

	def do_setcarrier30(self, line):
		'''
		Sets the modem carrier to 30 Khz
		'''
		self.dol.setValueI("UPCONVERT_Carrier", 30000)
		self.dol.setValueI("DOWNCONVERT_Carrier", 30000)

	def do_longevity(self,line):
		'''
			do_longevity <count>  delay
		
			sends <count> pings at each power .1
		'''
		args = line.split(" ")
		if(args[0] <1):
			print 'first parameter is the ping count'
		else:
			for a in range (0, 100):
				for x in range(1,int(args[0])):
					self.dol.sendPing(0.4)
					time.sleep(8.)
					self.dol.getNoise()
					time.sleep(2)
				self.dol.sendRange(.4, self.carrier)

				time.sleep(int(args[1]))
	def do_rxtest(self, line):
		'''
		This function runs a receive test.   It opens a pcm file, initilizes a CRC Pass Counter
		and waits for ping commands.

		Hitting a key makes the function do_exit
		'''


	def do_ping(self, line):
		'''
			Sends a test message (Dolphin Test Message) using the amplitude multiplier in PowerScale.   
				.05 < PowerScale < .7
				corresponds to XXX to YYY Watts 
		'''
		self.dol.sendPing(float(line))

	def do_airping(self, line):
		args = line.split(" ")
		airpower = float(args[0])
		if(airpower >.1):
			print 'power exceeded !'
			airpower = .1
		self.dol.sendPing(airpower)

	def do_multiping(self, line):
		'''
			Use multiping <power Watts> <number of pings>  <delay in seconds>
		'''
		args = line.split(" ")
		airpower = float(args[0])
		nping = int(args[1])
		delays = float(args[2])
	
		if(airpower > 1):
			airpower = 1
		if(airpower < .01):
			airpower = .01
		if(nping > 50):
			nping = 50

		for i in range(1,nping + 1):
			self.dol.sendPing(airpower)
			time.sleep(delays)




	def  do_q(self, line):
		'''
		Quiet the output screen
		'''
		self.dol.quiet=1
	def do_unq(self, line):
		'''
		Unquiet the output screen
		'''
		self.dol.quiet = 0

	def do_quit(self, line):
		return self.do_exit(line)

	def do_exit(self, line):
		self.dol.is_running = False
		time.sleep(3)
		self._should_quit = True
		return self._STOP_AND_EXIT

	def preparse(self, raw):
		logging.info(self.prompt + " " + raw)
		return raw

if __name__ == '__main__':

	
	ds = dshell()

	ds.cmdloop()
