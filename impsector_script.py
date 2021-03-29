import os
import subprocess
#import lvbt
from datetime import datetime

os.chdir(r"C:\Users\james\OneDrive\Sheffield\Building\Manipulator\Stimulus_Control")
command = "run | run_type axis | run_positions x_axis | speed 1000"

proc = subprocess.Popen('python Stimulus.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
proc.stdin.write(command)

m = lvbt.measurement("Measurement 1")

m.run()
print(proc.stdout.readline().rstrip())
proc.stdin.write("close\n")
proc.communicate()

def get_fname():
	return datetime.now().strftime("%Y%m%d%H%M_%S")

def run_command(process, command, measurement):
	fileroot = get_fname()
	command += npzfilename(fileroot)
	proc.stdin.write(command)

	# wait for ready command from device:
	deviceready = False
	while not deviceready:
		line = proc.stdout.readline().rstrip()
		deviceready = True if "READY" in line else False
	measurement.run()
	# then saev e


def npzfilename(base):
	return "| filename" + base + ".npz\n" 