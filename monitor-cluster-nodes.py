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
	
URL = "http://localhost:8080/nifi-api"

def sendNotificationMail(warning):
	fromaddr = "XXX@gmail.com"
	toaddr = "XXX@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Notification "
	body = "***Please do NOT reply to this email, it is auto-generated****\nACTION REQUIRED: \n"+warning
	msg.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com:465')
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.close()
	
def checkTimeElasped(nodeAddress,nodeApiPort,nodeId):
	filename = nodeAddress+".txt"
	file_path = "/home/ubuntu/perfLogs/"
	if os.path.exists(file_path+filename):
		f = open(file_path+filename,"r")
		oldTime = f.read()
		f.close()
		newTime = time.strftime("%X")
		FMT = '%H:%M:%S'
		timeElasped = datetime.strptime(newTime,FMT) - datetime.strptime(oldTime,FMT)
		inSeconds = timeElasped.seconds
		if inSeconds > 60 :
			sendNotificationMail("Node with Address "+nodeAddress+" ( "+nodeId+" )and Port "+nodeApiPort+" got DISCONNECTED")
			f = open(file_path+filename,'w')
			f.write(time.strftime("%X"))
			f.close()		
	else :
		f = open(file_path+filename,'w')
		f.write(time.strftime("%X"))
		sendNotificationMail("Node with Address "+nodeAddress+" ( "+nodeId+" )and Port "+nodeApiPort+" got DISCONNECTED")
	
def printNodesInfo(jdata):
	email_path = "/home/ubuntu/mailfiles/"
	for node in jdata['cluster']['nodes']:
		filename = "nifi-cluster-nodes.csv"
		file_path = "/home/ubuntu/perfLogs/"
		if os.path.exists(file_path+filename):
			append_write = 'ab'
		else:
			append_write = 'wb'
			
		f = open(file_path+filename,append_write)
		tm = time.strftime("%X")
		d = time.strftime("%d-%m-%y")	
		nodeId = node['nodeId']
		nodeAddress = node['address']
		nodeApiPort = str(node['apiPort'])
		nodeStatus = node['status']
		nodeStartTime = node['nodeStartTime']
		nodeHeartbeat = node['heartbeat']
		nodeData = node['queued']
		try:
			writer = csv.writer(f)		
			csv_data = (d+" "+tm,nodeId,nodeAddress,nodeApiPort,nodeStatus,nodeStartTime,nodeHeartbeat,nodeData)
			writer.writerow(csv_data)
		except:
			print "Error while storing data to a file"
		f.close()
		
		if nodeStatus == "CONNECTED":
			checkTimeElasped(nodeAddress,nodeApiPort,nodeId)
		else:
			if os.path.exists(email_path+nodeAddress+'.txt'):
				os.remove(email_path+nodeAddress+'.txt')
		
			
			
def getClusterNodesInfo(url):
	curl = "curl -k " + url +"/controller/cluster"
	p = subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if p.returncode == 0:
		jdata = json.loads(out)
		printNodesInfo(jdata)
	else:
		print "Failed to request " + url
		print err
		print out
		
getClusterNodesInfo(URL)