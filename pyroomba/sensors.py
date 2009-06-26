# Sensor definitions
BUMP_WHEEL_DROPS = (7, 'B', 'bump_wheel_drops')
WALL = (8, 'B', 'wall')

CLIFF_LEFT = (9, 'B', 'cliff_left')
CLIFF_FRONT_LEFT = (10, 'B', 'cliff_front_left')
CLIFF_FRONT_RIGHT = (11, 'B', 'cliff_front_right')
CLIFF_RIGHT = (12, 'B', 'cliff_right')

VIRTUAL_WALL = (13, 'B', 'virtual_wall')

WHEEL_OVERCURRENT = (14, 'B', 'wheel_overcurrent')

DIRT_DETECT = (15, 'B', 'dirt_detect')

IR_CHARACTER_OMNI = (17, 'B', 'ir_character_omni')
IR_CHARACTER_LEFT = (52, 'B', 'ir_character_left')
IR_CHARACTER_RIGHT = (53, 'B', 'ir_character_left')

BUTTONS = (18, 'B', 'buttons')

DISTANCE = (19, 'h', 'distance')
ANGLE = (20, 'h', 'angle')
CHARGING_STATE = (21, 'B', 'charging_state')

VOLTAGE = (22, 'H', 'voltage')
CURRENT = (23, 'h', 'current')
TEMPERATURE = (24, 'b', 'temperature')
BATTERY_CHARGE = (25, 'H', 'battery_charge')
BATTERY_CAPACITY = (26, 'H', 'battery_capacity')

WALL_SIGNAL = (27, 'H', 'wall_signal')

CLIFF_LEFT_SIGNAL = (28, 'H', 'cliff_left_signal')
CLIFF_FRONT_LEFT_SIGNAL = (29, 'H', 'cliff_front_left_signal')
CLIFF_FRONT_RIGHT_SIGNAL = (30, 'H', 'cliff_front_right_signal')
CLIFF_RIGHT_SIGNAL = (31, 'H', 'cliff_right_signal')

CHARGING_SOURCES_AVAILABLE = (34, 'B', 'charging_sources_available')

OI_MODE = (35, 'B', 'oi_mode')

SONG_NUMBER = (36, 'B', 'song_number')
SONG_PLAYING = (37, 'B', 'song_playing')

STREAM_PACKETS = (38, 'B', 'stream_packets')

REQUESTED_VELOCITY = (39, 'h', 'requested_velocity')
REQUESTED_RADIUS = (40, 'h', 'requested_radius')
REQUESTED_RIGHT_VELOCITY = (41, 'h', 'requested_right_velocity')
REQUESTED_LEFT_VELOCITY = (42, 'h', 'requested_left_velocity')

RIGHT_ENCODER = (43, 'H', 'right_encoder')
LEFT_ENCODER = (44, 'H', 'left_encoder')

LIGHT_BUMPER = (45, 'B', 'light_bumper')
LIGHT_BUMP_LEFT = (46, 'H', 'light_bump_left')
LIGHT_BUMP_FRONT_LEFT = (47, 'H', 'light_bump_front_left')
LIGHT_BUMP_CENTER_LEFT = (48, 'H', 'light_bump_center_left')
LIGHT_BUMP_CENTER_RIGHT = (49, 'H', 'light_bump_center_right')
LIGHT_BUMP_FRONT_RIGHT = (50, 'H', 'light_bump_front_right')

LEFT_MOTOR_CURRENT = (54, 'h', 'left_motor_current')
RIGHT_MOTOR_CURRENT = (55, 'h', 'right_motor_Current')
MAIN_BRUSH_MOTOR_CURRENT = (56, 'h', 'main_brush_motor_current')
SIDE_BRUSH_MOTOR_CURRENT = (57, 'h', 'side_brush_motor_current')

STASIS = (58, 'B', 'stasis')

# Bulk packet definitions
ALL_SCI = (0, [
    BUMP_WHEEL_DROPS,
    WALL,
    CLIFF_LEFT,
    CLIFF_FRONT_LEFT,
    CLIFF_FRONT_RIGHT,
    CLIFF_RIGHT,
    VIRTUAL_WALL,
    WHEEL_OVERCURRENT,
    DIRT_DETECT,
    DIRT_DETECT,
    IR_CHARACTER_OMNI,
    BUTTONS,
    DISTANCE,
    ANGLE,
    CHARGING_STATE,
    VOLTAGE,
    CURRENT,
    TEMPERATURE,
    BATTERY_CHARGE,
    BATTERY_CAPACITY
], 'all_sci')

SENSORS = [
   BUMP_WHEEL_DROPS,
    WALL,
    CLIFF_LEFT,
    CLIFF_FRONT_LEFT,
    CLIFF_FRONT_RIGHT,
    CLIFF_RIGHT,
    VIRTUAL_WALL,
    WHEEL_OVERCURRENT,
    DIRT_DETECT,
    IR_CHARACTER_OMNI,
    IR_CHARACTER_LEFT,
    IR_CHARACTER_RIGHT,
    BUTTONS,
    DISTANCE,
    ANGLE,
    CHARGING_STATE,
    VOLTAGE,
    CURRENT,
    TEMPERATURE,
    BATTERY_CHARGE,
    BATTERY_CAPACITY,
    WALL_SIGNAL,
    CLIFF_LEFT,
    CLIFF_FRONT_LEFT,
    CLIFF_FRONT_RIGHT,
    CLIFF_RIGHT,
    CLIFF_LEFT_SIGNAL,
    CLIFF_FRONT_LEFT_SIGNAL,
    CLIFF_FRONT_RIGHT_SIGNAL,
    CLIFF_RIGHT_SIGNAL,
    CHARGING_SOURCES_AVAILABLE,
    OI_MODE,
    SONG_NUMBER,
    SONG_PLAYING,
    STREAM_PACKETS,
    REQUESTED_VELOCITY,
    REQUESTED_RADIUS,
    REQUESTED_RIGHT_VELOCITY,
    REQUESTED_LEFT_VELOCITY,
    RIGHT_ENCODER,
    LEFT_ENCODER,
    LIGHT_BUMPER,
    LIGHT_BUMP_LEFT,
    LIGHT_BUMP_FRONT_LEFT,
    LIGHT_BUMP_CENTER_LEFT,
    LIGHT_BUMP_CENTER_RIGHT,
    LIGHT_BUMP_FRONT_RIGHT,
    LEFT_MOTOR_CURRENT,
    RIGHT_MOTOR_CURRENT,
    MAIN_BRUSH_MOTOR_CURRENT,
    SIDE_BRUSH_MOTOR_CURRENT,
    STASIS
]

SENSOR_ID_MAP = dict([ (sensor[0], sensor) for sensor in SENSORS ])
SENSOR_NAME_MAP = dict([ (sensor[2], sensor) for sensor in SENSORS])
