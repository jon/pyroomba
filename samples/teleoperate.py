import sys
import pygame
import pyroomba

pygame.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

screen = pygame.display.set_mode((640, 480))

port = sys.argv[1]
print port

roomba = pyroomba.Roomba(port)

roomba.start()
roomba.safe()
roomba.stream_samples(pyroomba.sensors.LEFT_ENCODER, pyroomba.sensors.RIGHT_ENCODER, pyroomba.sensors.DISTANCE, pyroomba.sensors.ANGLE)

motors = [0, 0]

def set_motor(motor, value):
    global motors
    motors[motor] = value

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                set_motor(1, -255*event.value)    
            elif event.axis == 3:
                set_motor(0, -255*event.value)
    roomba.drive_pwm(*motors)
    try:
        print roomba.poll()
    except:
        print "Error"

