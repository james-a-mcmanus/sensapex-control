import os
os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")
import subprocess
import sys
import lvbt
from datetime import datetime 
import imp
import time
import numpy as np

I = imp.load_source('Imspex', 'Imspex.py')
proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
sys.stderr = open('imspector_error_logs.txt', 'w')
if proc is None:
	raise Exeception("couldn't open subprocess.")

try:
	prepFolder = "D:\\JDoggyDog\\TEST5\\"
	if not os.path.isdir(prepFolder):
		os.mkdir(prepFolder)


	# Setup a white screen.
	whitescreen = I.StimulusParameters()
	whitescreen.filename = "whitescreen.mat"
	whitescreen.savevideo = "0"
	whitescreen.externaltrigger = "1"
	whitescreen.repeatstim = "1"

	# Setup a grating
	grating = I.StimulusParameters()
	grating.filename = "Grating_2x1000y4000t1v20w.mat"
	grating.savevideo = "0"

	# setup a manipulator command.
	y_manipulator = I.Manipulator()
	y_manipulator.s.x_range = [0, 20000]
	y_manipulator.s.y_range = [939,14184]
	y_manipulator.s.z_range = [12500,14227]
	y_manipulator.s.midpoint = 7342
	y_manipulator.r.run_type = "axis"
	y_manipulator.r.run_positions = [[0,7342,13000],[20000,7342,13000]]
	y_manipulator.r.numframes = 100
	y_manipulator.r.framerate = 15.3


	x_manipulator = I.Manipulator()
	x_manipulator.s = y_manipulator.s
	x_manipulator.r.run_type = "midpoint"
	x_manipulator.r.run_positions = [[7342,940,13000],[7342,14183,13000]]
	x_manipulator.r.framerate = 15.3
	x_manipulator.r.numframes = 100


	table = lvbt.table("xyz-Table")
	m = lvbt.measurement("Measurement 1")
	zrange = np.arange(-2, 4, 2)

	for zval in zrange:
		
		table.z(zval)
		time.sleep(1)

		I.run_stimulus_recording(prepFolder, m, grating, proc)
		I.run_manipulator_recording(prepFolder, m, whitescreen, y_manipulator, proc)
		I.run_manipulator_recording(prepFolder, m, whitescreen, x_manipulator, proc)
	grating.quit(proc)
finally:
	grating.quit(proc)
	proc.stdin.write("close\n")
	proc.kill()
	print("Finished Executing.")
