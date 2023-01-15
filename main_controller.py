import os, time, board, busio, digitalio, adafruit_ssd1306
import RPi.GPIO as GPIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pijuice import PiJuice

pijuice = PiJuice(1, 0x14)
oled_reset = digitalio.DigitalInOut(board.D4)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

servo1 = GPIO.PWM(12, 50)
servo1.start(0)

servo2 = GPIO.PWM(6, 50)
servo2.start(0)

servo1_pos = 7.5
servo2_pos = 7.5
                
WIDTH = 128
HEIGHT = 64
BORDER = 5
CALIBRATION = 250
INPUT_MEMORY = 10

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, oled.width, oled.height), outline = 255, fill = 255)
small_font = ImageFont.truetype('PixelOperator.ttf', 11)
font = ImageFont.truetype('PixelOperator.ttf', 15)

calibration_total = 0
calibration_length = 0
calibration_result = 0
solar_watt_hours = 0
solar_wattage_total = 0
solar_wattage_length = 0
solar_wattage_result = 0
solar_efficiency_total = 0
cycles = 0
runtime = 0
uptime = 0
time_left = 0
requested_time = 1
requested_cycles = 2
total_rounds = 1
total_duration = requested_time * requested_cycles * 60
last_duration = 10 ** 10
setup_finished = False
mode = "boot"

