"""
This file is a counterpart to the parameter objects in Stimulus. Designed to be run on python27, serialised, and then sent over to parameters in Stimulus.py
"""

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