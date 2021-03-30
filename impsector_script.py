import os
os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")

import subprocess
#import lvbt
from datetime import datetime
from Imspex import *

def get_fname():
	return datetime.now().strftime("%Y%m%d%H%M_%S")

def run_command(process, command, measurement):
	fileroot = get_fname()
	command.filename = npzfilename(fileroot)
	proc.stdin.write(command.serialise())

	# wait for ready command from device:
	deviceready = False
	while not deviceready:
		line = proc.stdout.readline().rstrip()
		deviceready = True if "READY" in line else False
	measurement.run()
	
	commandended = False
	while not commandended:
		line = stdout.readline().rstrip()
		print(line)
		commandended = True if "OVERANDOUT"	in line else False

		# then save the measurement.

def npzfilename(base):
	return "| filename" + base + ".npz\n" 


test = RunParameters()
test.run_type = "axis"
test.run_positions = "x_axis"
test.speed = 4000

proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
m = lvbt.measurement("Measurement 1")

run_command(proc, test, m)