while True:
    try:
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.LOW)
        time.sleep(0.001)
        GPIO.setup(17, GPIO.IN)
        
        currentTime = time.time()
        while GPIO.input(17) == GPIO.LOW:
            brightness1 = round(1 / (time.time() - currentTime))
            
        GPIO.setup(27, GPIO.OUT)
        GPIO.output(27, GPIO.LOW)
        time.sleep(0.001)
        GPIO.setup(27, GPIO.IN)
        
        currentTime = time.time()
        while GPIO.input(27) == GPIO.LOW:
            brightness2 = round(1 / (time.time() - currentTime))
            
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, GPIO.LOW)
        time.sleep(0.001)
        GPIO.setup(22, GPIO.IN)
        
        currentTime = time.time()
        while GPIO.input(22) == GPIO.LOW:
            brightness3 = round(1 / (time.time() - currentTime))
            
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.LOW)
        time.sleep(0.001)
        GPIO.setup(23, GPIO.IN)
        
        currentTime = time.time()
        while GPIO.input(23) == GPIO.LOW:
            brightness4 = round(1 / (time.time() - currentTime))
            
        battery_charge = pijuice.status.GetChargeLevel()["data"]
        battery_voltage = pijuice.status.GetBatteryVoltage()["data"] / 1000
        battery_amperage = -pijuice.status.GetBatteryCurrent()["data"]
        battery_wattage = battery_voltage * battery_amperage
        
        io_voltage = pijuice.status.GetIoVoltage()["data"] / 1000
        io_amperage = pijuice.status.GetIoCurrent()["data"]
        io_wattage = io_voltage * io_amperage
        
        if pijuice.status.GetStatus()["data"]["powerInput"] == "NOT_PRESENT" or battery_wattage <= 0:
            battery_left = (battery_charge / 100 * 12000) * round(battery_voltage, 2)
            if battery_wattage != 0:
                time_left = round(battery_left / -battery_wattage * 3600)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        current_date_save  = datetime.now().strftime("%m-%d-%y")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if mode == "boot":
            draw.text((0, 0), "Time: " + str(current_time), font = font, fill = 255)
            if pijuice.status.GetStatus()["data"]["powerInput"] == "NOT_PRESENT" or battery_wattage <= 0:
                draw.text((0, 14), "Battery[-]: " + str(battery_charge) + "% - " + str(int(time_left / 3600)) + "h:" + str(int(time_left / 60) - (int(time_left / 3600) * 60)) + "m", font = small_font, fill = 255)
            else:
                draw.text((0, 14), "Battery[+]: " + str(battery_charge) + "% - " + str(round(battery_wattage / 1000, 2)) + "W", font = small_font, fill = 255)
            draw.text((0, 24), "Dim TR to setup test", font = small_font, fill = 255)
            draw.text((0, 34), "Dim BL to end test", font = small_font, fill = 255)
            draw.text((0, 44), "Dim BR to kill program", font = small_font, fill = 255)
            
            if brightness2 <= 10:
                SAVE_FILE = "save-" + str(current_date_save) + "-" + str(current_time) + ".txt"
                mode = "running"
                start_time = time.perf_counter()
        
        if brightness4 <= 10 and setup_finished == True:
            if calibration_length <= CALIBRATION:
                with open(SAVE_FILE, "w") as file:
                    file.write("Test was terminated during calibration.\n")
            with open(SAVE_FILE, "a") as file:
                file.write("Test Ended On: " + str(current_date) + " @ " + str(current_time) + "\n")
            inflicted_error = 0 / 0
            
        if (mode == "running" or mode == "tracking") and setup_finished == True:
            if mode == "tracking":
                if brightness1 + brightness3 > brightness2 + brightness4:
                    if servo1_pos >= 3:
                        servo1_pos -= 0.1
                
                if brightness1 + brightness3 < brightness2 + brightness4:
                    if servo1_pos <= 11.5:
                        servo1_pos += 0.1
                    
                if brightness1 + brightness2 > brightness3 + brightness4:
                    if servo2_pos >= 7.5:
                        servo2_pos -= 0.1
                    
                if brightness1 + brightness2 < brightness3 + brightness4:
                    if servo2_pos <= 11:
                        servo2_pos += 0.1
                
                servo1.ChangeDutyCycle(servo1_pos)
                servo2.ChangeDutyCycle(servo2_pos)
                time.sleep(0.1)
                servo1.ChangeDutyCycle(0)
                servo2.ChangeDutyCycle(0)
            else:
                time.sleep(0.1)
        
            if brightness3 <= 10:
                if calibration_length <= CALIBRATION:
                    with open(SAVE_FILE, "w") as file:
                        file.write("Test was terminated during calibration.\n")
                with open(SAVE_FILE, "a") as file:
                    file.write("Test Ended On: " + str(current_date) + " @ " + str(current_time) + "\n")
                servo1.ChangeDutyCycle(7.5)
                servo2.ChangeDutyCycle(7.5)
                time.sleep(1)
                servo1.ChangeDutyCycle(0)
                servo2.ChangeDutyCycle(0)
                calibration_total = 0
                calibration_length = 0
                calibration_result = 0
                solar_watt_hours = 0
                solar_wattage_total = 0
                solar_wattage_length = 0
                solar_wattage_result = 0
                solar_efficiency_total = 0
                cycles = 0
                runtime = 0
                uptime = 0
                total_rounds = 0
                last_duration = 10 ** 10
                setup_finished = False
                mode = "boot"
            elif calibration_length >= CALIBRATION:
                if pijuice.status.GetStatus()["data"]["powerInput"] == "NOT_PRESENT":
                    calibration_total += battery_wattage + io_wattage
                    calibration_length += 1
                    calibration_result = calibration_total / calibration_length
                    raw_solar_wattage = 0
                    solar_wattage_total = 0
                    solar_wattage_length = 0
                    solar_wattage_result = 0
                else:
                    raw_solar_wattage = battery_wattage + io_wattage - calibration_result
                    
                    solar_wattage_total += raw_solar_wattage
                    solar_wattage_length += 1
                    solar_wattage_result = solar_wattage_total / solar_wattage_length
                    
                    if cycles % INPUT_MEMORY == 0:
                        solar_wattage_total = solar_wattage_result * INPUT_MEMORY
                        solar_wattage_length = INPUT_MEMORY
                
                if cycles % CALIBRATION == 0:
                    calibration_total = calibration_result * CALIBRATION
                    calibration_length = CALIBRATION
                
                cycles += 1
                solar_watt_hours += raw_solar_wattage * (runtime / 3600)
                raw_solar_efficiency = raw_solar_wattage / 5
                solar_efficiency_total += raw_solar_efficiency
                solar_efficiency = (solar_efficiency_total / cycles) / 10
                    
                runtime = time.perf_counter() - start_time
                start_time = time.perf_counter()
                uptime += runtime
                total_duration -= runtime
                
                if total_duration <= 0:
                    with open(SAVE_FILE, "a") as file:
                        file.write("Test Ended On: " + str(current_date) + " @ " + str(current_time) + "\n")
                    servo1.ChangeDutyCycle(7.5)
                    servo2.ChangeDutyCycle(7.5)
                    time.sleep(1)
                    servo1.ChangeDutyCycle(0)
                    servo2.ChangeDutyCycle(0)
                    inflicted_error = 0 / 0
                
                if last_duration + runtime * 2 <= (total_duration % (requested_time * 60)):
                    servo1_pos = 7.5
                    servo2_pos = 7.5
                    servo1.ChangeDutyCycle(7.5)
                    servo2.ChangeDutyCycle(7.5)
                    time.sleep(1)
                    servo1.ChangeDutyCycle(0)
                    servo2.ChangeDutyCycle(0)
                    total_rounds += 1
                    if mode == "running":
                        with open(SAVE_FILE, "a") as file:
                            file.write("Tracking Cycle " + str(int(total_rounds / 2)) + "/" + str(int(requested_cycles / 2)) + " Began At: " + str(current_date) + " @ " + str(current_time) + "\n")
                        mode = "tracking"
                    elif mode == "tracking":
                        with open(SAVE_FILE, "a") as file:
                            file.write("Running Cycle " + str(int((total_rounds / 2) + 0.5)) + "/" + str(int(requested_cycles / 2)) + " Began At: " + str(current_date) + " @ " + str(current_time) + "\n")
                        mode = "running"
                last_duration = total_duration % (requested_time * 60)
                        
                draw.text((0, 0), "Power: " + str(round(solar_watt_hours, 2)) + "mWh", font = font, fill = 255)
                draw.text((0, 14), "Input: " + str(round(solar_wattage_result)) + "mW", font = font, fill = 255)
                draw.text((0, 28), "Time Left: " + str(int(total_duration / 3600)) + "h:" + str(int(total_duration / 60) - (int(total_duration / 3600) * 60)) + "m", font = font, fill = 255)
                if mode == "running":
                    draw.text((0, 44), "Mode: RUNNING " + str(int((total_rounds / 2) + 0.5)) + "/" + str(int(requested_cycles / 2)), font = small_font, fill = 255)
                elif mode == "tracking":
                    draw.text((0, 44), "Mode: TRACKING " + str(int(total_rounds / 2)) + "/" + str(int(requested_cycles / 2)), font = small_font, fill = 255)
                if pijuice.status.GetStatus()["data"]["powerInput"] == "NOT_PRESENT" or battery_wattage <= 0:
                    draw.text((0, 54), "Battery[-]: " + str(battery_charge) + "% - " + str(int(time_left / 3600)) + "h:" + str(int(time_left / 60) - (int(time_left / 3600) * 60)) + "m", font = small_font, fill = 255)
                else:
                    draw.text((0, 54), "Battery[+]: " + str(battery_charge) + "% - " + str(round(battery_wattage / 1000, 2)) + "W", font = small_font, fill = 255)
                
                with open(SAVE_FILE, "a") as file:
                    cycles_text = "Cycle: " + str(cycles)
                    current_time_text = "Time: " + str(datetime.now().strftime("%H:%M:%S"))
                    uptime_text = "Uptime: " + str(int(uptime / 3600)) + "h:" + str(int(uptime / 60) - (int(uptime / 3600) * 60)) + "m:" + str(round(uptime - (int(uptime / 60) * 60) - (int(uptime / 3600) * 3600), 1)) + "s"
                    solar_wattage_text = "Solar Wattage: " + str(round(solar_wattage_result)) + "mW"
                    solar_watt_hours_text = "Solar Power Collected: " + str(round(solar_watt_hours)) + "mWh"
                    solar_efficiency_text = "Solar Efficiency: " + str(round(solar_efficiency)) + "%"
                    brightness_text = "Brightness: " + str(round((brightness1 + brightness2 + brightness3 + brightness4) / 4))
                    file.write(cycles_text + " - " + current_time_text + " - " + uptime_text + " - " + solar_wattage_text + " - " + solar_watt_hours_text + " - " + solar_efficiency_text + " - " + brightness_text + "\n")
            else:
                if pijuice.status.GetStatus()["data"]["powerInput"] == "WEAK" or pijuice.status.GetStatus()["data"]["powerInput"] == "PRESENT":
                    draw.text((0, 0), "Calibrating: PAUSED", font = font, fill = 255)
                    draw.text((0, 14), "Offset: PAUSED", font = font, fill = 255)
                    draw.text((0, 28), "Make sure the solar panel", font = small_font, fill = 255)
                    draw.text((0, 38), "is not in direct sunlight", font = small_font, fill = 255)
                    draw.text((0, 48), "during calibration!", font = small_font, fill = 255)
                else:
                    calibration_total += battery_wattage + io_wattage
                    calibration_length += 1
                    calibration_result = calibration_total / calibration_length
                    
                    runtime = time.perf_counter() - start_time
                    start_time = time.perf_counter()
                
                    draw.text((0, 0), "Calibrating: " + str(round(calibration_length * 100 / CALIBRATION)) + "%", font = font, fill = 255)
                    draw.text((0, 14), "Time: " + str(int(((CALIBRATION - calibration_length) * runtime) / 60)) + "m:" + str(round((CALIBRATION - calibration_length) * runtime - int(((CALIBRATION - calibration_length) * runtime) / 60) * 60, 2)) + "s", font = font, fill = 255)
                    draw.text((0, 28), "Make sure the solar panel", font = small_font, fill = 255)
                    draw.text((0, 38), "is not in direct sunlight", font = small_font, fill = 255)
                    draw.text((0, 48), "during calibration!", font = small_font, fill = 255)
                    if calibration_length >= CALIBRATION:
                        with open(SAVE_FILE, "w") as file:
                            file.write("Running Cycle 1/" + str(int(requested_cycles / 2)) + " Began At: " + str(current_date) + " @ " + str(current_time) + "\n")
        elif (mode == "running" or mode == "tracking") and setup_finished == False:
            if brightness1 <= 10:
                setup_finished = True
            if brightness2 <= 10:
                requested_time = 1
                requested_cycles = 2
            if brightness3 <= 10:
                requested_time += 1
            if brightness4 <= 10:
                requested_cycles += 2
            total_duration = requested_time * requested_cycles * 60
            draw.text((0, 0), "Duration: " + str(round(total_duration / 3600, 1)) + "hrs", font = font, fill = 255)
            draw.text((0, 14), "Cycle Time: " + str(requested_time) + "mins", font = font, fill = 255)
            draw.text((0, 28), "Cycles to Run: " + str(requested_cycles), font = font, fill = 255)
            draw.text((0, 42), "Dim TR/BL/BR to adjust", font = small_font, fill = 255)
            draw.text((0, 52), "Dim TL to start", font = small_font, fill = 255)
                
        oled.image(image)
        oled.show()
    except:
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        GPIO.setup(17, GPIO.LOW)
        GPIO.setup(27, GPIO.LOW)
        GPIO.setup(22, GPIO.LOW)
        GPIO.setup(23, GPIO.LOW)
        GPIO.setup(12, GPIO.LOW)
        GPIO.setup(6, GPIO.LOW)
        servo1.ChangeDutyCycle(7.5)
        servo2.ChangeDutyCycle(7.5)
        time.sleep(1)
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        time.sleep(0.5)
        servo1.stop()
        servo2.stop()
        GPIO.cleanup()
        oled.fill(0)
        oled.show()
        break