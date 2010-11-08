# This example moves servos on channel 0 and 10 at different speeds
# -- min
echo set chan 0,10 to 0.0 (speed=6)
pos 0  6 0.0
pos 10 6 0.0
sleep 0.65
# -- max
echo set chan 0,10 to 1.0 (speed=6)
pos 0  6 1.0
pos 10 6 1.0
sleep 0.65
# -- mid
echo set chan 0,10 to default (speed=9)
pos 0  9 default
pos 10 9 default
sleep 1.2
# -- min
echo set chan 0,10 to 0.0 (speed=12)
pos 0  12 0.0
pos 10 12 0.0
sleep 2.4
# -- max
echo set chan 0,10 to 1.0 (speed=6)
pos 0  6 1.0
pos 10 6 1.0
