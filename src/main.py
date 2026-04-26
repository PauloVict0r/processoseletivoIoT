from machine import Pin, PWM, time_pulse_us
import time

def read_distance(trig, echo):
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    try:
        duration = time_pulse_us(echo, 1, 30000)
        if duration > 0:
            return (duration / 2) / 29.1
    except Exception:
        pass
    return -1

def main():
    led_green = Pin(22, Pin.OUT)
    led_yellow = Pin(19, Pin.OUT)
    led_red = Pin(21, Pin.OUT)
    
    buzzer = PWM(Pin(23))
    buzzer.duty_u16(0)
    
    trig = Pin(5, Pin.OUT)
    echo = Pin(18, Pin.IN)
    
    print("PARKING_SYSTEM_READY")
    
    while True:
        distance = read_distance(trig, echo)
        
        if distance < 0:
            time.sleep(0.1)
            continue
            
        if distance > 100:
            led_green.value(1)
            led_yellow.value(0)
            led_red.value(0)
            buzzer.duty_u16(0)
            time.sleep(0.1)
        elif 50 <= distance <= 100:
            led_green.value(0)
            led_yellow.value(1)
            led_red.value(0)
            buzzer.freq(500)
            buzzer.duty_u16(32768)
            time.sleep(0.2)
            buzzer.duty_u16(0)
            time.sleep(0.2)
        else:
            led_green.value(0)
            led_yellow.value(0)
            led_red.value(1)
            buzzer.freq(1000)
            buzzer.duty_u16(32768)
            time.sleep(0.05)
            buzzer.duty_u16(0)
            time.sleep(0.05)

if __name__ == '__main__':
    main()