import random

class error_utils(object):
  def __init__(self,correct,incorrect,uncorrect,checksum):
    #number of different packets...
    self.correct = correct
    self.incorrect = incorrect
    self.uncorrect = uncorrect
    self.checksum = checksum

    #hamming code lookup table for: to_hamming
    self.hamming_lookup ={
      0x0:0x15,
      0x1:0x02,
      0x2:0x49,
      0x3:0x5e,
      0x4:0x64,
      0x5:0x73,
      0x6:0x38,
      0x7:0x2F,
      0x8:0xD0,
      0x9:0xC7,
      0xA:0x8C,
      0xB:0x9B,
      0xC:0xA1,
      0xD:0xB6,
      0xE:0xFD,
      0xF:0xEA
    }

    #the test packets that will be sent during generation
    self.correct_packet = self.to_hamming([10,20,30,40,50,60,210]) #all correct generates [140, 21, 100, 2, 253, 2, 208, 73, 73, 94, 161, 94, 73, 182]

    print str(self.correct_packet)
    self.correct_packet.append(0);
    self.incorrect_packet = [140, 21, 100, 3, 253, 2, 208, 73, 73, 94, 161, 94, 73, 182, 1] #one incorrect value index 4
    self.checksum_packet = [140, 21, 100, 2, 253, 2, 208, 253, 73, 94, 161, 94, 73, 182, -1] #correct-ish values incorrect check sum
    self.uncorrectable_packet = [140, 27, 100, 3, 253, 2, 209, 73, 254, 94, 161, 94, 73, 182, -2] #two incorrect values

  def get_bit(self,byte,index):
      #gets the parametrised bit
      return ((byte&(1<<index))!=0);

  def get_upper_nibble(self,value):
      #comprehend the top four bits into a string, and return
      return ''.join('{0:0b}'.format(int(self.get_bit(value,i)))for i in range(7,3,-1) )

  def get_lower_nibble(self,value):
      #comprehend the lower four bits into a string, and return
      return ''.join('{0:0b}'.format(int(self.get_bit(value,i)))for i in range(3,-1,-1) )

  def to_hamming(self,values):
      #hamming code has 4:8 encoding - therefore double array
      new_list = [0]*(len(values)*2)

      #take the paramterised values, and turns it into hamming code
      for i in range(0,len(values)):
        #correct count
        j=i*2
        #put into the returned list
        temp = int(self.get_lower_nibble(values[i]),2)
        new_list[j] = self.hamming_lookup[temp]
        temp = int(self.get_upper_nibble(values[i]),2)
        new_list[j+1] = self.hamming_lookup[temp]

      #return new list
      return new_list

  def generate_packets(self):
    total = self.correct+self.incorrect+self.uncorrect+ self.checksum
    return_list = []
    #ensure number of packets are the same as the constructor parameters
    correct_count = 0
    incorrect_count = 0
    uncorrect_count = 0
    checksum_count = 0

    #randomly distribute packets
    while len(return_list)<total:
      random_correct = random.randint(1,10)
      random_incorrect = random.randint(1,10)
      random_uncorrect = random.randint(1,10)
      random_checksum = random.randint(1,10)

      #correct packet generator
      if correct_count<self.correct:
        #account for edge case
        remaining_packets = self.correct - correct_count
        if remaining_packets <= 10:
            random_correct = random.randint(1,remaining_packets)
        for i in range(0,random_correct):
            return_list.append(self.correct_packet)
        correct_count += random_correct

      #incorrect packet generator
      if incorrect_count<self.incorrect:
        #account for edge case
        
        remaining_packets = self.incorrect - incorrect_count
        if  remaining_packets<=10:
            random_incorrect = random.randint(1,remaining_packets)
        for i in range(0,random_incorrect):
            return_list.append(self.incorrect_packet)
        incorrect_count += random_incorrect

      #uncorrect generator
      if uncorrect_count<self.uncorrect:
        remaining_packets = self.uncorrect - uncorrect_count
        if remaining_packets <= 10:
            random_uncorrect = random.randint(1,remaining_packets)
        for i in range(0,random_uncorrect):
            return_list.append(self.uncorrectable_packet)
        uncorrect_count += random_uncorrect

      #checksum packet generator
      if checksum_count<self.checksum:
        remaining_packets = self.checksum - checksum_count
        if remaining_packets <= 10:
            random_checksum = random.randint(1,remaining_packets)
        for i in range(0,random_checksum):
            return_list.append(self.checksum_packet)
        checksum_count += random_checksum
      
      
      

    print str(correct_count) +' '+str(incorrect_count)+' '+str(uncorrect_count)+' '+str(checksum_count)
    return return_list
