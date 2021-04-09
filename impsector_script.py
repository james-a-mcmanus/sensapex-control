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

try:
	prepFolder = "D:\\JDoggyDog\\TEST2\\"
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
	y_manipulator.s.x_range = [0,10000]
	y_manipulator.s.y_range = [0,10000]
	y_manipulator.s.z_range = [0,10000]
	y_manipulator.s.midpoint = 5000
	y_manipulator.r.run_type = "axis"
	y_manipulator.r.run_positions = [[0,10000,10000],[10000,10000,10000]]


	x_manipulator = I.Manipulator()
	x_manipulator.s = y_manipulator.s
	x_manipulator.r.run_type = "midpoint"
	x_manipulator.r.run_positions = [[10000,0,10000],[10000,10000,10000]]


	table = lvbt.table("xyz-Table")
	m = lvbt.measurement("Measurement 1")
	#m = Measurement("Measurement 1", prepFolder)
	zrange = np.arange(-2, 2, 1)

	for zval in zrange:
		
		table.z(zval)

		I.run_stimulus_recording(prepFolder, m, grating, proc)
		I.run_manipulator_recording(prepFolder, m, whitescreen, y_manipulator, proc)
		I.run_manipulator_recording(prepFolder, m, whitescreen, x_manipulator, proc)
	grating.quit(proc)
finally:
	grating.quit(proc)
	proc.stdin.write("close\n")
	proc.kill()
	print("Finished Executing.")
