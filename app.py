# Name: Hillel Chaitoff
# Date: 10/13/2014
# Updated: 1/4/2015

import sys
import serial
import socket
import time
import json
from collections import namedtuple
from sys import argv as cmdLineArgs

###--- Determine if in Debug ---###
inDebug = False
if len(cmdLineArgs) > 1:
	if (cmdLineArgs[1]) == 'debug':
		inDebug = True

###--- Read Configuration Files and Store Data---###
def getConfiguration():
	# Containers
	serialSetupData = namedtuple('serialData', 'comport baudeRate timeout')
	socketSetupData = namedtuple('socketData', 'address port')
	## Open the Communications Configuration File (comm.conf)
	with open('app_configs/comm.conf') as comms, open('app_configs/pairs.conf') as pairs:
		for line in comms:
			if (not line.startswith('#')) and (len(line) > 0):
				# Serial Setup
				if line.startswith('comport'): comport = line.split('>')[-1].strip()
				if line.startswith('baudeRate'): baudeRate = line.split('>')[-1].strip()
				if line.startswith('timeout'): timeout = line.split('>')[-1].strip()
				# Socket Setup
				if line.startswith('address'): address = line.split('>')[-1].strip()
				if line.startswith('port'): port = line.split('>')[-1].strip()
		serialSetup = serialSetupData(comport=comport, baudeRate=int(baudeRate), timeout=int(timeout))
		socketSetup = socketSetupData(address=address, port=int(port))
		# Rocket & Launcher Address Code Pairs
		allAddressCodes = []
		for line in pairs:
			if (not line.startswith('#')) and (len(line) > 0):
				allAddressCodes.append(line)
	return serialSetup, socketSetup, allAddressCodes

###--- General Functions ---###
# Debug Print
# Logging
def logit(content='', location='logs', fileName='', debug=False):
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
		# Address Checking (Closed Function)
		def addressCheck(addressCode, component, waitTime = 3):
			RL_setupMessage = {str(addressCode) + "_" + str(component):{"initCommand":"True"}}
			EXPECTED_RESPONSE = {str(addressCode) + "_" + str(component):{"initialized":"True"}}
			xbee.write(json.dumps(RL_setupMessage))
			# Wait for a Response Message from the Rocket & Launcher pair
			waitingForReturnMessage = True
			doneWaiting = False
			startTime = time.time()
			while(waitingForReturnMessage and (not doneWaiting)):
				if (len(xbee.read()) > 0):
					RL_setupResponse = xbee.read()
					if (RL_setupResponse == json.dumps(EXPECTED_RESPONSE)):
						waitingForReturnMessage = False
					elif (time.time() - startTime > waitTime):
						doneWaiting = True
			return waitingForReturnMessage, doneWaiting
		# Send messge to each rocket & launcher pairing
		# Wait for return message from each rocket & launcher pairing
		serialResponse = namedtuple('serialResponse', 'xbee launchers rockets')
		serialComInfo = serialResponse(xbee=xbee, launchers=[], rockets=[])
		for address in allAddressCodes:
			wrongResponse, timedOut = addressCheck(address, 'launcher')
			launcherConnected = (wrongResponse and timedOut)
			serialComInfo.launchers.append(
				{str(address):{
					'connected':launcherConnected,
					'wrongResponse':wrongResponse,
					'timedOut':timedOut}
				}
			)
			wrongResponse, timedOut = addressCheck(address, 'rocket')
			rocketConnected = (wrongResponse and timedOut)
			serialComInfo.rockets.append(
				{str(address):{
					'connected':rocketConnected,
					'wrongResponse':wrongResponse,
					'timedOut':timedOut}
				}
			)
			# Log the Connection Statuses	
			logit('ADDRESS_CHECK: ' + address + ' L ' + str(launcherConnected) + ' R ' + str(rocketConnected), location, fileName, debug=inDebug)
		return serialComInfo
	except Exception, e:
		if inDebug: print sys.exc_traceback.tb_lineno 
		logit(content='SERIAL_SETUP: ' + str(e), fileName='errors.log', debug=inDebug)
		return False

