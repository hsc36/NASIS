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
import requests
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
			if (not line.startswith('#')) and (len(line) > 0):
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
			if (not line.startswith('#')) and (len(line) > 0):
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
def set_and_check_configs(serial_config, api_config, RL_IDs):
	try:
		# Check API Status
		req = requests.get(api_config.address)
		if not req.status_code == 200:
			# @TODO: Log the Exception - API Status Error
			return False
		# Setup Serial/XBee Communication
		xb = serial.Serial(serial_config.comport, serial_config.bauderate, timeout=serial_config.timeout)
		# Check Serial/XBee Communication (for all Rocket & Launcher IDs)
		for RL_ID in RL_IDs:
		# @Note_1
		#	# Send Check for Rocket
		#	xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='rocket', content_type='command', content='check'))
		#	# Wait for Response
		#	time.sleep(2)	# Hardcoded Read Delay for Startup Responses
		#	rocket_response = json.loads(xb.readline())
			# Send Check for Launcher
			xb.write(format_inter_node_data_package(node_id=RL_ID, branch_type='launcher', content_type='command', content='check'))
			# Wait for Response
			time.sleep(2)	# Hardcoded Read Delay for Startup Responses
			launcher_response = json.loads(xb.readline())
			# Forward To Server
			# @TODO: Add Authentication: auth=(api_config.username, api_config.password)
			end_point = api_config.address + '/' + RL_ID + '/status'
			package = json.dumps({'launcher': launcher_response['status']})	# @NOTE_1: - 'rocket': rocket_response['status'], 
			req = requests.post(end_point, data=package)
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
	serial_config, api_config, RL_IDs = read_config_files()
	xb = set_and_check_configs(serial_config, api_config, RL_IDs)
	if not type(xb) is bool:	# @TODO: Improve this method of checking. It's bad and ugly.
		break

## Standby/Ready-to-Launch Process ##
while True:
	# @Note_2
	commands = {}
	for RL_ID in RL_IDs:
		end_point = api_config.address + '/' + RL_ID + '/status'
		req = requests.get(end_point)
		commands[RL_ID] = req.content

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
	for RL_ID in commands:
		process_command(RL_ID, commands[RL_ID], xb, api_config.address)
	# @Note_4
	# Listen for Data from the Rocket
