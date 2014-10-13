# Name: Hillel Chaitoff
# Date: 10/13/2014
# Updated: 
# NOTE:	Add configuration file for reading in settings: Serial Setup, Socket Setup, 

import serial
import socket
import time
from collections import namedtuple

###--- Build Storage Containers ---###
serialSetupData = namedtuple('serialData', 'comport baudeRate timeout')
socketSetupData = namedtuple('socketData', 'hostName hostPort')

###--- Read Configuration Files and Store Data---###
# Serial Setup
comport = '/dev/ttyUSB0'
baudeRate = 9600
timeout = 1
serialSetup = serialSetupData(comport=comport, baudeRate=baudeRate, timeout=timeout)
# Socket Setup
hostName = 'http://ServerAddress.com'
hostPort = 8080
socketSetup = socketSetupData(hostName=hostName, hostPort=hostPort)

###--- General Functions ---###
def logit(content='', location='', fileName=''):
	destination = location + '/' + fileName


###--- Setup Functions ---###
# Setup Serial (XBee)
def serial_setup(comport, baudeRate, timeout):
	xbee = serial.Serial(comport, baudeRate, timeout=timeout)
	# Send messge to each rocket & launcher pairing
	# Wait for return message from each rocket & launcher pairing
	# For each successful pair of return messages:
	#	Log 'SUCCESS: XBee Communication RL[12345, 67890, abcde]'
	# Else:
	#	Log 'FAIL: XBee Communication R[12345, abcde] L[12345]'
	return xbee

# Setup Socket (Command Center's AWS Server)
def socket_setup(hostName, hostPort):
	server = socket.Socket(socket.AF_INET, socket.SOCK_STREAM)
	# Connect to the Server
	server.connect(hostName, hostPort)
	return server


###--- Processes ---###
# Initialization
def initialization_process():
	# Connect Pi to Server
	socket_setup()
	# Connect Launchers and Rockets to Pi
	serial_setup()

# Standby
def standby_process():
	standby = True	# Waiting for Launch
	while(standby)

# Launch
def launch_process():


###--- Run ---### 