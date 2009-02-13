
from serial import Serial
from struct import pack
from struct import unpack
from struct import calcsize
from time import sleep
from math import *


# Sensor definitions
BUMP_WHEEL_DROPS = (7, 'B', 'bump_wheel_drops')
WALL = (8, 'B', 'wall')

RIGHT_ENCODER = (43, 'H', 'right_encoder')
LEFT_ENCODER = (44, 'H', 'left_encoder')

DISTANCE = (19, 'h', 'distance')
ANGLE = (20, 'h', 'angle')
CHARGING_STATE = (21, 'B', 'charging_state')

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
        """Send a single byte command to the robot"""
        self.send('B', byte)
    
    def start(self):
        """Start controlling the robot"""
        self.cmd(128)
        sleep(0.1)  
    
    def safe(self):
        """Put the robot into safe mode"""
        self.cmd(131)
        sleep(0.1)
    
    def full(self):
        """Take full control of the robot"""
        self.cmd(132)
        sleep(0.1)
    
    def clean(self):
        """Start a cleaning cycle"""
        self.cmd(135)
    
    def max(self):
        """Start a max cleaning cycle"""
        self.cmd(136)
    
    def spot(self):
        """Start a spot cleaning cycle"""
        self.cmd(134)
    
    def dock(self):
        """Seek charging dock"""
        self.cmd(143)
    
    def drive(self, speed, radius):
        """Instructs the Robot to begin driving with a certain speed, specified in mm/sec, and turning radius, specified in mm"""
        self.send('>Bhh', 137, speed, radius)
    
    def drive_direct(self, right, left):
        """Instructs the robot to begin driving with a given speed for each drive wheel, specfied in mm/sec"""
        self.send('>Bhh', 145, right, left)
    
    def leds(self, color = 0, intensity = 0, check_robot = False, dock = False, spot = False, debris = False):
        """Sets the status of the Roomba's LEDs"""
        bits = 0
        bits |= debris and 1 or 0
        bits |= spot and 2 or 0
        bits |= dock and 4 or 0
        bits |= check_robot and 8 or 0
        self.send('BBBB', 139, bits, color, intensity)
    
    def sample(self, *sensors):
        """Samples a collection of Roomba's sensors, specified using the constants defined in this module"""
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


class RoombaDynamics(object):
    """A class that models the dynamics of the Roomba's motion using direct encoder values"""
    def __init__(self):
        self.prior_values = (0, 0)
        self.radius = 115.490625
        self.encoder_ratio = 0.55287243514
        self.reset()
    
    def normalize(self, encoders):
        """Normalizes encoder values to deltas"""
        priors = self.prior_values
        self.prior_values = encoders
        # Now some code to handle rollover
        left, right = encoders
        o_left, o_right = priors
        if o_left > left:
            o_left -= 65536
        if o_right > right:
            o_right -= 65536
        priors = (o_left, o_right)
        return tuple(self.encoder_ratio * (a - b) for a, b in zip(encoders, priors))
    
    def initialize_priors(self, encoders):
        """Initialize the prior encoder values -- identical to normalizing once and discarding the result"""
        self.normalize(encoders)
    
    def find_pivot(self, encoders):
        """Calculates a position delta based on encoder values"""
        left, right = encoders
        slope = (right - left) / (2 * self.radius)
        y_intercept = right - slope*self.radius
        x_intercept = -y_intercept / slope
        return (x_intercept, 0.0)
    
    def rotate(self, point, pivot, theta):
        """Rotates a point about a pivot for some number of degrees"""
        point = tuple(a - b for a, b in zip(point, pivot))
        x, y = point
        x_p = x*cos(theta) - y*sin(theta)
        y_p = x*sin(theta) + y*cos(theta)
        point = (x_p, y_p)
        return tuple(a + b for a, b in zip(point, pivot))
    
    def update(self, encoders, time):
        """Finds the displacement of the center of the robot based on distance, angle, and encoders. This assumes a constant velocity for the encoders."""
        left, right = encoders
        v_left, v_right = left / time, right / time
        if left == right:
            return (left / time, 0.0)
        pivot = self.find_pivot((v_left, v_right))
        x_int, zero = pivot
        right_off, left_off = x_int - self.radius, x_int + self.radius
        #print v_right, v_left, right_off, left_off, x_int
        if abs(right_off) > abs(left_off):
            w = v_right / right_off # angular velocity
        else:
            w = v_left / left_off
        d_theta = w * time # change in angle (about pivot)
        
        pos = self.position()
        t = self.angle()
        rotated_pivot = self.rotate(pivot, (0.0, 0.0), self.angle())
        offset_pivot = tuple(a + b for a, b in zip(rotated_pivot, pos))
        self.wheels = tuple(self.rotate(w, offset_pivot, d_theta) for w in self.wheels)        
        
    def angle(self):
        """Determines a the angle of the rotation of the robot from the origin"""
        left, right = self.wheels
        pos = self.position()
        # use the right wheel, since this will give us rotation above the x
        x, y = right
        x0, y0 = pos
        t = acos((x - x0) / self.radius)
        if (y - y0) > 0:
            return t
        else:
            return (pi - t) + pi
    
    def position(self):
        """Calculates the position of the center of the robot based on wheel positions"""
        left, right = self.wheels
        d = (a - b for a, b in zip(right, left))
        d = (x / 2 for x in d)
        return tuple(a + b for a, b in zip(left, d))
    
    def reset(self):
        """Reset the robots position"""
        self.wheels = ((-self.radius, 0), (self.radius, 0))

