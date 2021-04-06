from sensapex import UMP
import numpy as np
from serial import Serial
import sys
import re
import ast
from math import ceil
import time
import logging

UMP.set_library_path(r"C:\Users\James\Downloads\umsdk-1.010-binaries\x64")
ump = UMP.get_ump()
device_list = ump.list_devices()
logging.basicConfig(filename='logs.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
sys.stderr = open('errors.txt', 'w')

if len(device_list) == 0:
    raise Exception("No devices found.")

MAX_SPEED=4000
MAX_REPS = 2
MAX_STEP=100
DEF_FRAMERATE = 30
DEF_NUMFRAMES = 100
comport = 'COM26'

class Device(object):
    """
    Main control device for the manipulator, implements movement + interaction with the Port
    """
    def __init__(self, device_id, com_port):

        self.manipulator = ump.get_device(device_id)
        #(min_x, min_y, min_z, max_x, max_y, max_z) = get_measurements(self.manipulator)
        self.x_axis = None
        self.y_axis = None
        self.z_axis = None
        self.midpoint = None
        self.port = Port(com_port, 115200)
        self.running = True

    def wait_for_finish(self, position_data):
        while self.manipulator.is_busy():
            position_data = np.vstack((position_data, np.array([time.perf_counter(), *np.array(self.manipulator.get_pos())])))
        return position_data

    def goto_halfway(self, speed=2):
        self.manipulator.goto_pos((self.x_axis.midpoint()[0], self.y_axis.midpoint()[1], self.z_axis.midpoint()[2]), speed=speed)
    
    def scan_axis(self, params):
        
        #setup
        axis = params.run_positions
        self.manipulator.goto_pos(axis.point1, speed=params.speed)
        self.wait_for_finish(np.empty((1,4),dtype=float))
        sys.stdout.write("READY" + "\n")
        sys.stdout.flush()
        positions = np.array([time.perf_counter(), *np.array(self.manipulator.get_pos())])
        self.port.wait_for_trigger()
        
        #run
        for target in [axis.point2, axis.point1] * params.numreps:
            self.manipulator.goto_pos(target, speed=params.speed)
            positions = self.wait_for_finish(positions)
        positions[:,0] = positions[:,0] - positions[0,0]
        return positions

    def scan_midpoint(self, params):
        axis = params.run_positions
        xmid = self.midpoint[0] 
        x1 = axis.point1[0]
        x2 = axis.point2[0]
        xlen = min(x1-xmid, x2-xmid)
        axis.point1[0] = xmid - xlen ##assume point1 is less than point2??
        axis.point2[0] = xmid + xlen
        return self.scan_axis(params)

    # scans along axis1, and then along axis2. 
    def scan_plane(self, axis1, axis2, speed, numreps, stepsize):
        assert intersection(axis1, axis2)
        self.manipulator.goto_pos(axis1.point1, speed=speed)
        self.wait_for_finish()
        steps = axis2.positions(stepsize)
        self.port.wait_for_trigger()
        for step in steps:
            self.scan_axis(axis1 + step, speed, numreps)

    async def get_pos(self, numpos):

        await self.manipulator.get_pos()

class Axis(object):
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.distance = np.linalg.norm(self.point1 - self.point2)

    def __add__(self, point):
        return Axis(self.point1 + point, self.point2 + point)
    
    def positions(self, numsteps):
        return np.linspace(self.point1, self.point2, numsteps)

    def midpoint(self):
        return (self.point2 - self.point1)/2

    def to_string(self):
        return str(self.point1) + " : " + str(self.point2)

class Plane(object):
    def __init__(self, point1, point2, point3, point4):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.point4 = point4

class Port(Serial):
    """
    Serial port to communicate triggering, aspects of the stimulus.
    """
    def __init__(self, comport, baudrate):
        super().__init__(comport, baudrate)
        if(self.isOpen() == False):
            self.open()
            self.read(400, timeout=1)
        self.messagedict = {"quit" : self.stimulus_quit, "save" : self.stimulus_save, "reset": self.stimulus_reset, "params": self.stimulus_parameters, "load": self.stimulus_load, "trigger": self.stimulus_lookfor_trigger}
        # maybe get initial_info

    def wait_for_trigger(self, params=None):
        Ported = False
        while not Ported:
            #while self.in_waiting:
            dat = self.read()
            #   print(dat)
            #   print(type(dat))
            if dat == b't':
                Ported = True # is this necessary? may save a couple us by removing.
                break

    def stimulus_quit(self, params=None):
        self.write(b'Q\n')

    def stimulus_save(self, params=None):
        self.write(b'S\n')

    def stimulus_reset(self, params=None):
        self.write(b'R\n')

    def stimulus_parameters(self, params):
        self.write(b'C\n')
        self.sendover(params.adaptionduration)
        self.sendover(params.xpos)
        self.sendover(params.ypos)
        self.sendover(params.xscale)
        self.sendover(params.yscale)
        self.sendover(params.adaptionduration)
        self.sendover(params.angle)
        self.sendover(params.framelength)
        self.sendover(params.whitebackground)
        self.sendover(params.inversecolor)
        self.sendover(params.externaltrigger)
        self.sendover(params.savevideo)
        self.sendover(params.repeatstim)

    def stimulus_load(self, params):
        self.write(b'L\n')
        self.sendover(params.filename)

    def stimulus_lookfor_trigger(self, params=None):
        self.write(b'T\n')

    def sendover(self, message):
        self.write(str.encode(str(message) + "\n"))

class Parameters(object):
    def parse_parameters(self, paramlist):
        for parameter in paramlist:
            parameter = parameter.split()
            paramtype = parameter[0]
            paramvalue = parameter[1:]
            self.parse_parameter(paramtype, paramvalue)
    def parse_parameter(self, ptype, pvalue):
        if ptype in self.__dict__.keys():
            self.__setattr__(ptype, parse(pvalue))
            sys.stdout.write(ptype + ": " + str(parse(pvalue)) + "\n")
        else:
            raise Exception("No attribute named: %s", ptype)
    def save(self, fname):
        with open(fname, 'w') as f:
            f.write('\n'.join(["parameters.%s = %s" % (k,v) for k,v in self.__dict__.items()]))

class SetupParameters(Parameters):
    def __init__(self):
        self.x_axis = None
        self.y_axis = None
        self.z_axis = None
        self.midpoint = None
        self.max_speed = None

    def axistype(self, property):
        if property in  ["max_speed", "midpoint"]:
            return False
        else:
            return True

    def run(self, device):
        # loop over the attributes and fix them up if they're axistypes. 
        for prop in self.__dict__.keys():
            if self.axistype(prop):
                ax_prop = getattr(self, prop)
                self.__setattr__(prop, Axis(np.array(ax_prop[0]), np.array(ax_prop[1])))

        for prop in self.__dict__.keys():
            setattr(device, prop, getattr(self, prop))

        sys.stdout.write("READY" + "\n")
        sys.stdout.flush()

class RunParameters(Parameters):
    def __init__(self):
        self.run_type = None
        self.run_positions = None
        self.speed = MAX_SPEED
        self.numreps = MAX_REPS
        self.stepsize = MAX_STEP
        self.framerate = None
        self.numframes = None
        self.filename = None
        self.timelimit = None

    def run(self, device):

        if self.run_type == "axis":
            runfun = device.scan_axis
        elif self.run_type == "midpoint":
            runfun = device.scan_midpoint
        else:
            logging.warning("Didn't understand that run command\n")

        self.stringoraxispositions(device)
        self.set_timings()
        positions = runfun(self)
        np.savez_compressed(self.filename, positions)
        return "Device Ran Successfully\n"

    def stringoraxispositions(self, device):
        if type(self.run_positions) == str:
            self.run_positions = getattr(device, self.run_positions)
        elif type(self.run_positions) == list:
            self.run_positions = Axis(np.array(self.run_positions[0]), np.array(self.run_positions[1]))

    def set_timings(self):
        if (self.numframes and self.framerate) is not None:
            self.timelimit = self.numframes / self.framerate # in seconds
            actual_distance = self.timelimit * self.speed # in um
            self.numreps = ceil(actual_distance / self.run_positions.distance) # find how many actual  repetitions we can do in that time.

    def save(self, fname):
        with open(fname, 'w') as f:
            f.write('\n'.join(["parameters.%s = %s" % (k,v) for k,v in self.__dict__.items()]))
            if type(self.run_positions) == Axis:
                f.write(self.run_positions.to_string())

class StimulusParameters(Parameters):
    def __init__(self):

        self.message = None
        self.adaptionduration = "0"
        self.xpos = "451"
        self.ypos = "519"
        self.xscale = "1"
        self.yscale = "600"
        self.angle = "203"
        self.framelength = "3"
        self.whitebackground = "0"
        self.inversecolor = "0"
        self.externaltrigger = "1"
        self.savevideo = "1"
        self.repeatstim = "1"

    def run(self, device):
        
        if self.message in device.port.messagedict:
            device.port.messagedict[message](self)
        else:
            raise Exception("That's not a valid command!")

def get_measurements(manipulator):
    input("minimum x position:")
    min_x = manipulator.get_pos(timeout=1)[0]
    input("maximum x position:")
    max_x = manipulator.get_pos()[0]
    input("minimum y position: ")
    min_y = manipulator.get_pos()[1]
    input("maximum y position: ")
    max_y = manipulator.get_pos()[1]
    input("minimum z position: ")
    min_z = manipulator.get_pos()[2]
    input("maximum z position: ")
    max_z = manipulator.get_pos()[2]
    return (min_x, min_y, min_z, max_x, max_y, max_z)

def intersection(axis1, axis2):
    return True
    # Do this later: https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect

def time_speed(d, speed):
    origin(d)
    d.wait_for_finish()
    t1 = time.perf_counter()
    d.manipulator.goto_pos(d.x_axis.point2, speed=speed)
    d.wait_for_finish()
    t2 = time.perf_counter()
    print("time elapsed: ", t2-t1)

def origin(d):
    d.manipulator.goto_pos(d.x_axis.point1, speed=5000)

def run_command(command, device):

    if "close" in command:
        device.close = True
        return "Closing\n"
    else:
        return parse_command(command, device)

def parse_command(commands, device):

    commands = commands.split("|")
    command_params = command_type(commands[0].strip())
    command_params.parse_parameters(commands[1:])
    return command_params.run(device)

def command_type(comtype):
    if comtype == "run":
        return RunParameters()
    elif comtype == "setup":
        return SetupParameters()
    elif comtype == "stimulus":
        return StimulusParameters()
    else:
        raise Exception("Couldn't determine command type: must be run, setup, or stimulus. You entered {}".format(comtype)) 

def parse(input_string):

    if type(input_string) == list and len(input_string) > 1:
        return [parse(item) for item in input_string]
    elif type(input_string) == list:
        input_string = input_string[0]

    if input_string == "":
        return None
    elif re.match("\A[0-9]+\.[0-9]+\Z", input_string):
        return float(input_string)
    elif re.match("\A[0-9]+\Z", input_string):
        return int(input_string)
    elif re.match("\A(true|false)\Z", input_string):
        return bool(input_string)
    elif re.match("\A\[+[0-9,.,\],\[,-]+\]\Z", input_string): #matches list looking type
        return ast.literal_eval(input_string)
    else:
        return input_string

def main(device):

    while device.running:
        command = sys.stdin.readline().rstrip()
        ret = run_command(command, device)
        sys.stdout.write("OVERANDOUT" + "\n")
        sys.stdout.flush()

d = Device(device_list[0], comport)
main(d)


#TODO:
# - SAVE MANIPULATOR LOCATIONS                      ✅
# - SCAN EQUAL ON BOTH SIDES RELATIVE TO MIDPOINT   ✅
# - WORK WITH IMSPECTOR                             ✅
# - TAKE MORE COMPLEX ARGUMENTS                     ✅
# - scan plane
# - only run as long as frames and fps              ✅
# - Imspector save and export to folder				✅
# - Turn get_measurements into a script in imspector(✅)
# - prevent any movement from occuring outside of those pre-determined axes.
# - change script to work with max and mins not the axes
# - build timeouts into the arduino scripts
# - change arduino scripts to communicate over extra serial pins.
# - Better error handling


