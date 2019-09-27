from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib
import json
import argparse
import subprocess
import os
import re
import urllib
import time
import httplib
import csv
	
URL =  "http://localhost:8080/nifi-api"

def processRestReq( url, type = "GET", data = None):
	if( type == "GET" ):
		curl = "curl -k " + url 	
	else:
		print "Type " + type + " not supported"
	
	p = subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	
	if p.returncode == 0:
		return out
	else:
		print "Failed to request " + url
		print err
		print out
		return None
		
def getIds( jData, component ):
	ids = []
	for processor in jData['processGroupFlow']['flow'][component]:
		ids.append(processor['id'])
	return ids
	
def listIds( url,component, parent = None, isRecursive = False ):
	endpoint = None
	if( parent is None ):
		endpoint = "/flow/process-groups/root"
	else:
		endpoint = "/flow/process-groups/"+ parent
	 
	response = processRestReq(url + endpoint, "GET")
	jData = json.loads(response)
	ids = getIds(jData, component)
	
	if( isRecursive ):
		pgIds = getIds(jData, "processGroups")
		for id in pgIds:
			ids.extend(listIds(url, component, id, True))
		return ids
	else:
		return ids
	
def printProcessGroupStatus(jdata):
	for flowfile in jdata["processGroupStatus"]["aggregateSnapshot"]["connectionStatusSnapshots"]:
		filename = "nifi-proc-throughput.csv"
		file_path = "/home/ubuntu/performance/logs-nifi/"
		if os.path.exists(file_path+filename):
			append_write = 'ab'
		else:
			append_write = 'wb'
			
		f = open(file_path+filename,append_write)
		tm = time.strftime("%X")
		d = time.strftime("%d-%m-%Y")
		processid = flowfile["connectionStatusSnapshot"]["id"]
		groupid = flowfile["connectionStatusSnapshot"]["groupId"]
		sourceName = flowfile["connectionStatusSnapshot"]["sourceName"]
		destinationName = flowfile["connectionStatusSnapshot"]["destinationName"]
		inputflowfiles = flowfile["connectionStatusSnapshot"]["flowFilesIn"]
		outputflowfiles = flowfile["connectionStatusSnapshot"]["flowFilesOut"]
		flowfilesqueued = flowfile["connectionStatusSnapshot"]["flowFilesQueued"]
		flowfilesqueuedbytes = flowfile["connectionStatusSnapshot"]["queuedSize"]
		bytesread = flowfile["connectionStatusSnapshot"]["bytesIn"]
		byteswritten = flowfile["connectionStatusSnapshot"]["bytesOut"]
		#ist_time = jdata["processGroupStatus"]["statsLastRefreshed"]
		if int(inputflowfiles)==0:
			flow_rate = 0.0
		else:
			flow_rate = float(outputflowfiles)/float(inputflowfiles)
		try:
			writer = csv.writer(f)
			#if append_write=='wb':
			#	writer.writerow(('Date','Time','Processor','FlowFiles In','FlowFiles Out','FlowFiles Queued','Queued Bytes','Flow Rate'))
		
			csv_data = (d+" "+tm,str(processid),str(sourceName),str(destinationName),str(bytesread),str(byteswritten),str(inputflowfiles),str(outputflowfiles),str(flowfilesqueued),str(flowfilesqueuedbytes),str(flow_rate))
			writer.writerow(csv_data)
		except:
			print "Error while storing data"
		f.close()
				
def processGroupStatus(id):
	global URL
	url = URL
	curl = "curl -k " + url +"/flow/process-groups/"+id+"/status"
	p = subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	
	if p.returncode == 0:
		jdata = json.loads(out)
		printProcessGroupStatus(jdata)
	else:
		print "Failed to request " + url
		print err
		print out
		
		
def listThroughput( url,component, parent = None, isRecursive = False ):
	endpoint = None
	if( parent is None ):
		endpoint = "/flow/process-groups/root"
	else:
		endpoint = "/flow/process-groups/"+ parent
	 
	response = processRestReq(url + endpoint, "GET")
	jData = json.loads(response)
	if( isRecursive ):
		pgIds = getIds(jData, "processGroups")
		for id in pgIds:
			processGroupStatus(id)
			listThroughput(url, component, id, True)

listThroughput(URL,"processors", None, True )