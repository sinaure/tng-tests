#!/usr/bin/python3
import tnglib
import sys
import time
import os
from datetime import datetime
import requests
import json
import graylog
import logging
from graylog.rest import ApiException
from pprint import pprint
import subprocess
import sys


class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

def get_logging(_from, to, query):
    # query = "source:pre-int-sp-ath AND type:E" # Object | Query (Lucene syntax)
    # _from = "2019-04-25 17:11:01.201" # Object | Timerange start. See description for date format
    # to = "2019-04-25 17:26:01.201" # Object | Timerange end. See description for date format
    try:
        # Message search with absolute timerange.
        api_instance = graylog.SearchuniversalabsoluteApi()
        api_response = api_instance.search_absolute(query, _from, to)
        reply = api_response.to_dict()
    except ApiException as e:
        print(e)

    for message in reply["messages"]:
        pprint(message["message"]["timestamp"] + " " +
		       message["message"]["container_name"] + ": " +
			   message["message"].get("message"))
        print("\n")

def instantiation(time_start, sp_path, _exit):
	# obtain package path/name
	pkg_loc = sys.argv[1]

	# clean all packages
	tnglib.remove_all_packages()

	# upload package
	upl_package = tnglib.upload_package(pkg_loc)

	# Evaluate upload
	if not upl_package[0]:
		print("Package upload failed")
		print(upl_package[1])
		_exit += 1

	print("Package upload succeeded: " + upl_package[1])

	# Obtain service uuid
	obt_serv_uuid = tnglib.map_package_on_service(upl_package[1])

	# Evaluate obtaining serv_uuid
	if not obt_serv_uuid[0]:
		print("Couldn't obtain service uuid")
		print(obt_serv_uuid[1])
		time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
		_exit += 1

	print("Service uuid obtained: " + obt_serv_uuid[1])

	time.sleep(2)

	# Instantiate the service
	req_inst = tnglib.service_instantiate(obt_serv_uuid[1])

	# Evaluate instantiation request
	if not req_inst[0]:
		print("Couldn't obtain service uuid")
		print(req_inst[1])
		time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
		_exit += 1

	print("Instantiation request made")

	# Waiting for instantiation to finish
	counter = 0
	while counter < 60:
		time.sleep(10)
		request = tnglib.get_request(req_inst[1])
		print("Waiting for instantiation, current status: " + request[1]['status'])

		if request[1]['status'] == 'READY':
			print("instantiation finished successfully")
			break

		if request[1]['status'] == 'ERROR':
			print("instantiation finished in error mode")
			time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
			get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
			_exit += 1
			break

		counter += 1

	if counter == 60:
		print("instantiation took longer than 10 minutes, aborting")
		time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
		_exit += 1

	print(str(request))
	service_instance_uuid = request[1]['instance_uuid']
	return service_instance_uuid

def termination(time_start, service_instance_uuid, sp_path, _exit):
	# Terminate the service
	ter_req = tnglib.service_terminate(service_instance_uuid)

	print("Termination request made")

	# Waiting for termination to finish
	counter = 0
	while counter < 12:
		time.sleep(10)
		request = tnglib.get_request(ter_req[1])
		print("Waiting for termination, current status: " + request[1]['status'])

		if request[1]['status'] == 'READY':
			print("termination finished successfully")
			break

		if request[1]['status'] == 'ERROR':
			print("termination finished in error mode")
			time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
			get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
			_exit += 1
			break
		counter += 1

	if counter == 12:
		print("termination took longer than 2 minutes, aborting")
		time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
		_exit += 1

	# clean all packages
	tnglib.remove_all_packages()

# Configuring the logging connection
sys.stdout = Unbuffered(sys.stdout)
configuration = graylog.Configuration()
configuration.username = "api"
configuration.password = "apiapi"
configuration.host = "logs.sonata-nfv.eu:12900"
tnglib.set_sp_path(os.environ["SP_PATH"])
tnglib.set_timeout(60)
LOG = logging.getLogger(__name__)
level = logging.DEBUG
logging.getLogger("tnglib").setLevel(level)
logging.getLogger(__name__).setLevel(level)
logging.basicConfig(level=level)

# Prering the timers
test_start = current_time = int(time.time())
test_end = int(time.time()) + 14400
counter = 0
_exit = 0

print(test_start)
# Set the environment
sp_path = os.environ["SP_PATH"].split(".")[0].replace("http://","")

while current_time < test_end:
	time_start = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	service_instance_uuid = instantiation(time_start, sp_path, _exit)
	termination(time_start, service_instance_uuid, sp_path, _exit)
	counter += 1
	current_time = int(time.time())
	if _exit > 1:
		break

# Test finished
print("The amount of repetitions was: {}".format(counter))
if _exit != 0:
	print("The test failed {} times".format(_exit))

print("Test Passed")

# Instances time
bashCommand = "docker exec -ti son-postgres psql -h localhost -U sonatatest -d  gatekeeper -c 'SELECT  instance_uuid, created_at, updated_at, request_type, status FROM requests;'"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print("Output\n{}".format(output))

bashCommand = "docker exec -ti son-postgres psql -h localhost -U sonatatest -d  gatekeeper -c 'DELETE FROM requests *;'"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

# Kubernetes Wrapper times
print("\n")
print("\n")
print("\n")
print("##############")
print("## K8S LOGS ##")
print("##############")
get_logging(time_start, time_finish, query="source:{} AND container_name:tng-sp-ia-k8s AND time".format(sp_path))

# Heat Wrapper times
print("\n")
print("\n")
print("\n")
print("###############")
print("## Heat LOGS ##")
print("###############")
get_logging(time_start, time_finish, query="source:{} AND container_name:vim-wrapper-heat AND time".format(sp_path))

if _exit > 0:
	exit(1)
exit(0)
