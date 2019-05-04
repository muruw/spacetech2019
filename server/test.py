import sys
from time import sleep

#print("This is the name of the script: ", sys.argv[0])
#print("Number of arguments: ", len(sys.argv))
#print("The arguments are: " , str(sys.argv))

x1 = 659344

for i in range(10):
   print('[{"x": ' + str(x1) + ', "y": 6474159, "type": "mm-wave"}, {"x": 659572.0000000093, "y": 6473747.999999776, "type": "small-cell"}]')

   x1 += 1

   sleep(1)

#print('[{"x": 659344, "y": 6474159, "type": "mm-wave"}, {"x": 659572.0000000093, "y": 6473747.999999776, "type": "small-cell"}]')

#sleep(2)

#print('[{"x": 659354, "y": 6474159, "type": "mm-wave"}, {"x": 659522.0000000093, "y": 6473727.999999776, "type": "small-cell"}]')