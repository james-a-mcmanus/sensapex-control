# imitate the old pc:

Messages:

'': Quit
'Q': Quit
'S': Save
'R': Reset
'C': Read the parameters. followed by the values for:
	- adaptionduration
	- xpos
	- ypos
	- xscale
	- pscale
	- angle
	- framelength
	- whitebackground
	- inversecolour
	- externaltrigger
	- savevideo
	- repeatstim
	- These are all ints
'L': Load. Followed by stimulus filename.
'T': trigger.



# Errors to check:
Do as many exception handling on the impsector side as possible - or otherwise work out why imspector doesn't record erros happening within a module...