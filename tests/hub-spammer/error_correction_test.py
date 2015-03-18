import serial
import sys
import os.path
import time
import logging
from error_correction_util import error_utils

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)

if len(sys.argv) == 1 or len(sys.argv) < 5:
  print 'You forgot the number of packets, corrective percent, and the complete error percent!\nThis should be:\npython error_correction_test.py numpackets correctable uncorrectable checksum\n'
  sys.exit()


try:
  num_packets = float(sys.argv[1])
  correctable_percent = float(sys.argv[2])
  uncorrectable_percent = float(sys.argv[3])
  checksum_percent = float(sys.argv[4])
except:
  raise Exception("Not a valid number of packets, correctable percent or uncorrectable percent")


num_incorrect = int(round(num_packets*(correctable_percent/100)))
num_uncorrect = int(round(num_packets*(uncorrectable_percent/100)))
num_checksum = int(round(num_packets*(checksum_percent/100)))

num_correct = int(num_packets-num_incorrect-num_uncorrect-num_checksum)

print str(num_incorrect)+' '+str(num_uncorrect)+' '+str(num_checksum)+' '+str(num_correct)

spammer_prefix = 'spammer_'+str(num_correct)+'_'+str(num_incorrect)+'_'+str(num_uncorrect)+'_'+str(num_checksum)+'_'

test_count = 1

while os.path.isfile("./logs/"+spammer_prefix + str(test_count)+'.csv'):
  test_count += 1

test_count = test_count

# create logger
spammer_logger = logging.getLogger('SmartFuse Listener Logger')
spammer_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG

# add a file handler
fh = logging.FileHandler("./logs/"+spammer_prefix + str(test_count)+'.csv')
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
spammer_logger.addHandler(fh)

spammer_logger.debug('Time,Packet Number,Type') 
frmt = logging.Formatter('%(asctime)s.%(msecs)d,%(message)s',"%H:%M:%S")
fh.setFormatter(frmt)
spammer_logger.addHandler(fh)



#instantiate error_utils
util = error_utils(num_correct,num_incorrect,num_uncorrect,num_checksum)

#get packets from utils
packets = util.generate_packets()

print 'PACKET LEN '+str(len(packets))

#sleep time for packet loop
sleep_time = 0.5

#loop through packets and send via Serial
try:
  for i in range(0,len(packets)):
    #send start bit
    ser.write(chr(85))

    #write each byte
    for j in range(0,len(packets[i])-1):
      ser.write(chr(packets[i][j]))

    spammer_logger.debug(str(i+1)+','+str(packets[i][len(packets[i])-1])) 

    #type is 0 for correct,  1 for incorrect, -1 for checksum incorrect, -2 for uncorrectable 
    print "Sent packet: "+str(i+1)+' type: '+str(packets[i][len(packets[i])-1])

    #sleep half a second
    time.sleep(0.2)
except Exception as e:
  print str(e)
  #don't forget to close serial!
ser.close()  
