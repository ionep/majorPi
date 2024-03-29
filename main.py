from ultrasonic import *
from dbHelper import *
from raingauge import *
import logging
import traceback
import datetime
import time
import array

import urllib
import urllib2

def sendIt():	
	count=0;
	db=Database();
	while(count!=10):
		query="""SELECT * FROM RiverLevel WHERE sent='false'""";
		num,data=db.query(query);
		if(num>0):
			for d in data:
						url="http://192.168.137.1/hexflood/piinterface.php";
						json={
								'data':d['data'],
								'dd':d['dd'],
								'mm':d['mm'],
								'yy':d['yy'],
								'location':d['location']
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
							query="""UPDATE RiverLevel SET sent='True' WHERE sn=%s"""%(d['sn']);
							db.insert(query);
							print("Updated 1 record");
							count=0;
						else:
							print result;
							print("Error in server side");
							return;
		else:
			return;
			

if __name__=='__main__':
	try:
		db= Database();
		sensor= ultraSound(21);
		l_id=1;
		holding1=False;
		holding2=False;
		holding3=False;
		while True:
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
			data=round(d/4,2);
			print("River:"+str(data));
			d=datetime.datetime.now();
			if(d.month<10):
				mm='0'+str(d.month);
			else:
				mm=str(d.month);
				#if(d.day<10):
					#dd='0'+str(d.day);
				#else:
					#dd=str(d.day);
			if(d.minute<10):
				dd='0'+str(d.minute);
			else:
				dd=str(d.minute);
			query = """INSERT INTO RiverLevel(data,dd,mm,yy,location) VALUES(%s, %s,%s,%s,%s)
					"""%(data,dd,mm,str(d.year),l_id);
			db.insert(query);
			sendIt();
			time.sleep(1);
			holding1=raingauge(1,holding1);
			holding2=raingauge(2,holding2);
			holding3=raingauge(3,holding3);
			
			
			

		
	except Exception as e:
		print e.message;
		logging.error(traceback.format_exc());
