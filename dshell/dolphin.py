#!/usr/bin/python
from __future__ import print_function
from socket import socket, AF_INET, SOCK_STREAM,   SHUT_RDWR
from socket import error as socket_error
import sys
import threading
import cmd
import json
import Queue

import logging

PCMLOG_OFFSET=2

class dolphin:
    def __init__(self, ip='localhost', basePort=17000): 
        logging.info("Dolphin Init Called")        
        self.pcmioport  = basePort+3
        self.pcmlogport = basePort+2
        self.dataport   = basePort+1
        self.cmdport    = basePort
        self.quiet = 0
        logging.info("Opening Command Socket")
        self.cmdsocket=socket(AF_INET, SOCK_STREAM)
        self.cmdsocket.connect((ip, basePort))
        self.cmdsocket.settimeout(20)

        self.SampFreq = 102400        
        self.pcmlogsocket = 0
        self.recByteCount = 0
        self.ip = ip
        self.is_running = True
        self.fp = None;
        self.fileLock = threading.Lock()
        logging.info("Starting Command Thread")
        self.rxThread = threading.Thread(target=self.RxCmdLoop, name="CmdRxLoop")
        self.rxThread.start();
        self.replyQ = Queue.Queue()

        logging.info("Starting pcmThread")
        self.pcmThread = threading.Thread(target=self.recPcmLoop, name="PCMRxLoop")
        self.pcmThread.start();
        self.intParams = {}
        self.floatParams = {}
    
        self.getAllParameters()
    
    def RxCmdLoop(self):
        errorcount = 0
        rxString = ''
        self.cmdsocket.settimeout(1)
        while(self.is_running ==True):
            try:
                data = self.cmdsocket.recv(1)
                if(len(data) >= 1):

                    if ord(data)  != 13:
                        rxString = rxString+str(data);
                     
                    else:
                        
                        idx = rxString.find("{")
                        msgType = rxString[0:idx]
                        msgType = msgType.strip();

                        jsonData = rxString[idx:len(rxString)]
                        try:
                            reply = json.loads(jsonData)
                            self.replyQ.put(reply)
                        except:
                            print("Unparseable JSON message " + jsonData)
                        print("\033[1m"+str(jsonData)+"\033[0m")
                        logging.info(str(jsonData))
                        rxString = ''
            
            except socket_error  as s_err:
                errorcount = errorcount +1 
        print("exiting RxCmd")
    def exit(self):
        print ("Stub for exit routine")
  #      self.is_running = False

   #     self.rxThread.join()
    #    self.pcmThread.join()
    def send(self, message):
        args =message.split(' ',1)

        if len(args) > 1:
            command = args[0]
            arguments = args[1]
        else:
            command = message
            arguments = "Unused Arguments"

        message = "{ \"Command\": \"" + command + "\", \"Arguments\": \""+arguments + "\"}"

        self.cmdsocket.sendall(message + '\n')
      
    def receive(self):
        data = self.cmdsocket.recv(256)

    def close(self):
        self.cmdsocket.close() 

    def settimeout(self, timeout):
        self.cmdsocket.settimeout(timeout)

    def sendPing(self, power=.1):
        self.setValueF('TxPowerWatts', power)
        self.setValueI('CarrierTxMode', 0)
        self.send('Event_sendTestPacket')

    def startRx(self):
        self.send('Event_StartRx')

   
    def calibrate(self):
        self.setValueF('TxPowerWatts', 1)
 
        self.send('Event_startTxCal')

    def version(self):
        self.send('GetVersion')

    def sendRange(self, power=.1):
        self.setValueF('TxPowerWatts', power)
        self.setValueI('CarrierTxMode', 0)
        self.send('Event_sendRanging')
    
    def recordStartTarget(self,filename):
        self.send('StartRecording {}'.format(filename))
    def recordStopTarget(self):
        self.send('StopRecording')          

    def recordStart(self, filename):
        with self.fileLock:
            self.fp = open(filename, 'w')
            self.recByteCount = 0;
        
        if(self.fp is not None):
            print('Record Started for Filename {}'.format(filename))

    def recordStop(self):
        #self.send('StopRecording')
        with self.fileLock:
            self.fp.close()
            self.fp = None
            print('Record Stopped {} bytes Recorded'.format( self.recByteCount) )
       
    
    def getInbandEnergy(self):
        self.getValueF('GetInbandEnergy')



    def setGainMode(self, value=2):
        self.setValueI('GainAdjustMode', value)

    def setValueI(self, Element, value):
        self.send('SetValue {} int {} 0'.format(Element, value))        

    def setValueF(self, Element, value):
        self.send('SetValue {} float {} 0'.format(Element, value))        

    def getValueI(self, Element):
        self.send('GetValue {} int  0'.format(Element))        

    def getValueF(self, Element):
        self.send('GetValue {} float  0'.format(Element))        

    def getParameter(self, idx):
        self.send('GetParameters {}'.format(idx))        
    

    def getAllParameters(self):
        idx = 0;
        try:
            while idx >= 0:
                self.getParameter(idx)
                reply = self.replyQ.get(True, 3)    
                if reply:    
                    if "Element" in reply:
                        El = reply['Element']
                        if 'nextidx' in El:
                            idx = int(El['nextidx'])
                        if  int(El['nextidx'])  > 0:
                            if (El['Format'] == 'int'):
                                self.intParams[El['Name']] = El
                            else:
                                self.floatParams[El['Name']] = El
                    print(reply)
                else:
                    print("GetParameter Timeout")

                    idx = -1
        except Exception, a:
            print(a)
            return

    def __del__(self):
        done = 0;

        # Read all data out of socket
        self.is_running =0


    def recPcmLoop(self):
        # Record passband pcm for duration seconds.  This function also
        # returns a vector of timestamps in pcmCount and a vector of
        # HiGain_LowGain flags 0=lo,1=hi which indicate which A/D
        # channel was selected on a frame basis
        self.pcmlogsocket=socket(AF_INET, SOCK_STREAM)
        self.pcmlogsocket.connect((self.ip, self.pcmlogport))
        self.pcmlogsocket.settimeout(1)
        while (self.is_running == True):
            # Read socket
            try:
                fromRx=self.pcmlogsocket.recv(8192);
                with self.fileLock:
                    if self.fp != None:
                        self.fp.write(fromRx)
                        self.recByteCount = self.recByteCount + len(fromRx);
            except:
                continue

        print("Exiting PCM Loop")




if __name__ == '__main__':
    mt = dolphin()
    mt.sendRange()

   
