#!/usr/bin/python3
import tnglib
import sys
import time
import os
from datetime import datetime
import requests
import json
import graylog 
from graylog.rest import ApiException
from pprint import pprint

configuration = graylog.Configuration()
configuration.username = "api"
configuration.password = "apiapi"
configuration.host = "logs.sonata-nfv.eu:12900"
api_instance = graylog.SearchuniversalabsoluteApi()

def get_logging(_from, to, query):
    # query = "source:pre-int-sp-ath AND type:E" # Object | Query (Lucene syntax)
    # _from = "2019-04-25 17:11:01.201" # Object | Timerange start. See description for date format
    # to = "2019-04-25 17:26:01.201" # Object | Timerange end. See description for date format
    try: 
        # Message search with absolute timerange.
        api_response = api_instance.search_absolute(query, _from, to)
        reply = api_response.to_dict()
    except ApiException as e:
        print(e)

    for message in reply["messages"]:
        pprint(message["message"]["container_name"] + ": " + message["message"].get("message"))
        print("\n")

time_start = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# Set the environment
tnglib.set_timeout(60)
tnglib.set_sp_path(os.environ["SP_PATH"])
sp_path = os.environ["SP_PATH"].split(".")[0].replace("http://","")

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
	exit(1)

print("Package upload succeeded: " + upl_package[1])

# Obtain service uuid
obt_serv_uuid = tnglib.map_package_on_service(upl_package[1])

# Evaluate obtaining serv_uuid
if not obt_serv_uuid[0]:
	print("Couldn't obtain service uuid")
	print(obt_serv_uuid[1])
	time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
	exit(1)

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
	exit(1)

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
		exit(1)
	
	counter += 1

if counter == 60:
	print("instantiation took longer than 10 minutes, aborting")
	time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
	exit(1)

service_instance_uuid = request[1]['instance_uuid']

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
		exit(1)
	
	counter += 1

if counter == 12:
	print("termination took longer than 2 minutes, aborting")
	time_finish = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	get_logging(time_start, time_finish, query="source:{} AND type:E".format(sp_path))
	exit(1)

# clean all packages
tnglib.remove_all_packages()

# Test finished
print("test finished successfully")
exit(0)
