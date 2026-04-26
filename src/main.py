from machine import Pin, PWM, time_pulse_us, WDT
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

class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.values = []
        
    def add(self, val):
        self.values.append(val)
        if len(self.values) > self.size:
            self.values.pop(0)
            
    def get_average(self):
        if not self.values:
            return -1
        return sum(self.values) / len(self.values)

def main():
    # Watchdog timer: reinicia o ESP32 se ele travar por mais de 5s
    wdt = WDT(timeout=5000)
    
    led_green = Pin(22, Pin.OUT)
    led_yellow = Pin(19, Pin.OUT)
    led_red = Pin(21, Pin.OUT)
    
    buzzer = PWM(Pin(23))
    buzzer.duty_u16(0)
    
    trig = Pin(5, Pin.OUT)
    echo = Pin(18, Pin.IN)
    
    filter = MovingAverage(5)
    
    # Variaveis para execucao nao-bloqueante
    last_sensor_read = time.ticks_ms()
    last_buzzer_toggle = time.ticks_ms()
    buzzer_state = False
    
    print("SMART_PARKING_V1_OK")
    
    while True:
        wdt.feed() # Alimenta o cão de guarda
        current_time = time.ticks_ms()
        
        # Le o sensor a cada 100ms
        if time.ticks_diff(current_time, last_sensor_read) > 100:
            last_sensor_read = current_time
            dist = read_distance(trig, echo)
            if dist >= 0:
                filter.add(dist)
                
        avg_dist = filter.get_average()
        if avg_dist < 0:
            continue
            
        if avg_dist > 100:
            led_green.value(1)
            led_yellow.value(0)
            led_red.value(0)
            buzzer.duty_u16(0)
        elif 50 <= avg_dist <= 100:
            led_green.value(0)
            led_yellow.value(1)
            led_red.value(0)
            
            # Toggle nao-bloqueante do buzzer (200ms)
            if time.ticks_diff(current_time, last_buzzer_toggle) > 200:
                last_buzzer_toggle = current_time
                buzzer_state = not buzzer_state
                if buzzer_state:
                    buzzer.freq(500)
                    buzzer.duty_u16(32768)
                else:
                    buzzer.duty_u16(0)
        else:
            led_green.value(0)
            led_yellow.value(0)
            led_red.value(1)
            
            # Toggle nao-bloqueante rapido (50ms)
            if time.ticks_diff(current_time, last_buzzer_toggle) > 50:
                last_buzzer_toggle = current_time
                buzzer_state = not buzzer_state
                if buzzer_state:
                    buzzer.freq(1000)
                    buzzer.duty_u16(32768)
                else:
                    buzzer.duty_u16(0)

if __name__ == '__main__':
    main()