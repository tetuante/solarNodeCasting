'''
Linear rail:
- 200 steps/rev
- 8 mm/rev
- 0.04 mm/step

Rotary platform:
- 200 steps/rev
- 1.8 or 0.9 deg/step
'''

from machine import Pin
from utime import sleep_us

halfperiod = 2000 # us, half the time needed per step

step = Pin('G22', mode=Pin.OUT) # STEP pin
dire = Pin('G28', mode=Pin.OUT) # DIR pin

'''
These 3 pins set the step mode. However, only full step mode (0, 0, 0)
works properly with this stepper motor (MT-2303HS280AW)
'''
m0 = Pin('G15', mode=Pin.OUT)
m1 = Pin('G16', mode=Pin.OUT)
m2 = Pin('G17', mode=Pin.OUT)

'''
Set STEP and DIR to low
'''
step(0)
dire(0)

'''
Function to drive the stepper motor
'''
def steps(nsteps, direction, mode=(0, 0, 0)):
    m2(mode[0])
    m1(mode[1])
    m0(mode[2])

    dire(direction)

    sleep_us(5000)
    for n in range(nsteps*2):
        step.toggle()
        sleep_us(halfperiod)

'''
Based on steps() function. This function moves the linear rail according to
the parameters passed as arguments
'''
def move(dist, sense):
    nsteps = round(dist / 0.04)
    dist = nsteps * 0.04
    time = nsteps * 2 * halfperiod / 1e6
    speed = dist/time

    print('moving {:.2f} mm ({} steps) in {} s ({} mm/s)'.format(dist, nsteps, time, speed))

    steps(nsteps, sense)

'''
Based on steps() function. This function rotates the rotary platform according
to the parameters passed as arguments. Note that a ratio can be given depending on
the timing pulley used
'''
def rotate(angle, sense, ratio=2):
    deg_per_step = 1.8 / ratio
    nsteps = round(angle / deg_per_step)
    angle = nsteps * deg_per_step
    time = nsteps * 2 * halfperiod / 1e6
    ang_speed = angle/time

    print('rotating {:.2f} deg ({} steps) in {} s ({} deg/s)'.format(angle, nsteps, time, ang_speed))

    steps(nsteps, sense)
