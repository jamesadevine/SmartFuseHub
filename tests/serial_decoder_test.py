from multiprocessing import Process
import os.path
import logging

class serial_decoder(Process):
        
  def __init__(self, values,baud,cable_length,packet_number):
    super(serial_decoder, self).__init__()

    self.packet_number = packet_number

    decoder_prefix = 'decoder_'+str(baud)+'_'+str(cable_length)+'_'

    test_count = 1

    while os.path.isfile(decoder_prefix + str(test_count)+'.csv'):
      test_count += 1

    # create logger
    self.decoder_logger = logging.getLogger('SmartFuse Decoder Logger')
    self.decoder_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
    # add a file handler
    fh = logging.FileHandler(decoder_prefix + str(test_count)+'.csv')
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

    self.bit_error = 0
    self.check_sum_rec = 0
    self.check_sum = 0
    self.incorrect_index = 0
    self.corrected_val = 0


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
    try:
      self.decode(values)
    except Exception,e:

      #-1 for checksum error
      if str(e) == 'Check sum incorrect':
        self.decoder_logger.debug(str(self.packet_number)+','+str(self.bit_error)+',1,-1,Checksum incorrect| Received:'+str(self.check_sum_rec)+' | Calculated:'+str(self.check_sum))
      
      #-2 for uncorrectable packet...
      if str(e) == 'Uncorrectable packet':
        self.decoder_logger.debug(str(self.packet_number)+','+str(self.bit_error)+',1,-2,Uncorrectable packet')
      self.terminate()

  def decode(self,values):
    values=self.convert_packet(values)
    print str(values)
    binaryString = ''.join('{0:08b}'.format(values[i])[::-1] for i in range(len(values)))
    binaryResult=binaryString
    id=int(binaryResult[0:12][::-1],2)
    sampleCount=int(binaryResult[12:24][::-1],2)
    totalVal=int(binaryResult[24:48][::-1],2)
    check_sum=int(binaryResult[48:56][::-1],2) 
    calculated_check_sum = self.calculate_checksum(values)

    self.check_sum_rec = check_sum
    self.check_sum = calculated_check_sum

    if calculated_check_sum != check_sum:
      raise Exception("Check sum incorrect")
      return

    voltage = 0
    
    if sampleCount>0:
      voltage = float((float(5000/4095)*(float(totalVal)/float(sampleCount)))/1000)

    if self.incorrect_index == 0 and self.corrected_val == 0:
      self.decoder_logger.debug(str(self.packet_number)+','+str(self.bit_error)+',0,0,Everything is fine | voltage:'+str(voltage))
    else:
      self.decoder_logger.debug(str(self.packet_number)+','+str(self.bit_error)+',0,0,Had to correct one bit | corrected bit:'+str(self.incorrect_index))+' | new value:'+str(self.corrected_val)

  def calculate_checksum(self,values):
    checksum = 0
    for i in range(0,len(values)-1):
      checksum += values[i]
      if checksum>255:
        checksum = checksum-256
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

    #one bit error which can be corrected
    if not parity:
      if self.is_correctable(check1,check2,check3):
        self.bit_error=1
        #determine which bit is wrong!
        incorrect_index = self.truth_table_lookup[(check1,check2,check3)]
        #correct the value...
        value = self.toggle_bit(value,incorrect_index)

        self.incorrect_index = incorrect_index
        self.corrected_val = value
        print 'incorrect index: '+str(incorrect_index)
        print 'new val = '+str(value)
      else:
        self.bit_error = 2
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
