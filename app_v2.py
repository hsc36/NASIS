# Name: Hillel Chaitoff
# Date: 10/13/2014
# Updated: 1/20/2015
#
# @Note_1: Cannot change destination address (outside of XCTU) to switch communication between rocket and launcher, mid-process.
# @Note_2: Future implementations need to check for a "General Command" command that will tell the system to get ALL commands at once.
#         This will allow the user to post multiple commands and then execute them after they have ALL been chosen.
# @NOTE_3: Future implementations will need to thread this portion of the process and handle multiple items being sent to the Serial
# @Note_4: Future implementations will need to have threading to listen to different sub-units taht are responding to different commands
import sys
import serial
import socket
import time
import json
import threading
import requests
import imuCalculations as imuCalc
from collections import namedtuple
from sys import argv

###--- Functions ---###
# Extracts Data from the Configuration Files
def read_config_files():
	serial_setup_data = namedtuple('serial_setup_data', 'comport bauderate timeout')
	api_setup_data = namedtuple('api_setup_data', 'address username password')
	# Read Communication Configuration Data
	with open('app_configs/comm.conf') as comms:
		for line in comms:
			if (not line.startswith('#')) and (len(line.strip()) > 0):
				# RF Communication to Rocket and Launcher via Serial/XBee
				if line.startswith('comport'): comport = line.split('=')[-1].strip()
				if line.startswith('bauderate'): bauderate = line.split('=')[-1].strip()
				if line.startswith('timeout'): timeout = line.split('=')[-1].strip()
				# HTTP Communication to Server/Hub via API
				if line.startswith('address'): address = line.split('=')[-1].strip()
				if line.startswith('username'): username = line.split('=')[-1].strip()
				if line.startswith('password'): password = line.split('=')[-1].strip()
		serial_setup_configs = serial_setup_data(comport=comport, bauderate=int(bauderate), timeout=int(timeout))
		api_setup_configs = api_setup_data(address=address, username=username, password=password)
	# Read Rocket & Launcher IDs
	with open('app_configs/pairs.conf') as RL_ID_list:
		RL_IDs = []
		for line in RL_ID_list:
			if (not line.startswith('#')) and (len(line.strip()) > 0):
				RL_IDs.append(line)
	return serial_setup_configs, api_setup_configs, RL_IDs

# Formats Data for Communication
def format_inter_node_data_package(node_id, branch_type, content_type, content):
	#json.loads('{' + carrier + ':' + json.dumps(package._asdict()) + '}')
	package = {}
	package['node_id'] = node_id + branch_type[0].upper()
	if content_type.upper() == 'MESSAGE':
		package['message'] = content
	elif content_type.upper() == 'COMMAND':
		package['command'] = content
	return json.dumps(package)

# Sets and Checks Configuration Data
def set_configs(serial_config, api_config):
	try:
		# Check API Status
		req = requests.get(api_config.address)
		if not req.status_code == 200:
			# @TODO: Log the Exception - API Status Error
			return False
		# Setup Serial/XBee Communication
		xb = serial.Serial(serial_config.comport, serial_config.bauderate, timeout=serial_config.timeout)
#		# Read all powered on components
#		while (xb.inWaiting() > 0):
#			serialLine = xb.readline()
#			try:
#				jsonLine = json.loads(serialLine)
#			except Exception, e:
#				# @TODO: Post error to log
#				continue
#			# @TODO: if "powered" set to "idle"
#			if 'node_id' in jsonLine.keys():
#				if 'powerOn' in jsonLine.keys():
#					if bool(jsonLine.keys()['powerOn']):
#						end_point = api_config.address + '/' + jsonLine.keys()[:-1] + '/status'
#						package = json.dumps({'status':'idle'})
#						req = requests.post(end_point, data=package)
#		# Check Serial/XBee Communication (for all Rocket & Launcher IDs)
#		for RL_ID in RL_IDs:
#		# @Note_1
#		#	# Send Check for Rocket
#		#	xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='rocket', content_type='command', content='check'))
#		#	# Wait for Response
#		#	time.sleep(2)	# Hardcoded Read Delay for Startup Responses
#		#	rocket_response = json.loads(xb.readline())
#			# Send Check for Launcher
#			xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='launcher', content_type='command', content='check'))
#			# Wait for Response
#			time.sleep(2)	# Hardcoded Read Delay for Startup Responses
#			launcher_response = json.loads(xb.readline())
#			# Forward To Server
#			# @TODO: Add Authentication: auth=(api_config.username, api_config.password)
#			end_point = api_config.address + '/' + RL_ID + '/status'
#			package = json.dumps({'launcher': launcher_response['status']})	# @NOTE_1: - 'rocket': rocket_response['status'], 
#			req = requests.post(end_point, data=package)
		return xb
	except Exception, e:
		# @TODO: Log the Exception - Inter-Node Communication Error
		return False 

