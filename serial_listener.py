import serial
import struct
import time
import datetime
from serial_decoder import serial_decoder

class serial_listener(object):
  def __init__(self,networker):
    #baud is usually 9600
    self.ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)
    self.networker = networker

  """
    Listens for packets on the serial line
  """
  def listen(self):
    count = 0
    #8:4 hamming coding... which means for every 4 bits, 8 are produced meaning 14 bytes.
    dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    transmissionFlag = False
    last_received=datetime.datetime.now()
    packet_count = 0
    try:
      while True:
        read = self.ser.read()
        value = struct.unpack('B',read)[0]
        #check to see if we have seend a start byte and we aren't currently receiving...
        if value == 85 and transmissionFlag == False:
          #add to packet count
          packet_count+=1
          #set receiving...
          transmissionFlag=True
          #set last_received...
          last_received = datetime.datetime.now()
        #after transmissionflag has been set, spin until we either timeout or have received a complete packet
        while transmissionFlag and (datetime.datetime.now().microsecond - last_received.microsecond < 1000):
          read = self.ser.read()
          value = struct.unpack('B',read)[0]
          dataList[count] = value
          count+=1
          #update last_received
          last_received = datetime.datetime.now()
          #if we have received a whole 'packet', decode it and log the results...
          if(count==14):
            print str(dataList)
            decoder = serial_decoder(self.networker,dataList)
            decoder.daemon = True
            decoder.start()
            transmissionFlag = False
        else:
          print 'Finished receiving packet'
          #log an error with the packet
          if transmissionFlag:
            print 'packet lost'
          #reset
          dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
          count=0
          transmissionFlag = False
        #allow the processor to process other stuff...
        time.sleep(0)
    except Exception as e:
      print str(e)
      #don't forget to close serial!
      self.ser.close()  