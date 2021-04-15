"""
This file is a counterpart to the parameter objects in Stimulus. Designed to be run on python27, serialised, and then sent over to parameters in Stimulus.py
"""
from datetime import datetime
import sys
import os


#sys.stderr = open('Imspex_errors.txt', 'w')

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
        with open(fname, 'a') as f:
            f.write('\n'.join(["parameters.%s = %s" % (k,v) for k,v in self.__dict__.iteritems()]))
            f.write('\n')

    def run_command(self, process):
        process.stdin.write(self.serialise())
        deviceready = False
        while not deviceready:
            line = process.stdout.readline().rstrip()
            deviceready = True if "READY" in line else False

    def reset(self, process):
        pass

class Manipulator(Parameters):
    def __init__(self):
        self.s = SetupParameters()
        self.r = RunParameters()

    def setup(self, process):
        self.s.run_command(process)

    def trigger(self, process):
        self.r.run_command(process)

    def quit(self, process):
        process.stdin.write("close\n")

    def save(self, filename):
        with open(filename, 'w') as f:
            [v.save(filename) for k,v in self.__dict__.iteritems()]


class SetupParameters(Parameters):
    def __init__(self):
        self.x_axis = None
        self.y_axis = None
        self.z_axis = None
        self.x_range = None
        self.y_range = None
        self.z_range = None
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
        self.run_command(process)
        # load the parameters
        self.message = "params"
        self.run_command(process)
        
    def trigger(self, process):
        self.message = "trigger"
        self.run_command(process)

    def reset(self, process):
        self.message = "reset"
        self.run_command(process)

    def quit(self, process):
        self.message = "quit"
        self.run_command(process)

    def save(self, filename, process=None):
        with open(filename, 'a') as f:
            f.write('\n'.join(["parameters.%s = %s" % (k,v) for k,v in self.__dict__.iteritems()]))
            f.write('\n')
        if process is not None:
            self.message = "save"
            self.run_command(process)

def get_fname(fileroot=None):
    if fileroot is None:
        return datetime.now().strftime("%Y%m%d%H%M_%S")
    else:
        return fileroot + "\\" + datetime.now().strftime("%Y%m%d%H%M_%S")

def npzfilename(base):
    return base + ".npz" 


def generate_recordingfolder(prepFolder):
        basename = get_fname()
        recordingFolder = prepFolder + "\\" + basename + "\\"
        if not os.path.isdir(recordingFolder):
            os.mkdir(recordingFolder)
        return (recordingFolder, basename)

def run_stimulus_recording(prepFolder, measurement, stimobj, proc):
    recordingFolder, basename = generate_recordingfolder(prepFolder)
    stimobj.setup(proc)
    stimobj.trigger(proc)
    measurement.run()
    measurement.export(recordingFolder, basename)
    stimobj.save(recordingFolder + basename + "_stimulus.txt", proc)
    #stimobj.reset(proc)

def run_manipulator_recording(prepFolder, measurement, stimobj, manobj, proc):
    recordingFolder, basename = generate_recordingfolder(prepFolder)
    manobj.r.filename = recordingFolder + basename + "_manipulator_positons.npz"
    manobj.setup(proc)
    stimobj.setup(proc)
    stimobj.trigger(proc)
    manobj.trigger(proc)
    measurement.run()
    measurement.export(recordingFolder, basename)
    manobj.save(recordingFolder + basename + "_manipulator_parameters.txt")
    stimobj.reset(proc)


possible_messages = ["quit", "save", "reset", "params", "load", "trigger"]