def check_command(RL_ID, xb, api_addr):
	# Send Check and Wait for Response
	xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='launcher', content_type='command', content='check'))
	# Wait for Response
	time.sleep(2)	# Hardcoded Read Delay for Startup Responses
	launcher_response = json.loads(xb.readline())

	end_point = api_addr + '/' + RL_ID + '/response'
	package = json.dumps({'launcher': launcher_response['response']})	# @NOTE_1: - 'rocket': rocket_response['status'], 
	req = requests.post(end_point, data=package)

def launch_command(RL_ID, xb, api_addr):
	# Send Init and Wait for Response
	xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='launcher', content_type='command', content='init'))
	# Wait for Response
	time.sleep(2)	# Hardcoded Read Delay for Testing Responses
	launcher_response = json.loads(xb.readline())
	# Send Launch and Wait for Response
	xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='launcher', content_type='command', content='launch'))
	# Wait for Response
	time.sleep(2)	# Hardcoded Read Delay for Testing Responses
	launcher_response = json.loads(xb.readline())

	end_point = api_addr + '/' + RL_ID + '/response'
	package = json.dumps({'launcher': launcher_response['response']})	# @NOTE_1: - 'rocket': rocket_response['status'], 
	req = requests.post(end_point, data=package)

def process_command(RL_ID, command, xb, api_addr):
	return {
		'check':check_command(RL_ID, xb, api_addr),
		'launch':launch_command(RL_ID, xb, api_addr)
	}[command]


###--- Process ---###
## On Startup ##
while True:
	# Read configuration files
	serial_config, api_config, RL_IDs = read_config_files()
	# Set dictionary for checking poweredOn node components
	node_poweredOn = dict.fromkeys(RL_IDs, 0)
	# Set configurations
	xb = set_configs(serial_config, api_config)
	if not type(xb) is bool:	# @TODO: Improve this method of checking. It's bad and ugly.
		break

## Setup ##
while True:
	# Get all incomming 'poweredOn' componnet pairs, for each ID in the configuration files
	while (xb.inWaiting() > 0):
		serialLine = xb.readline()
		try:
			jsonLine = json.loads(serialLine)
		except Exception, e:
			# @TODO: Post error to log
			continue
		# Check that both rocket and launcher components are powered on for the node
		if 'powerOn' in jsonLine.keys():
			if bool(jsonLine.keys()['powerOn']):
				if jsonLine.keys()['node_id'][:-1] in RL_IDs:
					if jsonLine.keys()['node_id'][-1] == 'R': 
						node_poweredOn[jsonLine.keys()['node_id'][:-1]] += 1
					if jsonLine.keys()['node_id'][-1] == 'L': 
						node_poweredOn[jsonLine.keys()['node_id'][:-1]] += 2
	for RL_ID in RL_IDs:
		if node_poweredOn[RL_ID] > 2:
			end_point = api_config.address + '/' + jsonLine.keys()['node_id'][:-1] + '/status'
			package = json.dumps({'status':'idle'})
			req = requests.post(end_point, data=package)
			# Remove the dictionary entry
			del node_poweredOn[RL_ID]
	# Exit once all RL pairs are accounted for (the dictionary is empty)
	if len(node_poweredOn.keys()):
		break
## Standby/Ready-to-Launch Process ## 
# @TODO: Reorganize this process into separate functions and thread them
command_process_threads = []
while True:
	# @Note_2
	commands = {}
	for RL_ID in RL_IDs:
		end_point = api_config.address + '/' + RL_ID + '/command'
		req = requests.get(end_point)
		commands[RL_ID] = req.content
		# @TODO: Create a new thread for each command and start the thread
		command_process_thread = threading.Thread(target=process_command, args=(RL_ID, commands[RL_ID], xb, api_config.address))
		command_process_threads.append(command_process_thread)
		command_process_thread.start()
	for command_process_thread in command_process_threads:
		if not command_process_thread.isAlive():
			del command_process_threads[command_process_thread]
			# command_process_thread.handled = True

	###################################################
	# Commands from Command Center:
	#	- check: Checks the node's wireless connection to the RL Pairs
	#	Format: {command:{type:command_name, ids:[RL_IDs]}}
	#	- init: Initializes the launch based on the RL Pairs
	#	Format: {command:{type:command_name, ids:[RL_IDs]}}
	#	- launch: Launches based on the RL Pairs
	#	Format: {command:{type:command_name, ids:[RL_IDs]}}
	#	- *restart: Re-starts the entire script
	#	Format: {command:{type:command_name}}
	###################################################
	# Process the Command from the Command Center
	# @Note_3
#	for RL_ID in commands:
#		process_command(RL_ID, commands[RL_ID], xb, api_config.address)
	# @Note_4
	# Listen for Data from the Rocket
	# Check for errors in JSON data and Append UTC-Timestamp
