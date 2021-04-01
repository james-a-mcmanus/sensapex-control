import os
os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")
import subprocess
import lvbt
from datetime import datetime 
import imp

logger = open("Imspector_Logging.txt","w")

I = imp.load_source('Imspex', 'Imspex.py')
proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

prepFolder = "D:\\JDoggyDog\\2021-03-31-P1"

# Setup device
setup = I.SetupParameters()
setup.x_axis = [[0,2674,14907], [2000,2674,14907]] # min max x
setup.y_axis = [[20193,83,16204], [20193,8237,16204]] # min max y
setup.z_axis = [[16325,12501,14907], [16325,12501,10000]] # min max z
setup.midpoint = [16030,12501,14907]
I.run_command(proc, setup)

logger.write("setup completed\n")

fname = I.get_fname()
fileroot = prepFolder + "\\" + fname
os.mkdir(fileroot)

logger.write("Directory Created\n")
logger.write("fname is :" + fname)
logger.write("\nFileroot is " + fileroot + "\n")
# Setup a Manipulator Command.
test =I.RunParameters()
test.run_type = "axis"
test.run_positions = "x_axis"
test.speed = 4000
test.filename = I.npzfilename(fileroot)
test.numframes = 100
test.framerate = 19.2

m = lvbt.measurement("Measurement 1")

logger.write("measurement created\n")

try:
    I.run_command(proc, test, m)
except:
    setup.save(fileroot + "setup.txt")
    test.save(fileroot + "run.txt")
    proc.kill()

setup.save(fileroot + "setup.txt")
test.save(fileroot + "run.txt")

logger.write("command sent\n")
m.export(prepFolder, fname)
logger.close()
proc.stdin.write("close\n")
proc.kill()
