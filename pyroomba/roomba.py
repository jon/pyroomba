
try:
    from serial import Serial
except ImportError:
    print "Unable to import serial library -- unless you are running tests this will not work"
from struct import pack
from struct import unpack
from struct import calcsize
from time import sleep
from time import time
from math import *

import sensors as sensor_list

__all__ = [ 'Roomba', 'RoombaClassic' ]

def sign(x):
    """Returns the sign of x, either 1 or -1"""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0

class Roomba(object):
    """A Roomba robot instance.
    
    A convenient wrapper around the Roomba 500 Open Interface protocol giving
    names to all of the Roomba's various commands. Most of the function names
    map directly to the command names provided in the protocol docs. Where
    names in the documentation were ambiguous some effort has been made to
    clarify. Most importantly, the methods in this class are defined in the
    order they are presented in the documentation. Thus if you find a command
    you know the Roomba supports missing you can, in the worst case, locate it
    by its position in the class definition.
    
    Taking control of an attached Roomba should look something like the
    following:
    
        from pyroomba import Roomba
        roomba = Roomba('/dev/tty.roomba')
        roomba.start()
        roomba.safe()
    
    At this point you have full control over the robot, subject to safety
    considerations (e.g., the robot will not drive itself off a cliff). Unless
    you have a good reason to do otherwise, this is the recommended mode of
    operation.
    
    Once you are done with the robot is is recommended (although not strictly
    necessary) that you call close() to free up the serial port.
    """
    
    BAUD_RATES = {
        300: 0,
        600: 1,
        1200: 2,
        2400: 3,
        4800: 4,
        9600: 5,
        14400: 6,
        19200: 7,
        28800: 8,
        38400: 9,
        57600: 10,
        115200: 11
    }
    
    def __init__(self, port, baud = 115200, timeout = 0.030, serial_port = None):
        """Instantiate a new Roomba on a given port at a given speed.
        
        Arguments are:
         port: The serial port to which the robot is connected (e.g., 
            '/dev/tty.roomba' or 'COM1')
         baud: The baud rate or speed at which to communicate with the robot.
            This defaults to 115200 which should be correct for 500 series
            robots. Ealier models communicated at 57600."""
        self._running = False
        if not serial_port:
            self.port = Serial(port, baudrate = baud, timeout = timeout) # Anything we ask the robot to do it should reply within 0.015 seconds. We give it a buffer of twice that.
        else:
            self.port = serial_port # Mostly useful for testing, but also if
            # you have a pyserial compliant class for communicating over some
            # other medium. Mostly it needs to support blocking reads and
            # writes, as well as .flushInput()
    
    # Action commands (i.e., commands that make the Roomba do things)
    def send(self, format, *args):
        """Send a command to the robot. 
        
        This is basically a wrapper around self.port.write and struct.pack"""
        self.port.write(pack(format, *args))
    
    def cmd(self, byte):
        """Convenience method to send a single byte command to the robot."""
        self.send('B', byte)
        
    def baud(self, baud_rate):
        """Changes the baudrate at which the Roomba communicates"""
        if not baud_rate in self.BAUD_RATES:
            raise 'Invalid baud rate specified'
        self.send('BB', 128, self.BAUD_RATES[baud_rate])
        sleep(0.1)
        self.port.setBaudrate(baud_rate)
        sleep(0.1)
    
    def start(self):
        """Start controlling the robot; wait for a tenth of a second to allow the Roomba to change modes"""
        self.cmd(128)
        sleep(0.1)  
        self.cmd(130) # Necessary for SCI robots (no harm on OI?)
        sleep(0.1)
    
    def safe(self):
        """Put the robot into safe mode; wait for a tenth of a second to allow the Roomba to change modes. 
        
        Safe mode allows full control of the robot but leaves cliff-detection
        sensors and the like enabled. This is intended to prevent most forms
        of unintentional or intentional robot doom."""
        self.cmd(131)
        sleep(0.1)
    
    def full(self):
        """Take full control of the robot; wait for a tenth of a second to allow the Roomba to change modes.
        
        Full control mode disables all of the Roomba's self-preservation
        features. In full mode the robot will be perfectly happy to burn out
        its motors or run off a cliff."""
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
        """Sets the Roomba's clock (for scheduling models). 
        
        Note that hours are represented in 24-hour time, 0-23."""
        self.send('BBBB', 168, day, hour, minute)
    
    def off(self):
        """Powers the Roomba down, placing it back in Passive mode."""
        self.cmd(133)

    def drive(self, speed, radius):
        """Instructs the Robot to begin driving with a certain speed, specified in mm/sec, and turning radius, specified in mm. 
        
        This method is untested, and while it can be safely assured that the
        command will be sent as specified, the Roomba OI manual's assertion
        that the speed and radius are specified in mm is likely incorrect. The
        sensor data return when requesting distance traveled is supposedly in
        mm, but empirical results suggest that the data is really measured in
        cm."""
        if radius == 0x8000:
            self.send('>BhH', 137, speed, radius)
            return # Special case for straight ahead
        if abs(speed) > 500:
            speed = 500 * sign(speed)
        if abs(radius) > 2000:
            radius = 2000 * sign(radius)
        if radius <> 0x8000:
            self.send('>Bhh', 137, speed, radius)
    
    def drive_direct(self, right, left):
        """Instructs the robot to begin driving with a given speed for each drive wheel, specfied in mm/sec.
        
        The same caveat with respect to units
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
        """Turns the Roomba's cleaning motors (i.e., brushes and vacuum) on or off at full speed. 
        
        A value of True indicates that the motor should be
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
        """Controls the Roomba's cleaning motors in PWM mode. 
        
        See the documentation for drive_pwm for a description of PWM. Ranges
        for the main and side motors are -127 to 127; range for the vacuum is
        0 to 127"""
        if abs(main) > 127:
            main = 127 * sign(main)
        if abs(side) > 127:
            side = 127 * sign(side)
        if vacuum < 0:
            vacuum = 0
        if vacuum > 127:
            vacuum = 127
        self.send('BbbB', 144, main, side, vacuum)
    
    def leds(self, color = 0, intensity = 0, check_robot = False, dock = False, spot = False, debris = False):
        """Sets the status of the Roomba's LEDs. 
        
        Color and intensity must be in the range (0-255). Color ranges from
        solid green to solid red. Intensity ranges from completely dark to
        fully illuminated. Other LEDs are specified as either on (True) or off
        (False)."""
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
        """Displays up to 4 ASCII characters using the 7-segment displays on scheduling Roombas. 
        
        Only a limited subset of ASCII is supported. See the Roomba OI
        specification for details, but you can safely use all letters,
        numbers, and most punctuation."""
        text = text[0:4].encode('ascii').upper()
        padding = 4 - len(text)
        self.send('B4s', 164, text + ' ' * padding) # struct.pack() will pad for us, but we want space padding, not NUL padding
    
    def buttons(self, clean = False, spot = False, dock = False, minute = False, hour = False, day = False, schedule = False, clock = False):
        """Simulates pressing the Roombas buttons for at most 1/6th of a second. 
        
        Pass True to push the button, False to release it (or not push it)"""
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
    
    def define_song(self, songID, notes, durations):
        """Defines a song in the Roomba's repertoire"""
        packingScheme = 'B' * (2 * len(notes) + 3)
        composition = list(reduce(lambda x, y: x + y, zip(notes, durations)))
        self.send(packingScheme, 140, songID, len(notes), *composition)
    
    def play_song(self, number):
        """Plays one of the already stored Roomba songs"""
        self.send('BB', 141, number)
    
    def _read_sensor_list(self, sensors):
        """Reads a list of sensor values and returns the associated dictionary"""
        #packet_list = [ packet for packet, format, name in sensors ]
        formats = [ format for packet, format, name in sensors ]
        names = [ name for packet, format, name in sensors ]
        
        response_format = '>' + ''.join(formats)
        response = self.port.read(calcsize(response_format))
        values = unpack(response_format, response)
        return dict(zip(names, values))
    
    # Data commands (i.e., getting information out of the Roomba)
    def sensors(self, sensor):
        """Request a single sensor packet"""
        sensor_id, format, name = sensor
        self.send('BB', 142, sensor_id)
        # It's ugly to check for things like this
        if isinstance(format, str):
            format = '>' + format
            return self.port.read(calcsize(format))
        elif isinstance(format, list):
            # Some packets return a list of results (particularly on SCI robots)
            return self._read_sensor_list(format)
        else:
            raise 'Unknown sensor format type'
    
    def query_list(self, *sensors):
        """Takes a blocking sample of a collection of Roomba's sensors, specified using the constants defined in this module"""
        packet_list = [ packet for packet, format, name in sensors ]
        count = len(packet_list)
        format = 'BB' + 'B' * count
        self.send(format, 149, count, *packet_list)
        
        return self._read_sensor_list(sensors)
    
    def stream_samples(self, *sensors):
        """Starts streaming sensor data from the Roomba at a rate of one reading every 15ms (the Roomba's internal update rate).
        
        After this method has executed you should call poll() at least once
        every 15ms to access the returned sensor data. To halt the stream call
        stream_pause(). To result the stream with the same packet list call
        stream_resume()."""
        packet_list = [ packet for packet, format, name in sensors ]
        count = len(packet_list)
        format = 'BB' + ('B' * count)
        self.send(format, 148, count, *packet_list)
    
    def pause_stream(self):
        """Pauses the sample stream (if any) coming from the Roomba"""
        self.send('BB', 150, 0)
        sleep(0.1)
        self.port.flushInput()
        
    
    def resume_stream(self):
        """Resumes the sample stream with the previously requested set of sensors"""
        self.send('BB', 150, 1)
    
    def poll(self):
        """Reads a single sample from the current sample stream."""
        # Samples always start with a 19 (decimal) followed by a byte indicating the length of the message
        magic = ord(self.port.read())
        while magic <> 19:
            # We're out of sync. Read until we get our magic (which might
            # occur mid-packet, so we may not resync, but in that case the
            # checksum should be bad and we'll ditch everything, we hope.)
            magic = ord(self.port.read())
        length = ord(self.port.read()) + 1 # Bytes left to read (plus checksum)
        packet = self.port.read(length)
        # Roomba OI documentaiton is wrong, Checksum includes 19 magic (-1 for extra length byte)
        if (sum(unpack('B' * length, packet), length + 18) & 0xff) <> 0:
            # Bad checksum. Ditch everything in the input buffer
            self.port.flushInput()
            raise (-1, 'Bad checksum while attempting to read sample') # Should maybe add autoretry option?
        packet = packet[0:-1] # Strip off checksum
        readings = {}
        while len(packet) <> 0:
            sensor_id = ord(packet[0])
            id, format, name = sensor_list.SENSOR_ID_MAP[sensor_id]
            size = calcsize(format)
            value = unpack(format, packet[1:1+size])
            readings[name] = value[0]
            packet = packet[1+size:]
        return readings
        
    # Cleaup and shut down
    def close(self):
        """Closes the serial port used to control the Roomba"""
        self.stop()
        self.port.close()
    
    # The simplest of polling run-loops, perfect for SCI robots
    def run(self, sensors = sensor_list.ALL_SCI, idle_func = None):
        """Polls the robot at most once every 15ms, updating stored sensor data and optionally calling an idle function"""
        if self._running:
            return
        self._running = True
        while self._running:
            start = time()
            self.latest = self.sensors(sensors)
            if idle_func:
                idle_func()
            stop = time()
            remaining = 0.015 - (start - stop)
            if remaining > 0:
                sleep(remaining)
    
    def stop(self):
        """Signals the built-in polling run-loop to stop if it is running"""
        self._running = False

