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

def printDiagnostics(jdata):
        filename = "nifi-node-diagnostics.csv"
        file_path = "/home/ubuntu/performance/logs-gelegua/"
        if os.path.exists(file_path+filename):
                append_write = 'ab'
        else:
                append_write = 'wb'

        f = open(file_path+filename,append_write)
        tm = time.strftime("%X")
        d = time.strftime("%d-%m-%Y")
        maxheap = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["maxHeap"])
        usedheap =  str(jdata["systemDiagnostics"]["aggregateSnapshot"]["usedHeap"])
        freeheap = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["freeHeap"])
        heaputilization = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["heapUtilization"])
        maxnonheap = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["maxNonHeap"])
        usednonheap = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["usedNonHeap"])
        freenonheap = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["freeNonHeap"])
        #nonheaputilization = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["nonHeapUtilization"])
        flowtotalspace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["flowFileRepositoryStorageUsage"]["totalSpace"])
        flowusedspace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["flowFileRepositoryStorageUsage"]["usedSpace"])
        flowfreespace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["flowFileRepositoryStorageUsage"]["freeSpace"])
        flowutilization =  str(jdata["systemDiagnostics"]["aggregateSnapshot"]["flowFileRepositoryStorageUsage"]["utilization"])
        contenttotalspace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["contentRepositoryStorageUsage"][0]["totalSpace"])
        contentusedspace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["contentRepositoryStorageUsage"][0]["usedSpace"])
        contentfreespace = str(jdata["systemDiagnostics"]["aggregateSnapshot"]["contentRepositoryStorageUsage"][0]["freeSpace"])
        contentutilization =  str(jdata["systemDiagnostics"]["aggregateSnapshot"]["contentRepositoryStorageUsage"][0]["utilization"])
        try:
		writer = csv.writer(f)	
                csv_data = (d+" "+tm,"0.0.0.0",maxheap,usedheap,freeheap,heaputilization,maxnonheap,usednonheap,freenonheap,flowtotalspace,flowusedspace,flowfreespace,flowutilization,contenttotalspace,contentusedspace,contentfreespace,contentutilization)
                writer.writerow(csv_data)
        except:
                print "Error while storing data to a file"
        f.close()
        for node in jdata['systemDiagnostics']['nodeSnapshots']:
                filename = "nifi-node-diagnostics.csv"
                file_path = "/home/ubuntu/performance/logs-gelegua/"
                if os.path.exists(file_path+filename):
                        append_write = 'ab'
                else:
                        append_write = 'wb'

                f = open(file_path+filename,append_write)
                nodeaddress = str(node["address"])
                nodemaxheap = str(node["snapshot"]["maxHeap"])
                nodeusedheap = str(node["snapshot"]["usedHeap"])
                nodefreeheap = str(node["snapshot"]["freeHeap"])
                nodeheaputilization = str(node["snapshot"]["heapUtilization"])
                nodemaxnonheap = str(node["snapshot"]["maxNonHeap"])
                nodefreenonheap = str(node["snapshot"]["freeNonHeap"])
                nodeusednonheap = str(node["snapshot"]["usedNonHeap"])
                nodeflowtotalspace = str(node["snapshot"]["flowFileRepositoryStorageUsage"]["totalSpace"])
                nodeflowusedspace = str(node["snapshot"]["flowFileRepositoryStorageUsage"]["usedSpace"])
                nodeflowfreespace = str(node["snapshot"]["flowFileRepositoryStorageUsage"]["freeSpace"])
                nodeflowutilization = str(node["snapshot"]["flowFileRepositoryStorageUsage"]["utilization"])
                nodecontenttotalspace = str(node["snapshot"]["contentRepositoryStorageUsage"][0]["totalSpace"])
                nodecontentusedspace = str(node["snapshot"]["contentRepositoryStorageUsage"][0]["usedSpace"])
                nodecontentfreespace = str(node["snapshot"]["contentRepositoryStorageUsage"][0]["freeSpace"])
                nodecontentutilization = str(node["snapshot"]["contentRepositoryStorageUsage"][0]["utilization"])
                try:
                        writer1 = csv.writer(f)	
                        csv_data1 = (d+" "+tm,nodeaddress,nodemaxheap,nodeusedheap,nodefreeheap,nodeheaputilization,nodemaxnonheap,nodeusednonheap,nodefreenonheap,nodeflowtotalspace,nodeflowusedspace,nodeflowfreespace,nodeflowutilization,nodecontenttotalspace,nodecontentusedspace,nodecontentfreespace,nodecontentutilization)
                        writer1.writerow(csv_data1)
                except:
                        print "Error while storing data to a file"
                f.close()      

def getSystemDiagnostics(url):
        curl = "curl -k " + url +"/system-diagnostics?nodewise=true"
        p = subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode == 0:
                jdata = json.loads(out)
                printDiagnostics(jdata)
        else:
                print "Failed to request " + url
                print err
                print out


getSystemDiagnostics(URL)