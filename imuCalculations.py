# Name: Hillel Chaitoff
# Calculations Module for the AltIMU-10v3
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
	# 1-Drop '0b' prefix
	# 2-Grab leading 4 digits
	# 3-Convert to float
	# 4-Multiply by gravity (9.81 m/s^2)
	return (float(bin(rawData)[2,-4], 2) * 9.81)

def getSpeed(v0, a, t):
	# Data returned in Meters-per-Second (no direction)
	return (v0 + (a * (t * 1000000)))