
from serial import Serial
from struct import pack
from struct import unpack
from struct import calcsize
from time import sleep
from math import *

def sign(x):
    """Returns the sign of x, either 1 or -1"""
    return int(x / abs(x))

class Roomba(object):
    """A Roomba robot instance"""
    def __init__(self, port, baud = 115200):
        self.port = Serial(port, baud, timeout = None)
    
    def send(self, format, *args):
        """Send a command to the robot. Basically a wrapper around self.port.write and struct.pack"""
        self.port.write(pack(format, *args))
    
    def cmd(self, byte):
        """Convenience method to send a single byte command to the robot"""
        self.send('B', byte)
    
    def start(self):
        """Start controlling the robot, wait for a tenth of a second to allow the Roomba to change modes"""
        self.cmd(128)
        sleep(0.1)  
    
    def safe(self):
        """Put the robot into safe mode, wait for a tenth of a second to
        allow the Roomba to change modes. Safe mode allows full control
        of the robot but leaves cliff-detection sensors and the like
        enabled. This is intended to prevent most forms of unintentional
        or intentional robot doom."""
        self.cmd(131)
        sleep(0.1)
    
    def full(self):
        """Take full control of the robot, wait for a tenth of a second to
        allow the Roomba to change modes. Full control mode disables all of the
        Roomba's self-preservation features. In full mode the robot will be
        perfectly happy to burn out its motors or run off a cliff."""
        self.cmd(132)
        sleep(0.1)
    
    def clean(self):
        """Start a standard cleaning cycle"""
        self.cmd(135)
    
    def max(self):
        """Start a max cleaning cycle"""
        self.cmd(136)
    
    def spot(self):
        """Start a spot cleaning cycle"""
        self.cmd(134)
    
    def dock(self):
        """Seek self-charging drive-on dock"""
        self.cmd(143)
    
    def drive(self, speed, radius):
        """Instructs the Robot to begin driving with a certain speed, 
        specified in mm/sec, and turning radius, specified in mm. This method
        is untested, and while it can be safely assured that the command will
        be sent as specified, the Roomba OI manual's assertion that the speed
        and radius are specified in mm is likely incorrect. The sensor data
        return when requesting distance traveled is supposedly in mm, but
        empirical results suggest that the data is really measured in cm."""
        self.send('>Bhh', 137, speed, radius)
    
    def drive_direct(self, right, left):
        """Instructs the robot to begin driving with a given speed for each 
        drive wheel, specfied in mm/sec. The same caveat with respect to units
        as specified in drive() likely holds for this method as well."""
        self.send('>Bhh', 145, right, left)
    
    def leds(self, color = 0, intensity = 0, check_robot = False, dock = False, spot = False, debris = False):
        """Sets the status of the Roomba's LEDs. Color and intensity must be
        in the range (0-255). Color ranges from solid green to solid red.
        Intensity ranges from completely dark to fully illuminated. Other LEDs
        are specified as either on (True) or off (False)."""
        bits = 0
        bits |= debris and 1 or 0
        bits |= spot and 2 or 0
        bits |= dock and 4 or 0
        bits |= check_robot and 8 or 0
        self.send('BBBB', 139, bits, color, intensity)
    
    def sample(self, *sensors):
        """Takes a blocking sample of a collection of Roomba's sensors,
        specified using the constants defined in this module"""
        packet_list = [ packet for packet, format, name in sensors ]
        formats = [ format for packet, format, name in sensors ]
        names = [ name for packet, format, name in sensors ]
        count = len(packet_list)
        format = 'BB' + 'B' * count
        self.send(format, 149, count, *packet_list)
        
        response_format = '>' + ''.join(formats)
        response = self.port.read(calcsize(response_format))
        return unpack(response_format, response)
        
    def close(self):
        """Closes the serial port used to control the Roomba"""
        self.port.close()


