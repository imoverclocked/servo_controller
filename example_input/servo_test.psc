# set channels 0-15 to position "0.0"
# channel 0 is set at speed "5" which is slower than speed "0"
echo set position to 0.0
pos 0 5 0.0
pos 1 0 0.0
pos 2 0 0.0
pos 3 0 0.0
pos 4 0 0.0
pos 5 0 0.0
pos 6 0 0.0
pos 7 0 0.0
pos 8 0 0.0
pos 9 0 0.0
pos 10 0 0.0
pos 11 0 0.0
pos 12 0 0.0
pos 13 0 0.0
pos 14 0 0.0
pos 15 0 0.0
# Wait for all servos to get to their appropriate place
# 1.5 seconds is usually enough here
sleep 1.50
# set channels 0-15 to the position "1.0"
echo set position to 1.0
pos 0 0 1.0
pos 1 0 1.0
pos 2 0 1.0
pos 3 0 1.0
pos 4 0 1.0
pos 5 0 1.0
pos 6 0 1.0
pos 7 0 1.0
pos 8 0 1.0
pos 9 0 1.0
pos 10 0 1.0
pos 11 0 1.0
pos 12 0 1.0
pos 13 0 1.0
pos 14 0 1.0
pos 15 0 1.0
# wait for them to reach their position (1 second)
sleep 1
# set all channels to their default (or center) position
echo defaults
defaults
