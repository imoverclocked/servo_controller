# This exemplifies the limits that can be placed for more generic command sets
# this assumes the controller is attached to a hand and servos are controlling
# it.

# give each servo a human recognizable name
##         name    chan
#  two pinky finger servos
chan_alias pinky1  0
chan_alias pinky2  1
#  two ring finger servos
chan_alias ring1   2
chan_alias ring2   3
#  two middle finger servos
chan_alias middle1 4
chan_alias middle2 5
#  two index finger servos
chan_alias index1  6
chan_alias index2  7
#  three thumb finger servos
chan_alias thumb1  8
chan_alias thumb2  9
chan_alias thumb3  10

#  set valid servo min/max values for each digit
#          name    min max  default
chan_range pinky1  320 1180 750
chan_range pinky2  320 1180 750
chan_range ring1   320 1180 750
chan_range ring2   320 1180 750
chan_range middle1 320 1180 750
chan_range middle2 320 1180 750
chan_range index1  320 1180 750
chan_range index2  320 1180 750
chan_range thumb1  320 1180 750
chan_range thumb2  320 1180 750
chan_range thumb3  320 1180 750

# Exercise pinky (quickly)
echo Exercise pinky quickly
pos pinky1 0 0.0
pos pinky2 0 0.0
sleep .75
pos pinky1 0 1.0
pos pinky2 0 1.0
sleep .75
# put pinky in default position
pos pinky1 0 default
pos pinky2 0 default
sleep .75

# Exercise pinky (slowly)
echo Exercise pinky slowly
pos pinky1 7 0.0
pos pinky2 7 0.0
sleep 1.5
pos pinky1 7 1.0
pos pinky2 7 1.0
sleep 1.5
# put pinky in default position
pos pinky1 7 0.5
pos pinky2 7 0.5
sleep 1.5

# Exercise hand (faily quickly)
echo Exercise hand quickly
pos pinky1  5 0.0
pos pinky2  5 0.0
pos ring1   5 0.0
pos ring2   5 0.0
pos middle1 5 0.0
pos middle2 5 0.0
pos index1  5 0.0
pos index2  5 0.0
pos thumb1  5 0.0
pos thumb2  5 0.0
pos thumb3  5 0.0
sleep 1.25
pos pinky1  5 1.0
pos pinky2  5 1.0
pos ring1   5 1.0
pos ring2   5 1.0
pos middle1 5 1.0
pos middle2 5 1.0
pos index1  5 1.0
pos index2  5 1.0
pos thumb1  5 1.0
pos thumb2  5 1.0
pos thumb3  5 1.0
sleep 1.25

# put hand in default position
pos pinky1  5 default
pos pinky2  5 default
pos ring1   5 default
pos ring2   5 default
pos middle1 5 default
pos middle2 5 default
pos index1  5 default
pos index2  5 default
pos thumb1  5 default
pos thumb2  5 default
pos thumb3  5 default
sleep 1
