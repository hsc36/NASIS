import sys
import json
import ast
from flask import Flask, request, Response

###--- Setup ---###
# Read in Configurations
api_config_file = ''
try:
	with open(api_config_file) as api_config:
		for line in api_config:
			if line.startswith('debug'):
				debug_on = bool(line.split()[-1].strip())
except Exception, e:
	print 'EXCEPTION: API CONFIG -', e
	debug_on = True

# Construct the Flask API
api = Flask(__name__, template_folder=".")

# Store Flight Data in a Global {'node_id':<node_id>, 'content':[{data_point}]}
global command_dict
global status_dict
global response_dict
global flight_data_dict
command_dict = {}
status_dict = {}
response_dict = {}
flight_data_dict = {}

###--- General Functions ---###


###--- End Point Functions ---###
# Default - Used for getting list of available Nodes
@api.route("/", methods=['GET'])
def default_func():
	if request.method == 'GET':
		return_content = '<p>Request From: ' + request.remote_addr + '</p>' + '<p>Nothing to See Here. Move Along...</p>'
		return return_content
# List - Used for getting a list of the available Nodes, by their IDs
@api.route("/list", methods=['GET'])
def list_func():
	if request.method == 'GET':
		node_id_list = {}
		node_id_list['node_id_list'] = status_dict.keys()
		return_content = Response(json.dumps(node_id_list), status=200, mimetype='application/json')
	return return_content

# Command - Set and Get the Command for a Node (Check or Launch)
@api.route("/<node_id>/command", methods=['POST', 'GET', 'DELETE'])
def command_func(node_id):
	if request.method == 'GET':
		return_content = Response(json.dumps(command_dict[node_id]), status=200, mimetype='application/json')
	elif request.method == 'POST':
		command_dict[node_id] = ast.literal_eval(request.data)
		return_content = Response(json.dumps({'return_content': 'Got It!'}), status=200, mimetype='application/json')
	elif request.method == 'DELETE':
		del command_dict[node_id]
		return_content = Response(json.dumps({'return_content': 'Removed Entry!'}), status=200, mimetype='application/json')
	return return_content

# Status - Set and Get the Status of a Node (Idle, Checking, or Launching)
@api.route("/<node_id>/status", methods=['POST', 'GET', 'DELETE'])
def status_func(node_id):
	if request.method == 'GET':
		return_content = Response(json.dumps(status_dict[node_id]), status=200, mimetype='application/json')
	elif request.method == 'POST':
		status_dict[node_id] = ast.literal_eval(request.data)
		return_content = Response(json.dumps({'return_content': 'Got It!'}), status=200, mimetype='application/json')
	elif request.method == 'DELETE':
		del status_dict[node_id]
		return_content = Response(json.dumps({'return_content': 'Removed Entry!'}), status=200, mimetype='application/json')
	return return_content

# Response - Set and Get a Node's Response to a Command ({'id':<node_id>, 'branch':<rocket/launcher>, 'response':{<content>}})
@api.route("/<node_id>/response", methods=['POST', 'GET', 'DELETE'])
def response_func(node_id):
	if request.method == 'GET':
		return_content = Response(json.dumps(response_dict[node_id]), status=200, mimetype='application/json')
	elif request.method == 'POST':
		response_dict[node_id] = ast.literal_eval(request.data)
		return_content = Response(json.dumps({'return_content': 'Got It!'}), status=200, mimetype='application/json')
	elif request.method == 'DELETE':
		del response_dict[node_id]
		return_content = Response(json.dumps({'return_content': 'Removed Entry!'}), status=200, mimetype='application/json')
	return return_content

# Flight Data - Set and Get the Flight Data for a Node's Rocket Branch (({'id':<node_id>, 'branch':<rocket/launcher>, 'flight_data':{<content>}}))
@api.route("/<node_id>/flight_data", methods=['POST', 'GET', 'PUT', 'DELETE'])	# Append Data to a Global List
def flight_func(node_id):
	if request.method == 'GET':
		return_content = Response(json.dumps(flight_data_dict[node_id]), status=200, mimetype='application/json')
	elif request.method == 'POST':
		flight_data_dict[node_id] = []
		return_content = Response(json.dumps({'return_content': 'Got It!'}), status=200, mimetype='application/json')
	elif request.method == 'PUT':
		flight_data_dict[node_id].append(ast.literal_eval(request.data))
		return_content = Response(json.dumps({'return_content': 'Appended It!'}), status=200, mimetype='application/json')
	elif request.method == 'DELETE':
		del flight_data_dict[node_id]
		return_content = Response(json.dumps({'return_content': 'Removed Entry!'}), status=200, mimetype='application/json')
	return return_content

@api.route("/<node_id>/flight_data/from=<int:inclusive_start>&to=<int:inclusive_end>", methods=['GET'])	# Append Data to a Global List
def flight_func_get_specific(node_id, inclusive_start, inclusive_end):
	if request.method == 'GET':
		# Get Start and End or Data Selection
		count_start = 0 if ((inclusive_start < 0) or (inclusive_start > (len(flight_data_dict[node_id]) - 1))) else inclusive_start
		count_end = len(flight_data_dict[node_id]) if ((inclusive_end < 0) or (inclusive_end <= inclusive_start) or (inclusive_end > len(flight_data_dict[node_id]))) else inclusive_end
		# Determine the Validity of the Requested Start and End Selections
		if count_start >= 0 and count_end <= len(flight_data_dict[node_id]):
			return_data = flight_data_dict[node_id][count_start:count_end]
		else: # if count_start == 0 and cound_end == len(flight_data_dict[node_id]):
			return_data = flight_data_dict[node_id]
		return_content = Response(json.dumps(return_data), status=200, mimetype='application/json')
	return return_content

# Log - Get and Set Logs for the Node's Activities
# @NOTE: This endpoint is incomplete
@api.route("/<node_id>/log", methods=['GET', 'DELETE'])	# Append Data to the Log
def log_func(node_id):
	if request.method == 'GET':
		return_content = Response(json.dumps(flight_data_dict[node_id]), status=200, mimetype='application/json')
	if request.method == 'DELETE':
		return_content = Response(json.dumps(flight_data_dict[node_id]), status=200, mimetype='application/json')

# Run the API
if __name__ == "__main__":
	# Set Accessible IP is Debug is Off
	if debug_on:
		api.run(debug=debug_on)
	else:
		api.run(debug=debug_on, host='0.0.0.0')