# Name: Hillel Chaitoff
# 
# 

def convertGyro(rawData):
	# Data returned in Degrees-per-Second
	return rawData * 0.00875

def getOrientation(x1, x2, t):
	# Data returned in Degrees (changes in orientation)
	# x1: Degrees-per-Second
	# x2: Degrees-per-Second
	# t	: Time (microseconds)
	return ((x1 + x2) / (t * 1000000)) % 360

def convertAccel(rawData):
	# Data returned in Meters-per-Second-Squared
	return float(bin(rawData)[2,-4], 2)

def getSpeed(v0, a, t):
	# Data returned in Meters-per-Second (no direction)
	return (v0 + (a * (t * 1000000)))