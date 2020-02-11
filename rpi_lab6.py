# rpi_lab6.py
# In this lab, we will learn to interface a MCP3002 ADC chip to Raspberry Pi's SPI bus. 
# A variable resistor (Potentiometer) is used to provide analog input to ADC chip.

# Import Python Library
import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)

# read SPI data from MCP3002 chip
def read_adc(channel):
	# Send start bit(S), sgl/diff(D), odd/sign(C), MSBF(M)
    	# Command format: 0000 000S DCM0 0000 0000 0000
	# channel0:       0000 0001 1000 0000 0000 0000
	# channel1:       0000 0001 1100 0000 0000 0000
	# Start bit = 1
    	# sgl/diff = 1 (Single Ended Mode); odd/sign = channel (0/1); MSBF = 0
    	#
    	# 2 + channel shifted 6 to left
    	# channel 0: 1000 0000
    	# channel 1: 1100 0000
    	command = [1,(2+channel)<<6,0]
    	reply = spi.xfer2(command)

    	# spi.xfer2 returns 24 bit data (3*8 bit)
    	# We only need data from bit 13 to 22 (10 bit - MCP3002 resolution)
	# XXXX XXXX XXXX DDDD DDDD DDXX
    	# Mask data with 31 (0001 1111) to ensure we have all data from XXXX DDDD and nothing more. 
    	# 0001 is for signed in next operation.
    	data = reply[1] & 31   
    	# Shift data 6 bits to left.
    	# 000D DDDD << 6 = 0DDD DD00 0000
    	data = data << 6  
    
    	# Now we get the last set of data from reply[2] and discard last two bits
    	# DDDD DDXXX >> 2 = 00DD DDDD
    	# 0DDD DD00 0000 + 00DD DDDD = 0DDD DDDD DDDD
    	data = data + (reply[2] >> 2)
    
    	return data

try:
	while True:
		ADC0 = read_adc(0)
		Voltage = round(((ADC0 * 3.3) / 1024), 2)
		print("Raw ADC Value: {}".format(ADC0))
		print("Voltage (V): {}".format(Voltage))
		time.sleep(1)
except KeyboardInterrupt:
	spi.close()
