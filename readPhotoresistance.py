import PCF8591 as ADC
import RPi.GPIO as GPIO
import random

class photoresistor():
	def __init__(self):
		ADC.setup(0x48)
		
	def dataRead(self):
		lum = ADC.read(3)
		return lum
		#print 'outValue: ', ADC.read(3)

	# def dataRead():
		# try:
			# outlumsetup()
			# lumloop()
			
		# except KeyboardInterrupt: 
			# pass
			
class photoresistorSimulator():
	def __init__(self):
		self.mean_lum = random.uniform(100, 200)
		
	def dataRead(self):
		return self.mean_lum + random.uniform(0, 10) - 5
