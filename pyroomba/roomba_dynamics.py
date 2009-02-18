from math import *

__all__ = ['RoombaDynamics']

class RoombaDynamics(object):
    """Model of the dynamics of the Roomba's motion using direct encoder values.
    This treats the Roomba as a rigid body with its origin at the center of the 
    wheelbase. 

    The encoder values along with the elapsed time since the last update
    and the requested direction of motion are used to calculate velocity vectors
    for each of the Roomba's wheels. These vectors allow us to find an imaginary
    pivot about which the robot is rotating. Using this pivot we can calculate the
    angular velocity of the robot from the velocity of either wheel (assuming both
    are moving). Having done that we calculate the change in angle over the
    elapsed time. We then rotate the Roomba's origin the calculated angle about
    the pivot and establish this as the robot's new position.
    
    For details on why this works consult an introductory dynamics textbook. The
    author would like to point out that his understanding of dynamics is
    extremely limited, and he is willing to assert that the code in this class is
    probably not entirely correct. Patches from those with a better understanding
    of the problem at hand are, of course, welcome"""
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

