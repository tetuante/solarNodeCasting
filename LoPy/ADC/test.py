'''
This for-loop tests the influence of the sampling period in the measurements.
'''
for i in range(0,1000):
    print(i)
    measure(5000,i*10)
