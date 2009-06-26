import sys
import math
from math import exp
from random import random
from time import sleep
from pyroomba import Roomba
from pyroomba.sensors import *

import signal

quitting_time = False

def quit(sig, stack):
	global quitting_time
	sys.stderr.write("Quitting...\n")
	quitting_time = True
	sys.exit()

signal.signal(signal.SIGINT, quit)

r = Roomba(sys.argv[1], 115200)
r.start()
r.safe()
r.full()
r.leds(128, 255)
r.pause_stream()
#r.stream_samples(CLIFF_LEFT_SIGNAL, CLIFF_RIGHT_SIGNAL, CLIFF_FRONT_LEFT_SIGNAL, CLIFF_FRONT_RIGHT_SIGNAL)

left = 0
right = 0

for x in range(50):
	sample = r.query_list(CLIFF_FRONT_LEFT_SIGNAL, CLIFF_FRONT_RIGHT_SIGNAL)
	left += sample['cliff_front_left_signal']
	right += sample['cliff_front_right_signal']

left /= 50.0
right /= 50.0
threshold_left = 2625
threshold_right = 2725
average_left = left
average_right = right

speed_fast = 250
speed_slow = 100

	
print "left\tright"

alpha = 1
alpha_long = 0.01

def back_off_right():
	r.drive_direct(-250, -250)
	sleep(0.5)
	r.drive_direct(250, 0)
	sleep(0.75)

def back_off_left():
	r.drive_direct(-250, -250)
	sleep(0.5)
	r.drive_direct(0, 250)
	sleep(0.75)

def back_off():
	if random() > 0.5:
		back_off_right()
	else:
		back_off_left()

def speed(avg, sample):
	return exp(.75 * (float(avg) / float(sample))) / math.e * speed_fast

while not quitting_time:
	try:
		#sample = r.poll()
		sample = r.query_list(CLIFF_FRONT_LEFT_SIGNAL, CLIFF_FRONT_RIGHT_SIGNAL, BUTTONS, BUMP_WHEEL_DROPS)
		if sample['buttons'] == 1:
			quitting_time = True
		s_left, s_right = sample['cliff_front_left_signal'], sample['cliff_front_right_signal']
		left = alpha*s_left + (1-alpha)*left
		average_left = alpha_long*s_left + (1-alpha_long)*average_left
		right = alpha*s_right + (1-alpha)*right
		average_right = alpha_long*s_right + (1-alpha_long)*average_right
		#left_speed = speed_slow if left > threshold_left else speed_fast
		#right_speed = speed_slow if right > threshold_right else speed_fast
		left_speed = speed(average_left, left)
		right_speed = speed(average_right, right)
		sample_str = "%d\t%d\t%d\t%d\t%f\t%f" % (left, right, average_left, average_right, left_speed, right_speed)
		bump = sample['bump_wheel_drops'] & 0x03
		drops = (sample['bump_wheel_drops'] & 0x0c) <> 0
		if bump == 0 and not drops:
			r.drive_direct(right_speed, left_speed)
		elif bump == 1:
			back_off_right()
		elif bump == 2:
			back_off_left()
		else:
			back_off()
		print sample_str
	except Exception, e:
		sys.stderr.write(str(e) + "\n");
		continue

r.drive_direct(0, 0)
