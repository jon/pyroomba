# Modulate LED color and intensity with respect to time
# author: Erik Hollembeak

from pyroomba import *
from time import sleep

roomba = RoombaClassic('/dev/ttyUSB0')

roomba.start()
roomba.safe()

roomba.leds(0, 0)

for i in range(0, 256):
    roomba.leds(255 - i, i)
    sleep(0.01)

roomba.close()

