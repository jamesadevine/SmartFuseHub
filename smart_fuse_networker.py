import urllib
import urllib2
import json
import fcntl, socket, struct


class smart_fuse_networker(object):
  """
  This class is used for communicating with the remote server
  """
  def __init__(self):
    """
    constructor for smart_fuse_networker
    :return: nothing
    """
    self.userID = ""
    self.hubID = ""
    self.apiURL="http://scc-devine.lancs.ac.uk:8000"
    self.mac=self.getHwAddr('eth0')


  def getOwner(self):
    data = urllib.urlencode({'macaddr':self.mac})
    print self.apiURL+"/api/hub?"+data
    request = urllib2.Request(self.apiURL+"/api/hub?"+data)
    response = urllib2.urlopen(request)
    page = response.read()
    return json.loads(page);

  def sendFuseData(self,value,fuseid):
    """
    :param data: the params to use
    """
    data = {
        "userID":self.userID,
        "hubID":self.hubID,
        "fuseID":fuseid,
        "fuseVal":value
    }
    data = urllib.urlencode(data)
    request = urllib2.Request(self.apiURL+"/api/fuse",data)
    response = urllib2.urlopen(request)
    page = response.read()
    return json.loads(page)

  def getHwAddr(self,ifname):
    """
    Gets the mac address of the given interface
    :param ifname: the name of the interface
    :return: mac address of the interface
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]