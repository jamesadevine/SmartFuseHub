import serial
import sys
import time
from error_correction_util import error_utils

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600)

if len(sys.argv) == 1 or len(sys.argv) < 4:
  print 'You forgot the number of packets, corrective percent, and the complete error percent!\nThis should be:\npython error_correction_test.py numpackets correctable uncorrectable\n'
  sys.exit()


try:
  num_packets = int(sys.argv[1])
  correctable_percent = float(sys.argv[2])
  uncorrectable_percent = float(sys.argv[3])
except:
  raise Exception("Not a valid number of packets, correctable percent or uncorrectable percent")

num_incorrect = int(round(num_packets*(correctable_percent/100)))
num_uncorrect = int(round(num_packets*(uncorrectable_percent/100)))
num_correct = int(num_packets-num_incorrect-num_uncorrect)

#instantiate error_utils
util = error_utils(num_correct,num_incorrect,num_uncorrect)

#get packets from utils
packets = util.generate_packets()

#sleep time for packet loop
sleep_time = 1/1000000

#loop through packets and send via Serial
try:
  for i in range(0,len(packets)):
    #send start bit
    ser.write(85)

    #write each byte
    for j in range(0,len(packets[i])):
      ser.write(packets[i][j])

    #sleep 1 us
    time.sleep(sleep_time)
except Exception as e:
  print str(e)
  #don't forget to close serial!
ser.close()  
