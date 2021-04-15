import os
os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")
import subprocess
import sys
import lvbt
from datetime import datetime 
import imp
import time
import numpy as np
import winsound
from math import ceil

I = imp.load_source('Imspex', 'Imspex.py')
proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
sys.stderr = open('imspector_error_logs.txt', 'w')
if proc is None:
	raise Exeception("couldn't open subprocess.")

try:
	prepFolder = "D:\\JDoggyDog\\2021-04-14-P4\\"
	if not os.path.isdir(prepFolder):
		os.mkdir(prepFolder)

	# setup microscope.
	table = lvbt.table("xyz-Table")
	m = lvbt.measurement("Measurement 1")
	zrange = np.arange(0,1, 1)

	# Setup a white screen.
	whitescreen = I.StimulusParameters()
	whitescreen.filename = "whitescreen.mat"
	whitescreen.savevideo = "0"
	whitescreen.externaltrigger = "1"
	whitescreen.repeatstim = "1"

	# Setup a grating
	grating = I.StimulusParameters()
	grating.filename = "Grating_2x1000y4000t1v20w.mat"
	grating_frames = 4000
	grating.savevideo = "1"
	grating.repeatstim = "0"
	grating.framelength = "0.1"
	grating_stim_time = grating_frames * float(grating.framelength)
	
	m.setProperty("Time Time Resolution", int(ceil(grating_stim_time * 26.7)))

	# setup a manipulator command.
	y_manipulator = I.Manipulator()
	y_manipulator.s.x_range = [0, 20000]
	y_manipulator.s.y_range = [3000,14184]
	y_manipulator.s.z_range = [12500,13301]
	y_manipulator.s.midpoint = 6267
	y_manipulator.r.run_type = "axis"
	y_manipulator.r.run_positions = [[0,6267,13300],[20000,6267,13300]]
	y_manipulator.r.numframes = 500
	y_manipulator.r.framerate = 26.7


	x_manipulator = I.Manipulator()
	x_manipulator.s = y_manipulator.s
	x_manipulator.r.run_type = "midpoint"
	x_manipulator.r.run_positions = [[6267,3000,13300],[6267,14183,13300]]
	x_manipulator.r.framerate = 26.7
	x_manipulator.r.numframes = 1000


	for zval in zrange:
		

		winsound.Beep(1000, 100)
		table.z(zval)
		time.sleep(1)

		I.run_stimulus_recording(prepFolder, m, grating, proc)
		print(grating.message)
		#I.run_manipulator_recording(prepFolder, m, whitescreen, y_manipulator, proc)
		#I.run_manipulator_recording(prepFolder, m, whitescreen, x_manipulator, proc)
		#I.run_stimulus_recording(prepFolder, m, whitescreen, proc)
	grating.quit(proc)
finally:
	grating.quit(proc)
	proc.stdin.write("close\n")
	proc.kill()
	winsound.Beep(1000, 2000)
