import serial
import struct
import time
import datetime
from serial_decoder_test import serial_decoder
import os.path
import logging

class serial_listener(object):
  def __init__(self,baud,cable_length, packet_amount):
    #baud is usually 9600
    self.ser = serial.Serial("/dev/ttyAMA0", baudrate=baud)
    self.baud = baud
    self.cable_length = cable_length
    self.packet_amount = packet_amount

    #create test results file...
    test_count = 1

    listener_prefix = 'listener_'+str(baud)+'_'+str(cable_length).replace('.','_')+'_'

    while os.path.isfile("./logs/"+listener_prefix + str(test_count)+'.csv'):
      test_count += 1

    self.test_count = test_count

    # create logger
    self.listener_logger = logging.getLogger('SmartFuse Listener Logger')
    self.listener_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG

    # add a file handler
    fh = logging.FileHandler("./logs/"+listener_prefix + str(test_count)+'.csv')
    fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

    # create a formatter and set the formatter for the handler.
    frmt = logging.Formatter('%(message)s')
    fh.setFormatter(frmt)

    # add the Handler to the logger
    self.listener_logger.addHandler(fh)

    self.listener_logger.debug('Time,Packet Number,Discarded') 
    frmt = logging.Formatter('%(asctime)s.%(msecs)d,%(message)s',"%H:%M:%S")
    fh.setFormatter(frmt)
    self.listener_logger.addHandler(fh)

    decoder_prefix = 'decoder_'+str(baud)+'_'+str(cable_length).replace('.','_')+'_'

    # create logger
    self.decoder_logger = logging.getLogger('SmartFuse Decoder Logger')
    self.decoder_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
    # add a file handler
    fh = logging.FileHandler("./logs/"+decoder_prefix + str(test_count)+'.csv')
    fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

    # create a formatter and set the formatter for the handler.
    frmt = logging.Formatter('%(message)s')
    fh.setFormatter(frmt)

    # add the Handler to the logger
    self.decoder_logger.addHandler(fh)

    self.decoder_logger.debug('Time,Packet Number,Bit Error,Discarded,Reason,Details') 
    frmt = logging.Formatter('%(asctime)s.%(msecs)d,%(message)s',"%H:%M:%S")
    fh.setFormatter(frmt)
    self.decoder_logger.addHandler(fh)

  def listen(self):
    count = 0
    #8:4 hamming coding... which means for every 4 bits, 8 are produced meaning 14 bytes.
    dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    transmissionFlag = False
    last_received=datetime.datetime.now()
    packet_count = 1
    lost = 0
    try:
      while packet_count<self.packet_amount+1:
        read = self.ser.read()
        value = struct.unpack('B',read)[0]
        #check to see if we have seend a start byte and we aren't currently receiving...
        if value == 85 and transmissionFlag == False:
          #set receiving...
          transmissionFlag=True
          #set last_received...
          last_received = datetime.datetime.now()
        #after transmissionflag has been set, spin until we either timeout or have received a complete packet
        while transmissionFlag and (datetime.datetime.now().microsecond - last_received.microsecond < 1500):
          read = self.ser.read()
          value = struct.unpack('B',read)[0]
          dataList[count] = value
          count+=1
          #update last_received
          last_received = datetime.datetime.now()
          #if we have received a whole 'packet', decode it and log the results...
          if(count==14):
            self.listener_logger.debug(str(packet_count)+',0') #zero for not discarded...
            decoder = serial_decoder(dataList,self.decoder_logger,packet_count,self.test_count)
            decoder.daemon = True
            decoder.start()
            transmissionFlag = False
        else:
          #log an error with the packet
          if transmissionFlag:
            lost+=1
            self.listener_logger.debug(str(packet_count)+',1') #one for discarded...
          print 'Packet: '+str(packet_count)+' lost: '+str(lost)
          packet_count+=1
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