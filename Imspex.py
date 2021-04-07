"""
This file is a counterpart to the parameter objects in Stimulus. Designed to be run on python27, serialised, and then sent over to parameters in Stimulus.py
"""
from datetime import datetime
import sys


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
            f.write('\n'.join(["parameters.%s = %s" % (k,v) for k,v in self.__dict__.iteritems()]))

class SetupParameters(Parameters):
    def __init__(self):
        self.x_axis = None
        self.y_axis = None
        self.z_axis = None
        self.midpoint = None
        self.max_speed = None
    
    def serialise(self):
        """
        Pass any object that is not none into an output string to send to the Stimulus script.
        """
        outstring = "setup"
        properties = self.__dict__
        for prop in properties:
            attr = getattr(self, prop)
            outstring = (outstring + " | " + str(prop) + " " + self.tostring(attr))  if (attr is not None) else outstring
        return outstring + "\n"

    def tostring(self,var):
        if type(var) is list:
            return str(var).replace(" ","")
        else:
            return str(var)

class RunParameters(Parameters):
    
    def __init__(self):
        self.run_type = None
        self.run_positions = None
        self.speed = None
        self.numreps = None
        self.stepsize = None
        self.framerate = None
        self.numframes = None
        self.filename = None
        self.timelimit = None

    def serialise(self):
        """
        Pass any object that is not none into an output string to send to the Stimulus script.
        """
        outstring = "run"
        properties = self.__dict__
        for prop in properties:
            attr = getattr(self, prop)
            outstring = (outstring + " | " + str(prop) + " " + self.tostring(attr))  if (attr is not None) else outstring
        return outstring + "\n"

    def tostring(self,var):

        if type(var) is list:
            return str(var).replace(" ","")
        else:
            return str(var)

class StimulusParameters(Parameters):
    def __init__(self):

        self.message = None
        self.adaptionduration = None
        self.xpos = None
        self.ypos = None
        self.xscale = None
        self.yscale = None
        self.angle = None
        self.framelength = None
        self.filename = None
        self.whitebackground = None
        self.inversecolor = None
        self.externaltrigger = None
        self.savevideo = None
        self.repeatstim = None

    def serialise(self):
        outstring = "stimulus"
        properties = self.__dict__
        for prop in properties:
            attr = getattr(self, prop)
            outstring = (outstring + " | " + str(prop) + " " + self.tostring(attr))  if (attr is not None) else outstring
        return outstring + "\n"

    def tostring(self, var):
        return str(var)

    def setup(self, process):
        # load the file
        self.message = "load"
        run_command(process, self)
        # load the parameters
        self.message = "params"
        run_command(process, self)
        # get ready to run.
        self.message = "trigger"

def get_fname():
    return datetime.now().strftime("%Y%m%d%H%M_%S")

def run_command(process, command, measurement=None):


    process.stdin.write(command.serialise())
    # wait for ready command from device:
    deviceready = False
    while not deviceready:
        line = process.stdout.readline().rstrip()
        deviceready = True if "READY" in line else False
    if measurement is not None:
        measurement.run()
        commandended = False
        while not commandended:
            line = process.stdout.readline().rstrip()
            print(line)
            commandended = True if "OVERANDOUT" in line else False

def npzfilename(base):
    return base + ".npz" 



possible_messages = ["quit", "save", "reset", "params", "load", "trigger"]