from threading import Thread

__all__ = ['EventLoop']

class EventLoop(object):
    """Event loop processing for Roomba robots. 
    
    Allows construction of a list of sensors to query, polls those sensors
    either at user-specified intervals or continuously in a background thread
    (recommended).
    
    There are essentially three ways you can use this class correct:
     - Good: Call start_sampling() and then repeatedly call proccess_events() 
         at 15ms intervals
     - Better: Call start() and allow this class to spawn off a background 
         event loop
     - Best: Call run() to allow event processing to occur in the main thread 
         with on call to your idle-function per loop
    
    As to the matter of thread-safety, EventLoop is written in a lock-free
    fashion. What this means is that you can have as many threads reading
    sensor data from it as you like, but you shouldn't attempt to change
    anything (like sensor query lists) from more than one thread at a time."""
    def __init__(self, robot):
        """Create a new empty EventLoop on the specified robot.
        
        You should have at most one event loop per robot. More than that is
        just madness. Also, it can lead to strange behavior when both of them
        call read() on the same serial port at the same time, so don't do it."""
        super(EventLoop, self).__init__()
        self._robot = robot
        self._sensors = []
        self._handlers = {}
        self.latest = {}
        self.running = False
        self._thread = None
        self._idle = None
    
    def set_sensors(self, *sensors):
        """Sets the list of sensors to be read on each pass through the event loop."""
        self._sensors = set(sensors)
        if self.running:
            self._robot.stream_samples(sensors)
    
    def add_sensor(self, sensor):
        """Adds a sensor to the query list.
        
        If the event loop is running this will begin querying the sensor
        immediately."""
        self.set_sensors(self._sensors | set([sensor]))
    
    def remove_sensor(self, sensor):
        """Removes a sensor from the query list.
        
        If the event loop is running this will stop querying the sensor
        immediately."""
        self.set_sensors(self._sensors - set([sensor]))
    
    def start_sampling(self):
        """Asks the Roomba to start returning samples for the sensor query list.
        
        Upon receiving the stream samples command the Roomba will
        automatically start returning samples at 15ms intervals. You should
        therefore call process_events() at least that often.
        
        In general this method should not be called directly. Instead you
        should allow EventLoop to manage the run-loop for you by calling
        either start() or run() depending on whether you want to loop to
        daemonize itself
        """
        self.running = True
        self._robot.stream_samples(sensors)
    
    def process_events(self):
        """Runs one pass of the event-loop, polling for sensor data and running any event handlers."""
        readings = self._robot.poll()
        for name, value in readings:
            if self._handlers.has_key(name):
                self._handlers[name](self._robot, name, value)
        self.latest = readings
    
    def on(self, sensor_name, action):
        """Adds an event handler for a given sensor.
        
        Event handlers should be of the form:
        
            def handler(robot, sensor_name, value):
                # Code to process event
        
        Handlers will be called on the event-loop thread. Implementors should
        ensure thread-safety of their code accordingly.
        """
        self._handlers[sensor_name] = action
    
    def run(self):
        """Starts sampling, and runs the event loop in the calling thread."""
        assert not self.running
        self.start_sampling()
        while self.running:
            self.process_events()
    
    def stop(self):
        """Stops sampling and halts the event loop."""
        self.running = False
        if self._thread:
            self._thread.join()
        self._robot.pause_stream()
    
    def start(self):
        """Spawns off a background thread running the event loop."""
        assert not self.running
        self._thread = Thread(target = self.run)
        self._thread.start()
    

    