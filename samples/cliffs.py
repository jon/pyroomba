import sys
import math
from math import sqrt
from random import random
from time import sleep
from pyroomba import Roomba
from pyroomba.sensors import *

import atexit
import signal

quitting_time = False
alpha = .50
max_speed = 250
average_speed = 200
bias_scale = .7
slow_factor = 3.5
history = 10

def quit(sig, stack):
	global quitting_time
	sys.stderr.write("Quitting...\n")
	quitting_time = True

signal.signal(signal.SIGINT, quit)

def mean(list):
	return sum(list) / float(len(list))

def stdev(list):
	mu = mean(list)
	return sqrt(sum([ (x - mu)*(x - mu) for x in list ]) / float(len(list) - 1))

def stdevs(sample, list):
	return (sample - mean(list)) / stdev(list)

def sample_stdevs(left, right):
	lefts = [ s[0] for s in samples ]
	rights = [ s[1] for s in samples ]
	return (stdevs(left, lefts), stdevs(right, rights))

samples = []
def append_sample(left, right):
	global samples
	samples.append((left, right))
	if len(samples) > history:
		samples = samples[1:]

def speed(value, samples):
	return max_speed
	distance = (value - mean(samples)) / stdev(samples)
	return max_speed if distance < 3 else (max_speed / slow_factor)

def distance(speed):
	return (max_speed / speed) - 1.0

def speeds(left, right):
	lefts = [ s[0] for s in samples ]
	rights = [ s[1] for s in samples ]
	return (speed(left, lefts), speed(right, rights))

offset = 0
def alt_speeds(left, right, far_left, far_right):
	global offset
	samples = [ far_left, left, right, far_right ]
	average = (sum(samples) - max(samples)) / 3.0
	if (far_left > 2800 or left > 2800) and (far_right > 2800 or right > 2800):
		return (.5*average_speed, .5*average_speed)
	if max(samples) > 2550 and max(samples) > (1.1 * average):
		bias = samples.index(max(samples)) - 1.5
		target_offset = bias * bias_scale * average_speed
	else:
		target_offset = 0
	offset = alpha*target_offset + (1-alpha)*offset
	return (average_speed + offset, average_speed - offset)
		



r = Roomba(sys.argv[1], 115200)
r.start()
r.safe()
r.full()
r.leds(128, 255)
r.pause_stream()

print "front left\tfront right\tleft\tright\tv_left\tv_right\td_left\td_right"

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

def take_sample():
	sample = r.query_list(CLIFF_FRONT_LEFT_SIGNAL, CLIFF_FRONT_RIGHT_SIGNAL, BUTTONS, BUMP_WHEEL_DROPS)
	return (sample['cliff_front_left_signal'], sample['cliff_front_right_signal'], sample['bump_wheel_drops'] & 0x03, (sample['bump_wheel_drops'] & 0x0c) <> 0)


r.drive_direct(max_speed / slow_factor, max_speed / slow_factor)
for x in range(history):
	left, right, bump, drops = take_sample()
	append_sample(left, right)

def stop_robot():
	r.drive_direct(0, 0)

atexit.register(stop_robot)

while not quitting_time:
	try:
		sample = r.query_list(CLIFF_FRONT_LEFT_SIGNAL, CLIFF_FRONT_RIGHT_SIGNAL, CLIFF_LEFT_SIGNAL, CLIFF_RIGHT_SIGNAL, BUTTONS, BUMP_WHEEL_DROPS)
		if sample['buttons'] == 1:
			quitting_time = True
		left, right, far_left, far_right = sample['cliff_front_left_signal'], sample['cliff_front_right_signal'], sample['cliff_left_signal'], sample['cliff_right_signal']
		left_speed, right_speed = speeds(left, right)
		left_stdev, right_stdev = sample_stdevs(left, right)
		append_sample(left, right)
		sample_str = "%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f" % (left, right, sample['cliff_left_signal'], sample['cliff_right_signal'], left_speed, right_speed, left_stdev, right_stdev)

		left_speed, right_speed = alt_speeds(left, right, far_left, far_right)

		bump = sample['bump_wheel_drops'] & 0x03
		drops = (sample['bump_wheel_drops'] & 0x0c) <> 0
		if bump == 0 and not drops:
			r.drive_direct(right_speed, left_speed)
		elif drops:
			r.drive_direct(0, 0)
		elif bump == 1:
			back_off_right()
		elif bump == 2:
			back_off_left()
		else:
			back_off()
		print sample_str
	except:
		continue

r.drive_direct(0, 0)

