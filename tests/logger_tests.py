import os.path
import logging
from custom_formatter import custom_formatter

test_count = 1

listener_prefix = 'listener_test_'

while os.path.isfile(listener_prefix + str(test_count)+'.csv'):
  test_count += 1

# create logger
listener_logger = logging.getLogger('SmartFuse Listener Logger')
listener_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
# add a file handler
fh = logging.FileHandler(listener_prefix + str(test_count)+'.csv')
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
listener_logger.addHandler(fh)

listener_logger.debug('Time,Packet Number,Discarded') 
frmt = logging.Formatter('%(asctime)s.%(msecs)d,%(message)s',"%H:%M:%S")
fh.setFormatter(frmt)
listener_logger.addHandler(fh)

#begin listener_loger test messages...

for i in range(0,10):
    listener_logger.debug(str(i)+',1')
    listener_logger.debug(str(i)+',0')

#end


decoder_prefix = 'decoder_test_'

test_count = 1

while os.path.isfile(decoder_prefix + str(test_count)+'.csv'):
  test_count += 1

# create logger
decoder_logger = logging.getLogger('SmartFuse Decoder Logger')
decoder_logger.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
# add a file handler
fh = logging.FileHandler(decoder_prefix + str(test_count)+'.csv')
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
decoder_logger.addHandler(fh)

decoder_logger.debug('Time,Packet Number,Bit Error,Discarded,Reason,Details') 
frmt = logging.Formatter('%(asctime)s.%(msecs)d,%(message)s',"%H:%M:%S")
fh.setFormatter(frmt)
decoder_logger.addHandler(fh)

#begin decoder_logger test messages
for i in range(0,10):
    decoder_logger.debug(str(i)+','+str(6)+',1,-1,Checksum incorrect| Received:'+str(255)+' | Calculated:'+str(0))
    decoder_logger.debug(str(i)+','+str(12)+',1,-2,Uncorrectable packet')
    decoder_logger.debug(str(i)+','+str(0)+',0,0,Everything is fine | voltage:'+str(2.5))
    decoder_logger.debug(str(i)+','+str(1)+',0,0,Had to correct one bit | corrected bit:'+str(7)+' | new value:'+str(10.7))

#end
