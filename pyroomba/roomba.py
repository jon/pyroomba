
from serial import Serial
from struct import pack
from struct import unpack
from struct import calcsize
from time import sleep
from math import *

import sensors

def sign(x):
    """Returns the sign of x, either 1 or -1"""
    return int(x / abs(x))

class Roomba(object):
    """A Roomba robot instance"""
    def __init__(self, port, baud = 115200):
        self.port = Serial(port, baud, timeout = None)
    
    # Action commands (i.e., commands that make the Roomba do things)
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
    
    def schedule(self):
        """Not yet implemented"""
        pass
        
    def set_clock(self, day, hour, minute):
        """Sets the Roomba's clock (for scheduling models). Note that hours
        are represented in 24-hour time, 0-23."""
        self.send('BBBB', 168, day, hour, minute)
    
    def off(self):
        """Powers the Roomba down, placing it back in Passive mode."""
        self.cmd(133)

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
    
    def drive_pwm(self, right, left):
        """Controls the Roomba's motors in PWM (pulse-width modulation) mode. 
        This effectively specifies the pulse-width directly to the motor
        controller, with values ranging from -255 to 255. Positive widths
        specify forward motion; negative widths specify backward motion.
        
        Pulse-width modulation is a method of power control in which motors
        (or any current sink, but in our case motors) are pulsed alternately
        to full on and full off repeatedly. Control can be thought of as
        occuring in fixed time intervals (i.e., the period of the control
        signal). The duty cycle (pulse-width) specifies for what fraction of
        each of these periods the motor will be on. So for the Roomba a
        pulse-width of 1 means the motor is fully powered 1/255th of the
        time."""
        if abs(right) > 255:
            right = 255 * sign(right)
        if abs(left) > 255:
            left = 255 * sign(left)
        self.send('>Bhh', 146, right, left)
    
    def motors(self, main = False, side = False, vacuum = False, reverse_main = False, side_clockwise = False):
        """Turns the Roomba's cleaning motors (i.e., brushes and vacuum) on or
        off at full speed. A value of True indicates that the motor should be
        turned on. The value of reverse_main determines the direction of
        the main brush. The value of side_clockwise determines the rotation
        direction of the side brush."""
        state = 0
        state |= side and 1 or 0
        state |= vacuum and 2 or 0
        state |= main and 4 or 0
        state |= side_clockwise and 8 or 0
        state |= reverse_main and 16 or 0
        self.send('BB', 138, state)
    
    def motors_pwm(self, main = 0, side = 0, vacuum = 0):
        """Controls the Roomba's cleaning motors in PWM mode. See the
        documentation for drive_pwm for a description of PWM. Ranges for the
        main and side motors are -127 to 127; range for the vacuum is 0 to 127"""
        if abs(main) > 127:
            main = 127 * sign(main)
        if abs(side) > 127)
            side = 127 * sign(side)
        if vacuum < 0:
            vacuum = 0
        if vacuum > 127:
            vacuum = 127
        self.send('BbbB', 144, main, side, vacuum)
    
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
    
    def scheduling_leds(self):
        """Not yet implemented"""
        pass
    
    def display_raw(self):
        """Not yet implemented"""
        pass
    
    def display_ascii(self, text):
        """Displays up to 4 ASCII characters using the 7-segment displays on
        scheduling Roombas. Only a limited subset of ASCII is supported. See
        the Roomba OI specification for details, but you can safely use all
        letters, numbers, and most punctuation."""
        text = text[0:4].encode('ascii').upper()
        padding = 4 - len(text)
        self.send('B4s', 164, text + ' ' * padding) # struct.pack() will pad for us, but we want space padding, not NUL padding
    
    def buttons(self, clean = False, spot = False, dock = False, minute = False, hour = False, day = False, schedule = False, clock = False):
        """Simulates pressing the Roombas buttons for at most 1/6th of a
        second. Pass True to push the button, False to release it (or not
        push it)"""
        bits = 0
        bits |= clean and 1 or 0
        bits |= spot and 2 or 0
        bits |= dock and 4 or 0
        bits |= minute and 8 or 0
        bits |= hour and 0x10 or 0
        bits |= day and 0x20 or 0
        bits |= schedule and 0x40 or 0
        bits |= clock and 0x80 or 0
        self.send('BB', 165, bits)
    
    def define_song(self):
        """Not yet implemented"""
        pass
    
    def play_song(self):
        """Not yet implemented"""
        pass
    
    # Data commands (i.e., getting information out of the Roomba)
    def sensors(self, sensor):
        """Poll a single sensor"""
        self.query_list(sensor)
    
    def query_list(self, *sensors):
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
        values = unpack(response_format, response)
        return dict(zip(names, values))
    
    def stream_samples(self, *sensors):
        """Starts streaming sensor data from the Roomba at a rate of one
        reading every 15ms (the Roomba's internal update rate). After this
        method has executed you should call poll() at least once every 15ms
        to access the returned sensor data. To halt the stream call 
        stream_pause(). To result the stream with the same packet list call
        stream_resume()."""
        packet_list = [ packet for packet, format, name in sensors ]
        count = len(packet_list)
        format = 'BB' + ('B' * count)
        self.send(format, 148, count, *packet_list)
    
    def poll(self):
        """Reads a single sample from the current sample stream."""
        # Samples always start with a 19 (decimal) followed by a byte indicating the length of the message
        magic = ord(self.port.read())
        while magic <> 19:
            # We're out of sync. Read until we get our magic (which might occur mid-packet, so we may not resync)
            magic = ord(self.port.read())
        length = ord(self.port.read()) # Bytes left to read
        packet = self.port.read(length)
        if (sum(unpack('B' * length, packet)) & 0xff) <> 0:
            # Bad checksum. Ditch everything in the input buffer
            self.port.flushInput()
            raise 'Bad checksum while attempting to read sample' # Should maybe add autoretry option?
        packet = packet[0:-1] # Strip off checksum
        readings = {}
        while len(packet) <> 0:
            sensor_id = ord(packet[0])
            id, format, name = sensors.SENSOR_MAP[sensor_id]
            size = calcsize(format)
            value = unpack(format, packet[1:1+size])
            readings[name] = value
            packet = packet[1+size:]
        return readings
        
    # Cleaup and shut down
    def close(self):
        """Closes the serial port used to control the Roomba"""
        self.port.close()

