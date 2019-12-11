import time

startTime = ''

while True:
    if not startTime:
        startTime = time.time()
        print('Timer started!')
    if time.time()-startTime > 2.5:
        #currentTime = time.time()
        #print('Time Elapsed= {}'.format(currentTime-startTime))
        print('Ejla')

