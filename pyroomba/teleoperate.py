#!/opt/local/bin/python

import roomba

import pygame
import pygame.display
import pygame.joystick

from pygame.locals import *
from time import sleep
from time import time
from math import radians
from math import sin
from math import cos
from math import pi

r = roomba.Roomba('/dev/tty.rootooth')
rd = roomba.RoombaDynamics()
# pygame.joystick.init()
# pygame.display.init()
pygame.init()

pygame.joystick.Joystick(0).init()

r.start()
r.safe()
r.leds(255, 255)

motors = (0, 0)
oldMotors = (0, 0)

def controlMotors():
    global motors, oldMotors
    if motors == oldMotors:
        return
    oldMotors = motors
    left, right = (-500 * x for x in motors)
    r.drive_direct(right, left)

def updateMotors(left = False, right = False):
    global motors
    oldLeft, oldRight = motors
    motors = (left or oldLeft, right or oldRight)

calibrating = False
counts = (0, 0)

def plotCircle():
    """Attempts to plot a circle"""
    circum = rd.radius * 2 * pi
    ticks = rd.encoder_ratio * circum
    counts = (0, 0)
    r.drive_direct(-250, 0)
    while max(counts) < ticks:
        left, right = sampleRobot()
        encoders = rd.normalize((left, right))
        counts = tuple(a + b for a, b in zip(counts, encoders))
    r.drive_direct(0, 0)

def calibrate():
    """Starts or stops calibration for the robot"""
    global calibrating, counts
    calibrating = not calibrating
    circum = 10 * rd.radius * 2 * pi
    if calibrating:
        counts = (0, 0)
    else:
        c = (abs(n) for n in counts)
        rd.encoder_ratio = abs(max(c) / circum)
        print "Encoder ratio", rd.encoder_ratio
        plotCircle()

def processEvent(e):
    global go
    if e.type == JOYAXISMOTION:
        if e.axis == 1:
            updateMotors(left = e.value)
        elif e.axis == 3:
            updateMotors(right = e.value)
    elif e.type == JOYBUTTONUP:
        if e.button == 0:
            r.clean()
        elif e.button == 1:
            r.spot()
        elif e.button == 2:
            r.max()
        elif e.button == 3:
            r.dock()
        elif e.button == 8:
            go = False
        elif e.button == 5:
            calibrate()
        elif e.button == 7:
            rd.reset()
            reset()
        elif e.button == 9:
            r.safe()
            r.leds(255, 255)

def sampleRobot():
    """Samples the robot for common things like distance and angle"""
    return r.sample(roomba.LEFT_ENCODER, roomba.RIGHT_ENCODER)

font = pygame.font.Font('/Library/Fonts/Verdana.ttf', 24)
mode = (1024, 768)
screen = pygame.display.set_mode(mode)
surface = pygame.Surface(mode)
error_blob = pygame.Surface((100, 100))
pixel_offset = tuple(n / 2 for n in mode)


accuracy = 0.999
error = 1 - accuracy
error_rate = 0.00001
pygame.display.flip()

def updateDisplay(position):
    """Draws the Robot's new location on the display"""
    global error, accuracy
    position = tuple(-x / 10 for x in position)
    x, y = [ a + b for a, b in zip(position, pixel_offset) ]
    surface.set_at((int(x-1), int(y-1)), (255, 255, 255))
    surface.set_at((int(x-1), int(y+1)), (255, 255, 255))
    surface.set_at((int(x+1), int(y-1)), (255, 255, 255))
    surface.set_at((int(x+1), int(y+1)), (255, 255, 255))
    #error_blob.lock()
    #whole = 1.0
    #error_blob.fill((0, 0, 0))
    #parts = []
    #for i in range(10):
    #    part = whole * (1 - error)
    #    parts.append(part)
    #    whole -= part
    #for i in range(10):
    #    part = parts.pop()
    #    pygame.draw.circle(error_blob, (255 * part, 0, 0), (50, 50), 5*(10 - i))
    #error_blob.unlock()
    #surface.blit(error_blob, ((int(x), int(y))), None, BLEND_MAX)
    #accuracy *= (1 - error_rate)
    #error = 1 - accuracy
    #print error
    screen.blit(surface, (0, 0))
    text = font.render(repr(position), True, (255, 255, 255))
    screen.blit(text, (0, 0))
    if calibrating:
        text = font.render('Calibrating', True, (255, 0, 0))
        screen.blit(text, (0, 25))
    pygame.display.flip()

def sign(x):
    """Returns the sign of x, either 1 or -1"""
    if x == 0:
        return 1
    return int(x / abs(x))

def reset():
    """Resets the display"""
    surface.fill((0, 0, 0))

left, right = sampleRobot() # Zero out sensors
rd.initialize_priors((left, right))
start = before = time()


go = True
while go:
    left, right = sampleRobot()
    encoders = rd.normalize((left, right))
    encoders = tuple(-sign(m)*e for m, e in zip(motors, encoders))
    counts = tuple(a + b for a, b in zip(counts, encoders))
    print counts
    events = pygame.event.get()
    for e in events:
        processEvent(e)
    now = time()
    rd.update(encoders, now - before)
    before = now
    controlMotors()
    updateDisplay(rd.position())
    
r.close()
