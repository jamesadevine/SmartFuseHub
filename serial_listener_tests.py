#import serial!!!!
import struct
import time
import threading

from smart_fuse_networker import smart_fuse_networker

class serial_listener(object):
  #def __init__(self,networker):
  def __init__(self):
    print 'init'
    #self.ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)!!!!
    #self.networker = networker!!!!
    #returns the incorrect bit for hamming code.
    self.truth_table_lookup = {
      (True,True,True):6,
      (True,True,False):4,
      (True,False,True):2,
      (False,True,True):0,
      (False,False,True):7,
      (False,True,False):5,
      (True,False,False):3,
      (False,False,False):1,
    }


  def output(self,valList):
    valList=self.convert_packet(valList)
    print str(valList)
    binaryString = ''.join('{0:08b}'.format(valList[i])[::-1] for i in range(len(valList)))
    binaryResult=binaryString
    id=int(binaryResult[0:12][::-1],2)
    sampleCount=int(binaryResult[12:24][::-1],2)
    totalVal=int(binaryResult[24:48][::-1],2)
    check_sum=int(binaryResult[48:56][::-1],2) 
    calculated_check_sum = self.calculate_checksum(valList)
    if calculated_check_sum != check_sum:
      raise Exception("Uncorrectable packet")
      return
    print "received checksum "+str(check_sum)+" calculated: "+str(calculated_check_sum)
    #ourCheckSum
    voltage = 0
    
    #line=[binaryResult[i:i+8] for i in range(0, len(binaryResult), 8)]
    if sampleCount>0:
      voltage = float((float(5000/4095)*(float(totalVal)/float(sampleCount)))/1000)

    #self.networker.sendFuseData(voltage,id) !!!!

  def calculate_checksum(self,values):
    checksum = 0
    for i in range(0,len(values)):
      checksum += values[i]
      if checksum>255:
        checksum = checksum-255
    return checksum


  def convert_packet(self, values):
    newValues = [0,0,0,0,0,0,0]
    valCount=0;
    for i in range(0,len(values),2):
      temp = self.transpose(values[i+1])+self.transpose(values[i])
      print 'binary string: '+temp
      newValues[valCount] = int(temp,2)
      valCount+=1
    return newValues

  def transpose(self, value):
    #parity for the byte - True indicates 0 or 2 errors.
    parity = self.calculate_parity(value,6,1,self.get_bit(value,7))

    #if one check is incorrect, it is recoverable, otherwise we have to discard the packet...
    check1 = self.calculate_parity_specific(value,[7, 5, 1, 0])
    check2 = self.calculate_parity_specific(value,[7, 3, 2, 1])
    check3 = self.calculate_parity_specific(value,[5, 4, 3, 1])
    print 'current value: '+str(value)
    print 'overall '+str(parity)
    print 'check1 '+str(check1)
    print 'check2 '+str(check2)
    print 'check3 '+str(check3)

    #one bit error which can be corrected
    if not parity:
      if self.is_correctable(check1,check2,check3):
        #determine which bit is wrong!
        incorrect_index = self.truth_table_lookup[(check1,check2,check3)]
        #correct the value...
        value = self.toggle_bit(value,incorrect_index)
        print 'incorrect index: '+str(incorrect_index)
        print 'new val = '+str(value)
      else:
        #raise the exception to terminate the thread...
        raise Exception("Uncorrectable packet")
        return

    value = self.get_nibble(value)

    print 'actual value '+str(value)
    return value

  def is_correctable(self, a, b, c):
    return True if (a and (b or c)) or (b and c) else False

  def get_nibble(self,value):
    return ''.join('{0:0b}'.format(int(self.get_bit(value,i)))for i in range(7,0,-2) )

  #recursive function to calculate parity for a byte using hamming code
  def calculate_parity(self,value,index,step,result):
    if index == 0:
      return result ^ self.get_bit(value,0)
    elif index<0:
      return result
    else:
      return self.calculate_parity(value,index-step,step,result^self.get_bit(value,index)) 

  def calculate_parity_specific(self,value,indexesToCheck):
    parity = self.get_bit(value,indexesToCheck[0])
    for i in range(1,len(indexesToCheck)):
      parity = parity ^ self.get_bit(value,indexesToCheck[i])
    return parity

  def get_bit(self,byte,index):
    return ((byte&(1<<index))!=0);

  def toggle_bit(self,byte,index):
    return byte^(1<<index);

  def listen(self):
    count = 0
    #8:4 hamming coding... which means for every 4 bits, 8 are produced.
    dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    transmissonFlag = False
    try:
      while True:
        read = self.ser.read()
        value = struct.unpack('B',read)[0]
        print value

        if(value == 0x55 and transmissonFlag == False ):
          transmissonFlag=True
        if(transmissonFlag):
          dataList[count] = value
          count+=1
          if(count==7):
            thread = threading.Thread(target=self.output, args=(dataList,))
            thread.daemon = True
            thread.start()
            dataList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            count=0
            transmissonFlag = False
        time.sleep(0)
    except Exception as e:
      print e
      self.ser.close()  
serial_listener = serial_listener()
while(True):
  serial_listener.output([0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x8c,0x2f,0xea])