# Setup Socket (Command Center's AWS Server)
def socket_setup(address, port):
	# Setup the Socket for Server Connection
	try:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except Exception, e:
		if inDebug: print sys.exc_traceback.tb_lineno 
		logit(content='SOCKET_SETUP: ' + str(e), fileName='errors.log', debug=inDebug)
	# Connect to the Server
	try:
		server.connect((address, port))
	except Exception, e:
		if inDebug: print sys.exc_traceback.tb_lineno 
		logit(content='SOCKET_SETUP: ' + str(e), fileName='errors.log', debug=inDebug)
	# Return the socket connection
	try:
		return server
	except:	# If it could not connect to the server
		return False


###--- Communication Commands ---###
# Launch
def launch(serialComInfo):
	launchCommand = {str(addressCode) + "_" + str(component):{"launchCommand":"True"}}
	EXPECTED_RESPONSE = {str(addressCode) + "_" + str(component):{"initialized":"True"}}
	# Send Launch with Address Code

	# Wait for Launch Confirmation
	# If Launch Confirmed:
	#	launchConfirmationMessage = {addressCode:True}
	# Else:
	#	launchConfirmationMessage = {addressCode:Fail}
	# return launchConfirmationMessage

# Forward the Data from the Rocket
def forward_rocket_data():
	print "place holder"

###--- Processes ---###
# Initialization
def initialization_process():
	# Configure the Application
	serialSetupData, socketSetupData, allAddressCodes = getConfiguration()
	# Connect Hub to Server
	socketInfo = socket_setup(socketSetupData.address, socketSetupData.port)
	# Connect Launchers and Rockets to Hub
	serialInfo = serial_setup(serialSetupData.comport, serialSetupData.baudeRate, serialSetupData.timeout, allAddressCodes)
	# Return AddressCodes for Launch Process
	return socketInfo, serialInfo

# Launch
def launch_process(serialComInfo):
	# If the array of addressCodes is Empty:
	if len(addressCodes) < 1:
		# Fill addressCodes with all the address from the configuration file
		# @TODO: Determine "default" launchers & rockets from configuration file if none are specified by the command center
		addressCodes = allAddressCodes
	for addressCode in addressCodes:
		launch(addressCode)

###--- Run ---###
# Perform Initial Setup
server, serialComInfo = initialization_process()
# Listen and wait for Launch Command
while True:
	dataFromCommandCenter = ''
	serverConnected = True
	try:
		# Have server constantly send some data, to ensure connection
		dataFromCommandCenter = server.recv(4096)
		# @TODO: Change the methodology for ensuring socket connection
		#			- Send a "greeting" to the server every 't' time
		#			- Wait for appropriate response
		#			- If NOT received, Reestablish Socket Connection
		#			- Else Wait to receive Launch Command
		# Check if data from Command Center is the launch command
		if len(dataFromCommandCenter) > 0:
			if dataFromCommandCenter == launchCommand:
				# Launch the Rockets
				launch_process(serialComInfo)
				# Forward the received data to the Command Center
			elif dataFromCommandCenter == ensureConnectionCommand:
				# Ensuring connection to server
				serverConnected = True
			else:
				# Unexpected data received
				logit(content='COMMAND_CENTER: Unexpected Data Received (' + str(dataFromCommandCenter) + ')', fileName='errors.log', debug=inDebug)
		else:
			# No data received
			logit(content='COMMAND_CENTER: No Data Received', fileName='errors.log', debug=inDebug)
			serverConnected = False
			# @TODO: Reestablish socket connection

	except Exception, e:
		if inDebug: print sys.exc_traceback.tb_lineno 
		# Error Trying to Receive Data
		logit(content='SOCKET: ' + str(e), fileName='errors.log', debug=inDebug)
		break
