#AVelazquez -- Button BLE Consumer Control Commands (Gesture)

import board
import time
import displayio
import terminalio
import neopixel
import digitalio
import adafruit_apds9960.apds9960
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import adafruit_displayio_ssd1306
from adafruit_display_text import label


import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService


#release displays
displayio.release_displays()

i2c = board.I2C()

apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
#initialize displays
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

#create display group
splash = displayio.Group()

#initialize NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness = 0.5)

#Initialize Ble radio and HID services
ble = adafruit_ble.BLERadio()
ble.name = "AVelazquez-Volume-Control"

hid = HIDService()
device_info = DeviceInfoService(software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries")
advertisement = ProvideServicesAdvertisement(hid)
cc = ConsumerControl(hid.devices)

#Clear previous connections 
if ble.connected:
    for connection in ble.connections:
        connection.disconnect()

#Initial Display Text
initial_text = "Bluetooth Initialized"
text_body = ""

text_area_title = label.Label(terminalio.FONT, text=initial_text, color=0xFFFF00, x=0, y=5)
text_area_body = label.Label(terminalio.FONT, text=text_body, color=0xFFFF00, x=0, y=20)
#send text to group
splash.append(text_area_title)
splash.append(text_area_body)

#Show Initial Text Group
display.show(splash)

#Set Button Variables/States
button_A = digitalio.DigitalInOut(board.D9)
button_A.direction = digitalio.Direction.INPUT 
button_A.pull = digitalio.Pull.UP
prev_state_A = button_A.value

button_B = digitalio.DigitalInOut(board.D6)
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP
prev_state_B = button_B.value

button_C = digitalio.DigitalInOut(board.D5)
button_C.direction = digitalio.Direction.INPUT
button_C.pull = digitalio.Pull.UP
prev_state_C = button_C.value

advertising = False
connection_made = False
apds9960.enable_proximity = True
while True:
    cur_state_A = button_A.value
    cur_state_B = button_B.value
    cur_state_C = button_C.value
    

    if not ble.connected:
        pixel[0] = (255, 0, 0)
        connection_made = False
        pixel.show()
    if not advertising:
        ble.start_advertising(advertisement)
        advertising = True
        text_area_body.text = "Awaiting Connection"
        continue
    else:
        if connection_made:
            text_area_body.text = "Connection Made"
            text_area_title.text = "Awaiting Commands"
            pass
        else:
            pixel[0] = (0, 10, 0)
            pixel.show()
            connection_made = True


    if apds9960.proximity < 10 and apds9960.proximity > 2: #Hand Raised at Angle 
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        time.sleep(0.2)

    if apds9960.proximity > 10:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT) #Hand Lowered at Angle
        time.sleep(0.2)

    if apds9960.proximity > 105:  #Device Covered
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        cc.send(ConsumerControlCode.MUTE)
        time.sleep(3)
        
    



   
    