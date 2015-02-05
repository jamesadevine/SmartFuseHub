from smart_fuse_networker import smart_fuse_networker
from serial_listener import serial_listener
import time

print "Starting networker..."

networker = smart_fuse_networker()

print "Obtaining credentials..."

credentialsObtained = False

while not credentialsObtained:
  result = networker.getOwner()
  print str(result)
  if 'error' in result:
    credentialsObtained=False
    print "Credentials couldn't be obtained... Is the hub linked?"
    time.sleep(30)
  else:
    credentialsObtained=True
    networker.userID = result['hub']['ownerid']
    networker.hubID = result['hub']['id']
    print networker.userID+" "+networker.hubID

print "Credentials obtained, starting serial_listener..."

listener = serial_listener(networker)

listener.listen()