import RPi.GPIO as GPIO
import time
from dbHelper import *
import logging

motorPin=13
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(motorPin,GPIO.OUT)
GPIO.output(motorPin,GPIO.LOW)
started=False;
offtime=0;

while True:
	try:
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
	except Exception as e:
		GPIO.output(motorPin,GPIO.LOW);
		print e.message;
		logging.error(traceback.format_exc());
