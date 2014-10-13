# Name: Hillel Chaitoff
# Date: 10/13/2014
# Updated: 
# NOTE:	Add configuration file for reading in settings: Serial Setup, Socket Setup, 

import sys
import serial
import socket
import time
from collections import namedtuple
from sys import argv as cmdLineArgs

###--- Determine if in Debug ---###
if len(cmdLineArgs) > 1:
	if (cmdLineArgs[1]) == 'debug':
		inDebug = True
	else:
		inDebug = False

###--- Read Configuration Files and Store Data---###
# Containers
serialSetupData = namedtuple('serialData', 'comport baudeRate timeout')
socketSetupData = namedtuple('socketData', 'hostName hostPort')
# Serial Setup
comport = '/dev/ttyUSB0'
baudeRate = 9600
timeout = 1
serialSetup = serialSetupData(comport=comport, baudeRate=baudeRate, timeout=timeout)
# Socket Setup
hostName = 'http://ServerAddress.com'
hostPort = 8080
socketSetup = socketSetupData(hostName=hostName, hostPort=hostPort)
# Rocket & Launcher Address Code Pairs
allAddressCodes = []


###--- General Functions ---###
# Debug Print
# Logging
def logit(content='', location='', fileName='', debug=False):
	destination = location + '/' + fileName
	with open(destination, 'a') as logfile:	# Append to the logfile
		logfile.write(content +'\n')
	if debug:
		print content


###--- Setup Functions ---###
# Setup Serial (XBee)
def serial_setup(comport, baudeRate, timeout, allAddressCodes):
	try:
		xbee = serial.Serial(comport, baudeRate, timeout=timeout)
	except Exception, e:
		logit('SERIAL_SETUP: ' + str(e), location, fileName, debug=inDebug)
	# Send messge to each rocket & launcher pairing
	# Wait for return message from each rocket & launcher pairing
	# For each addressCode in allAddressCodes:
	#	RL_setupMessage = {'serial_setup':str(addressCode)}
	#	xbee.write(RL_setupMessage)
	# Wait for a Response Message from the Rocket & Launcher pair
	#	waitingForReturnMessage = True
	#	while(waitingForReturnMessage):
	#		if (len(xbee.read()) > 0):
	#			RL_setupResponse = xbee.read()
	#			if (RL_setupResponse == EXPECTED_RESPONSE):
	#				waitingForReturnMessage = False
	#			
	#	If successful pair of return messages:
	#		Log 'SUCCESS: XBee Communication RL[12345, 67890, abcde]'
	#	Else:
	#		Log 'FAIL: XBee Communication R[12345, abcde] L[12345]'
	return xbee

# Setup Socket (Command Center's AWS Server)
def socket_setup(hostName, hostPort):
	# Setup the Socket for Server Connection
	try:
		server = socket.Socket(socket.AF_INET, socket.SOCK_STREAM)
	except Exception, e:
		logit('SOCKET_SETUP: ' + str(e), location, fileName, debug=inDebug)
	# Connect to the Server
	try:
		server.connect(hostName, hostPort)
	except Exception, e:
		logit('SOCKET_SETUP: ' + str(e), location, fileName, debug=inDebug)
	return server


###--- Communication Commands ---###
# Launch
def launch(addressCode):
	# Send Launch with Address Code
	# Wait for Launch Confirmation
	# If Launch Confirmed:
	#	launchConfirmationMessage = {addressCode:True}
	# Else:
	#	launchConfirmationMessage = {addressCode:Fail}
	# return launchConfirmationMessage

# Forward the Data from the Rocket
def forward_rocket_data():


###--- Processes ---###
# Initialization
def initialization_process():
	# Connect Pi to Server
	socket_setup(serialSetupData.comport, serialSetupData.baudeRate, serialSetupData.timeout)
	# Connect Launchers and Rockets to Pi
	serial_setup(socketSetupData.hostName, socketSetupData.hostPort)

# Standby
def standby_process():
	# Wait for Launch Command from CommandCenter
	# Listen on Server
	standby = True
	while(standby):
		# @NOTE_START: New Ones may only be added from the configuration file, so ignore below
		# If another Launcher & Rocket is Powered On:
		#	Perform Serial Communication to Connect to the New Rocket
		#	Perform Serial Communication to Connect to the New Launcher
		# @NOTE_END
		# Listen for LANCH command from CommandCenter
		# If LAUNCH is sent:
		#	standby = False
		# If Specific Rocket & Launcher Pairs are being sent LAUNCH command:
		#	return [12345, abcde, fghij]	# AddressCodes for the Pairs
		# Else
		#	return []

# Launch
def launch_process(addressCodes):
	# If the array of addressCodes is Empty:
	if len(addressCodes) < 1:
		# 	Fill addressCodes with all the address from the configuration file
		addressCodes = allAddressCodes
	for addressCode in addressCodes:
		launch(addressCode)


###--- Run ---###
# Perform Initial Setup
initialization_process()
# Run in Standby
addressCodes = standby_process()
# Launch the Rockets
launch_process(addressCodes)