"""A library for controlling iRobot devices.

As the name implies, this package is primarily intended for controlling and
monitoring iRobot Roomba series robots. The Roomba class provides a mostly
complete implementation of the iRobot 500 Series Open Interface protocol as a
convenient set of python methods. EventLoop provides a convenient way to
handle sensor data returned from the robot in a sane manner, and 
RoombaDynamics provides an attempt at reasonable localization based on the
robot's built-in odometry.

"""

from roomba import *
from roomba_dynamics import *
from events import *
import sensors
