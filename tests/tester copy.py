import sys
import os.path

baud_rates = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200,230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000)

if len(sys.argv) == 1 or len(sys.argv) < 3:
  print 'You forgot the baud rate or cable length!\nThis should be:\npython tester.py baudrate cablelength\nCable length should be in metres'
  sys.exit()

#get baud rate
baud = sys.argv[1]

#get cable length

cable_length = sys.argv[2]

#test to see if the user is stupid
try:
  baud = int(baud)
  cable_length = float(cable_length)
except:
  raise Exception("Not a valid baud rate or cable length")

#check for valid baud
if baud not in baud_rates:
  raise Exception("Not a valid baud rate")

#create test results file...
test_count = 1

prefix = str(baud)+'_'+str(cable_length)+'_'

while os.path.isfile(prefix + str(test_count)):
  test_count += 1

f = open(prefix + str(test_count)+'.csv','w')
f.write('Time,Packet Number,BER,Packet Loss\r\n') 
f.close() 



print 'Beginning test with a Baud rate of: '+ str(baud)
