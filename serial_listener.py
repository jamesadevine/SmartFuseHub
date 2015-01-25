import serial
import struct
import time
import threading

class serial_listener(object):
  def __init__(self,networker):
    self.ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)
    self.networker = networker


  def output(self,valList):
    binaryString = ''.join('{0:08b}'.format(valList[i])[::-1] for i in range(len(valList)))
    binaryResult=binaryString
    id=int(binaryResult[0:12][::-1],2)
    sampleCount=int(binaryResult[12:24][::-1],2)
    totalVal=int(binaryResult[24:48][::-1],2)
    checkSum=int(binaryResult[48:56][::-1],2) 
    ourCheckSum = 0+[int(binaryResult[i:i+8][::-1],2) for i in range(0, len(binaryResult), 8)]
    ourCheckSum = ourCheckSum%255
    print "received checksum "+str(checkSum)+" calculated: "+str(ourCheckSum)
    #ourCheckSum
    voltage = 0
    
    #line=[binaryResult[i:i+8] for i in range(0, len(binaryResult), 8)]
    if sampleCount>0:
      voltage = float((float(5000/4095)*(float(totalVal)/float(sampleCount)))/1000)

    self.networker.sendFuseData(voltage,id)

  #print "ID: "+str(idVal)+" sample count: "+str(sampleCount)+" total: "+str(totalVal)+" checkSum: "+str(checkSum) +" Apparent voltage: "+str(voltage)
  #print "RESULT: "+'||'.join(line)+" LEN: "+str(len(binaryResult))
  #binaryResult=""

  def listen(self):
    count = 0
    dataList = [0,0,0,0,0,0,0]
    previousVal = -1
    transmissonFlag = False
    try:
      while True:
        read = self.ser.read()
        value = struct.unpack('B',read)[0]
        print value

        if(previousVal == 0 and value != 0 and transmissonFlag == False ):
          transmissonFlag=True
        if(transmissonFlag):
          dataList[count] = value
          count+=1
          if(count==7):
            thread = threading.Thread(target=self.output, args=(dataList))
            thread.daemon = True
            thread.start()
            dataList = [0,0,0,0,0,0,0]
            count=0
            transmissonFlag = False
        previousVal = value
        time.sleep(0)
    except Exception as e:
      print e
      self.ser.close()  
