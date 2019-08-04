import RPi.GPIO as GPIO
import time
from dbHelper import *

motorPin=26
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(motorPin,GPIO.OUT)
started=False;
offtime=0;

while True:
	db=Database();
	now=time.time()
	#print(now);
	query="SELECT * FROM motorSchedule WHERE old=False ORDER BY datetime ASC"
	num,data=db.query(query);
	for row in data:
		if(now>=float(row['datetime'])):
			if(not(started)):
				started=True;
				offtime=time.time()+float(row['ontime']);
				GPIO.output(motorPin,GPIO.HIGH);
				print("Motor On");
				continue;
			elif(now>=offtime):
				started=False;
				GPIO.output(motorPin,GPIO.LOW);
				query="UPDATE motorSchedule SET old=True WHERE id=%s"%(row['id'])
				db.insert(query)
				print("Motor Off");
				continue;
		else:
			started=False;
			GPIO.output(motorPin,GPIO.LOW);
			print("Motor Off");
