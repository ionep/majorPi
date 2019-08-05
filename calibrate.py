import RPi.GPIO as GPIO
import time
from dbHelper import *
from ultrasonic import *
import logging
import array
import traceback

motorPin=13
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(motorPin,GPIO.OUT)
GPIO.output(motorPin,GPIO.LOW)
sensor= ultraSound(21);
previous=0;
now=time.time()
while True:
	try:
		d=0;
		checkArray=array.array('d',[]);
		i=0;
		while i<10:
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
		data=round(d/10,2);
		if(previous==0):
			previous=data;
		current=data;
		print(current);
		if((current-previous)<=-1):
			GPIO.output(motorPin,GPIO.LOW);
			print("Motor Off");
			print(time.time()-now);
			time.sleep(100);
		else:
			GPIO.output(motorPin,GPIO.HIGH);
			print("Motor On");
	except Exception as e:
		GPIO.output(motorPin,GPIO.LOW);
		logging.error(traceback.format_exc());
		print "Interrupted"
		GPIO.cleanup()

