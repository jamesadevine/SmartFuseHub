from smart_monitoring_networker import smart_monitoring_networker
from serial_listener import serial_listener
import time

print "Starting networker..."

networker = smart_monitoring_networker()

print "Obtaining credentials..."

credentialsObtained = False

while not credentialsObtained:
  result = networker.getOwner()
  if result is None:
    print "Credentials couldn't be obtained... Is the hub linked?"
    time.sleep(30)
    continue
  else:
    credentialsObtained=True
    networker.userID = result['hub']['ownerid']
    networker.hubID = result['hub']['id']
    print networker.userID+" "+networker.hubID

print "Credentials obtained, starting serial_listener..."

listener = serial_listener(networker)

print "Listening..."

listener.listen()