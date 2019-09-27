import json
import argparse
import subprocess
import datetime
import os
import re
import urllib
import time
import threading
import httplib
import csv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

URL = "http://localhost:8080/nifi-api"

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

#Connections available in NIFI
def listConnectionsId( url, parent = None, isRecursive = False ):
	return listIds(url, "connections", parent, isRecursive)
	
def isBackpressureEnabled( url, connectionId ):
	endpoint = "/connections/" + connectionId
	response = processRestReq(url + endpoint, "GET")
	jData = json.loads(response)
	threshold = int(jData["component"]["backPressureObjectThreshold"])
	if threshold == 0:
		return False
	return jData['status']['aggregateSnapshot']['percentUseCount'] == "90"
	
#Checks for warnings and errors
def getBulletinsBoard( url):
	response = processRestReq(url + "/flow/bulletin-board" + "?after=0", "GET")
	return json.loads(response)
	

def showBulletins( url):
	data = getBulletinsBoard(url)
	for bulletin in data['bulletinBoard']['bulletins']:
		if ( "sourceId" in bulletin.keys() ):
			print bulletin['sourceId'] + "\t" + bulletin['timestamp'] + "\t" + bulletin['bulletin']['message']
		else:
			print "\t\t\t\t" + bulletin['timestamp'] + "\t" + bulletin['bulletin']['message']
			
#Sends mail to the admin if there is any warning or error
def sendNotificationMail(warning):
	fromaddr = "XXX@gmail.com"
	toaddr = "XXX@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Notification "
	body = "***Please do NOT reply to this email, it is auto-generated****\nACTION REQUIRED: "+warning
	msg.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com:465')
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.close()

def getNiFiStatus( url ):
	# check if back pressure is enabled on a connection
	connections = listConnectionsId(url, None, True)
	warning = False
	for connectionId in connections:
		if( isBackpressureEnabled(url,connectionId) ):
			print "WARNING: back pressure is enabled on connection " + connectionId
			warning = True
			
	# check if there are bulletins
	jData = getBulletinsBoard(url)
	nbBulletins = len(jData['bulletinBoard']['bulletins'])
	if( nbBulletins != 0 ):
		warning = True
		#print "WARNING: "
		showBulletins( url)
	
	if( warning ):
		print "NiFi is NOK"
		sendNotificationMail(warning)
	else:
		print "NiFi is OK"
	
getNiFiStatus(URL)	