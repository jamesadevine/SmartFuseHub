import serial
import struct
import time
import datetime
from serial_decoder_test import serial_decoder

class serial_listener(object):
  def __init__(self,logger):
    self.ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)
    self.logger = logger

  def listen(self):
    count = 0
    #8:4 hamming coding... which means for every 4 bits, 8 are produced.
    dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    transmissonFlag = False
    last_received=datetime.datetime.now()
    try:
      while True:
        read = self.ser.read()
        value = struct.unpack('B',read)[0]
        print str(value)
        if value == 85 and transmissonFlag == False:
          print 'flag set'
          transmissonFlag=True
          last_received = datetime.datetime.now()
        while transmissonFlag and (datetime.datetime.now().microsecond - last_received.microsecond < 10000):
          print 'in loop'
          read = self.ser.read()
          value = struct.unpack('B',read)[0]
          dataList[count] = value
          count+=1
          last_received = datetime.datetime.now()
          if(count==14):
            print 'starting serial decoder '+str(dataList)
            decoder = serial_decoder(dataList)
            decoder.daemon = True
            decoder.start()
            dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            count=0
            transmissonFlag = False
        else:
          print 'resetting'
          dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
          count=0
          transmissonFlag = False
        time.sleep(0)
    except Exception as e:
      print e
      self.ser.close()  