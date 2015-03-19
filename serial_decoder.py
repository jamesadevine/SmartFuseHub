from multiprocessing import Process


class serial_decoder(Process):
        
  def __init__(self,networker, values):
    super(serial_decoder, self).__init__()

    self.networker = networker

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
    
    #catch exceptions raise by the decode
    #then terminate the process
    try:
      self.decode(values)
    except Exception,e:
      print str(e)
      return

  """
    decodes the values passed through from the serial listener
  """
  def decode(self,values):
    values=self.convert_packet(values)
    #print for testing
    print str(values)
    #process
    binaryString = ''.join('{0:08b}'.format(values[i])[::-1] for i in range(len(values)))
    binaryResult=binaryString
    id=int(binaryResult[0:12][::-1],2)
    sampleCount=int(binaryResult[12:24][::-1],2)
    totalVal=int(binaryResult[24:48][::-1],2)
    check_sum=int(binaryResult[48:56][::-1],2) 
    calculated_check_sum = self.calculate_checksum(values)

    #check if checksum is correct
    if calculated_check_sum != check_sum:
      raise Exception("Check sum incorrect")
      return

    #ourCheckSum
    voltage = 0
    
    #check the number of samples is greater than zero... (It always should be)
    if sampleCount>0:
      voltage = float((float(5000/4095)*(float(totalVal)/float(sampleCount)))/1000)

    #transmit sample to server
    self.networker.sendApplianceData(voltage,id)

  """
    calculates a simple checksum for the received packet
  """
  def calculate_checksum(self,values):
    checksum = 0
    for i in range(0,len(values)-1):
      checksum += values[i]
      if checksum>255:
        checksum = checksum-256
    return checksum

  """
    transposes two bytes into a single byte (reversing the hamming code)
  """
  def convert_packet(self, values):
    newValues = [0,0,0,0,0,0,0]
    valCount=0;
    for i in range(0,len(values),2):
      #convert the two bytes into their actual values, and combine...
      temp = self.transpose(values[i+1])+self.transpose(values[i])
      print 'binary string: '+temp
      newValues[valCount] = int(temp,2)
      valCount+=1
    return newValues

  """
    checks the integrity of the byte passed in as Value (Reversing the hamming code)
  """
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

  """
    determines if a packet is correct and returns True or False depending
  """
  def is_correctable(self, check0, check1, check2):
    return True if (check0 and (check1 or check2)) or (check1 and check2) else False

  """
    fetches the actual bits from the Extended Hamming Code (1,3,5,7)
  """
  def get_nibble(self,value):
    return ''.join('{0:0b}'.format(int(self.get_bit(value,i)))for i in range(7,0,-2) )

  """
    recursive function to calculate parity for a byte using hamming code
  """
  def calculate_parity(self,value,index,step,result):
    if index == 0:
      return result ^ self.get_bit(value,0)
    elif index<0:
      return result
    else:
      return self.calculate_parity(value,index-step,step,result^self.get_bit(value,index)) 

  """
    basic function to calculate parity for a byte using hamming code
  """
  def calculate_parity_specific(self,value,indexesToCheck):
    parity = self.get_bit(value,indexesToCheck[0])
    for i in range(1,len(indexesToCheck)):
      parity = parity ^ self.get_bit(value,indexesToCheck[i])
    return parity

  """
    retrieves a specific bit of a byte
  """
  def get_bit(self,byte,index):
    return ((byte&(1<<index))!=0);

  """
    complements a specific bit of a byte
  """
  def toggle_bit(self,byte,index):
    return byte^(1<<index);
