# Monitor NiFi Health And Send Email Alerts

    Python Scripts are desgined to monitor health of NiFi cluster running which captures 
        1. JVM Memory
        2. Three repositories -> FlowFile, Content and Provenance
        3. Processor component throughput
        4. Cluster centric node monitoring
    
    These Scripts are executed on time-based scheduling (CRON - x hours,minutes or seconds ). Email Notification is sent when there is
    1. Increase in heap
    2. Increase in disk space
    3. Nodes getting DISCONNECTED from the cluster
    4. Components running bullentins errors, warnings
    
## Summary

###   System Metric Processor
  
      Responsible for capturing System Diagnostics as such as heap memory, non-heap memory , flowfile respository, content respository
      etc.. This Processor is scheduled to run every 5 minutes and it dumps all the collected data into a csv file which is shipped to 
      log server by filbeat.
      
###   ClusterNodesStatus Processor
  
      Responsible for capturing behaviour of each node in terms fo there connectivity (CONNECTED OR DISCONNECTED),Number of bytes assigned vs 
      number of bytes executed, StartTime, Port Number etc.. This Processor is scheduled to run every 1 hour and it dumps all the collected data into a csv file which is shipped to 
      log server by filbeat.
      

###   NiFiStatus Processor
  
      Responsible for capturing state of NIFI Cluster which includes Error, warnings,bulletins,backPressure Enabled etc.. This 
      Processor is scheduled to run every 5 minutes and whenever NIFI is NOK sends notification.
      
###   ProcessorThroughPut
  
      Responsible for capturing Processing rate of each processor in the dataflow (a.k.a Flow Rate) , Number of flowfiles In and Out,
      Number of task executed, flowfiles queued etc.. This Processor is scheduled to run every 15 minutes and it dumps all the collected data into a csv file which is shipped to 
      log server by filbeat.
  
### These Processors are executed only on Primary Node of the NIFI Cluster . ExecuteScript Processor is used to run these scripts.

## Files
        -- monitor-cluster-nodes.py
            does the functionality for ClusterNodesStatus Processor
	           
        -- monitor-node-metrics.py
            does the functionality for SystemMetrics Processor
	    
        -- monitor-status.py
            does the functionality for NIFIStatus Processor

        -- monitor-throughput.py
            does the functionality for ProcessorThroughPut 
	        
	        
## Setup on Environments (Deployment )
  
    Step 0 : Change the location in the scripts where you want to store all the logs intially.
    Step 1 :  Drag ExecuteScript Processor from the Panel to the Canvas.
    Step 2 : Configure the Porcessor with python as option and specify location of the script.
    Step 3 : Schedule to run for day 10 secs 
    Step 4 : Make the processor to run only on primary node.
    Step 5 : Start Processor (Thats it....) . All the logs are captured into the csv file which is shipped to log server by filebeat

