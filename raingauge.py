from dbHelper import *
from ultrasonic import *
import time
import datetime
import array

def raingauge(id,holding):
	if(id==1):
		#pin of first raingauge
		sensor=ultraSound(26);
		delay=10;
	elif(id==2):
		sensor=ultraSound(19);
		delay=20;
	else:
		sensor=ultraSound(16);
		delay=30;
	db=Database();
	query="SELECT * FROM raingauge WHERE id=%s"%(id);
	num,data=db.query(query);
	if(num>0):
		d=0;
		checkArray=array.array('d',[]);
		i=0;
		while i<4:
			checkArray.insert(i,sensor.readData());
			if(i>=2):
				if(abs(checkArray[i-2]-checkArray[i-1])>1.5 or abs(checkArray[i-1]-checkArray[i])>1.5 or
				abs(checkArray[i]-checkArray[i-2])>1.5):
					d-=checkArray[i-1];
					d-=checkArray[i-2];
					i=i-2;
					time.sleep(0.1);
					continue;
			d+=checkArray[i];
			time.sleep(0.1);
			i=i+1;
		distance=round(d/4,2);
		'''
		distance=sensor.readData();'''
		print("Raingauge"+str(id)+"="+str(distance));
		if(len(data[0]['previous'])==0):
			query="UPDATE raingauge SET previous=%s WHERE id=%s"%(distance,id);
			db.insert(query);
			print("New value inserted");
			return holding;
		else:
			diff=float(data[0]['previous'])-distance;
			if(diff<-1):
				query="UPDATE raingauge SET previous=%s WHERE id=%s"%(distance,id);
				db.insert(query);
				print("Change detected and updated");
			elif(diff>1):
				now=time.time();
				if(not(holding)):
					query="UPDATE raingauge SET current=%s,datetime=%s WHERE id=%s"%(str(distance),now,id)
					db.insert(query)
					holding=True;
					print("Change is above threshold");
					return holding;
				else:
					#already registered
					#check if 10 sec has passed
					print(now-float(data[0]['datetime']));
					if((now-float(data[0]['datetime']))<10):
						query="UPDATE raingauge SET current=%s WHERE id=%s"%(distance,id)
						db.insert(query)
						print("Waiting for fixed time to pass");
						holding=True;
						return holding;
					else:
						#rate=(float(data[0]['previous'])-distance)/(now-float(data[0]['datetime']));
						rate=(float(data[0]['previous'])-distance);
						changedLevel=float(data[0]['previous'])-distance
						print(changedLevel)
						#update db data on previous
						query="UPDATE raingauge SET previous=%s,current=%s WHERE id=%s"%(distance,0,id)
						db.insert(query);
						motorOnTime=rate*50; #some weight value
						query="SELECT * FROM motorSchedule WHERE old=False ORDER BY datetime DESC";
						num,data=db.query(query);
						
						if(num>0):
							if((float(data[0]['datetime'])+float(data[0]['ontime'])-now)>delay):
								sendPrediction(str(float(data[0]['datetime'])+float(data[0]['ontime'])+1-now),changedLevel)
								query="INSERT INTO motorSchedule (ontime,datetime,old) VALUES (%s,%s,%s)"%(motorOnTime,str(float(data[0]['datetime'])+float(data[0]['ontime'])+1),False);
								db.insert(query)
								print("Overlapping. Delayed motor registered");
							else:
								sendPrediction(delay,changedLevel)
								query="INSERT INTO motorSchedule (ontime,datetime,old) VALUES (%s,%s,%s)"%(motorOnTime,now+delay,'False');
								db.insert(query)
								print("Non Overlapping motor schedule inserted");
						else:
							sendPrediction(delay,changedLevel)
							query="INSERT INTO motorSchedule (ontime,datetime,old) VALUES (%s,%s,%s)"%(motorOnTime,now+delay,'False');
							db.insert(query)
							print("New motor schedule inserted");
						holding=False;
						return holding;

import urllib
import urllib2

def sendPrediction(delay,rise):	
	count=0;
	while(count!=10):
		url="http://192.168.137.1/hexflood/piinterface.php";
		json={
				'delay':delay,
				'rise':rise
		}
		# make a string with the request type in it:
		method = "GET";
		handler = urllib2.HTTPHandler()
		opener = urllib2.build_opener(handler)
		data = urllib.urlencode(json)
		url=url+"?"+data;
		request = urllib2.Request(url, data=data)
		request.add_header("Content-Type",'application/json')
		request.get_method = lambda: method
		try:
			connection = opener.open(request)
		except urllib2.HTTPError,e:
			connection = e
										
		# check. Substitute with appropriate HTTP code.
		if connection.code == 200:
			result = connection.read()
		else:
			# handle the error case. connection.read() will still contain data
			# if any was returned, but it probably won't be of any use
			result="false";
										
		if(result=="true"):
			print("Prediction Data Sent");
			return;
		else:
			print result;
			print("Error in server side");
			count+=1;