class RoombaClassic(Roomba):
    """Classic version of the Roomba robot (i.e., Red, Discovery, Sage).
    
    This class provides compatibility functions mapping from newer control
    methods (i.e., drive_pwm(), drive_direct()) onto the traditional drive()
    method. This allows code written expecting a Roomba supporting these
    methods to be used with older models.
    """
    def __init__(self, port, baud = 57600, serial_port = None):
        super(RoombaClassic, self).__init__(port, baud, serial_port)
        self._radius = 258.0 / 2
    
    def drive_direct(self, right, left):
        """Converts direct motor drive commands into radius/speed commands"""
        if left == right:
            # Special case to handle equal
            self.drive(left, 0x8000)
            return
        elif abs(left) == abs(right):
            # The only way this is true if the above wasn't is if the wheels are equal and opposite
            if left < right:
                self.drive(right, -1)
            else:
                self.drive(left, 1)
            return
        average = int((abs(right) + abs(left)) / 2)
        slope = (right - left) / (2 * self._radius)
        y_intercept = right - slope*self._radius
        radius = y_intercept / slope
        self.drive(sign(left + right) * average, radius)
    
    def drive_pwm(self, right, left):
        """Converts PWM values to direct motor drive values, simulating the desired duty cycle"""
        self.drive_direct(right / 255 * 500, left / 255 * 500)
    

