os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")

import os
import subprocess
#import lvbt
from datetime import datetime
import Imspex

testcommand = "run | run_type axis | run_positions x_axis | speed 1000"

proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
proc.stdin.write(command)

m = lvbt.measurement("Measurement 1")


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
		commandended = True if "OVERANDOUT"	in line else False
	
	# then save the measurement.


def npzfilename(base):
	return "| filename" + base + ".npz\n" 