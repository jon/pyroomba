# Your roomba sings the Katamari Theme!
# author: Erik Hollembeak

from pyroomba import *

katamariTheme  =  [70, 72, 74, 75, 74, 70, 65, 70, 65, 68, 70, 68, 67, 65]
katamariTiming =  [32, 16, 16, 16, 16, 16, 32, 32, 32, 32, 16, 16, 32, 32]

roomba = RoombaClassic('/dev/ttyUSB0')

roomba.start()
roomba.safe()
#ANGRY ROOMBA
roomba.leds(255, 255)

roomba.define_song(0, katamariTheme, katamariTiming)
roomba.play_song(0)
roomba.leds(0, 255)
roomba.close()
