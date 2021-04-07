import os
os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")
import subprocess
import lvbt
from datetime import datetime 
import imp

I = imp.load_source('Imspex', 'Imspex.py')
proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

prepFolder = "D:\\JDoggyDog\\2021-03-31-P1"

fname = I.get_fname()
fileroot = prepFolder + "\\" + fname
os.mkdir(fileroot)

# Setup device
setup = I.SetupParameters()
setup.x_axis = [[0,2674,14907], [2000,2674,14907]] # min max x
setup.y_axis = [[20193,83,16204], [20193,8237,16204]] # min max y
setup.z_axis = [[16325,12501,14907], [16325,12501,10000]] # min max z
setup.midpoint = [16030,12501,14907]
I.run_command(proc, setup)

# Setup a Manipulator Command.
test =I.RunParameters()
test.run_type = "axis"
test.run_positions = "x_axis"
test.speed = 4000
test.filename = I.npzfilename(fileroot)
test.numframes = 100
test.framerate = 19.2

# Setup a stimulus command.
stimulus = I.StimulusParameters()
stimulus.filename = "whitescreen.mat"
stimulus.externaltrigger = "1"
stimulus.setup(proc)

m = lvbt.measurement("Measurement 1")

try:
    I.run_command(proc, test, m)
except:
    setup.save(fileroot + "setup.txt")
    test.save(fileroot + "run.txt")
    stimulus.save(fileroot + "stimulus.txt")
    proc.kill()

setup.save(fileroot + "setup.txt")
test.save(fileroot + "run.txt")
stimulus.save(fileroot + "stimulus.txt")

m.export(prepFolder, fname)
proc.stdin.write("close\n")
proc.kill()
