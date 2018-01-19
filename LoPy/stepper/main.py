'''
200 steps/rev
8 mm/rev
0.04 mm/step
'''

from machine import Pin
from utime import sleep_us

halfperiod = 2000 # us (set to 2000 for 10 mm/s)

step = Pin('G22', mode=Pin.OUT)
dire = Pin('G28', mode=Pin.OUT)

m0 = Pin('G15', mode=Pin.OUT)
m1 = Pin('G16', mode=Pin.OUT)
m2 = Pin('G17', mode=Pin.OUT)

step(0)
dire(0)

def steps(nsteps, direction=0, mode=(0, 0, 0)):
    m2(mode[0])
    m1(mode[1])
    m0(mode[2])

    dire(direction)

    sleep_us(5000)
    for n in range(nsteps*2):
        step.toggle()
        sleep_us(halfperiod)

def move(dist, sense):
    nsteps = round(dist / 0.04)
    dist = nsteps * 0.04
    time = nsteps * 2 * halfperiod / 1e6
    speed = dist/time

    print('moving {:.2f} mm ({} steps) in {} s ({} mm/s)'.format(dist, nsteps, time, speed))

    steps(nsteps, sense)
