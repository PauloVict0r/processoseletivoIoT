from machine import Pin, PWM, time_pulse_us, WDT
import neopixel
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

def set_color(np, color):
    for i in range(np.n):
        np[i] = color
    np.write()

def main():
    wdt = WDT(timeout=5000)
    
    # fita NeoPixel no pino 22 com 3 LEDs
    np = neopixel.NeoPixel(Pin(22, Pin.OUT), 3)
    
    buzzer = PWM(Pin(23))
    buzzer.duty_u16(0)
    
    trig = Pin(5, Pin.OUT)
    echo = Pin(18, Pin.IN)
    
    filter = MovingAverage(5)
    
    last_sensor_read = time.ticks_ms()
    last_buzzer_toggle = time.ticks_ms()
    buzzer_state = False
    
    # Variaveis da maquina de estados
    last_movement_time = time.ticks_ms()
    last_avg_dist = -1
    
    print("SMART_PARKING_V2_OK")
    
    while True:
        wdt.feed()
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
            
        # Deteccao de movimento (de 3cm)
        if last_avg_dist < 0 or abs(avg_dist - last_avg_dist) > 3:
            last_movement_time = current_time
            last_avg_dist = avg_dist
            
        # ESTADO 1: Vaga Livre
        if avg_dist > 150:
            set_color(np, (0, 255, 0)) # Verde
            buzzer.duty_u16(0)
            
        # ESTADO 3: Estacionado (Parado por 5s)
        elif time.ticks_diff(current_time, last_movement_time) > 5000:
            set_color(np, (0, 0, 0)) # LEDs Apagados (descanso)
            buzzer.duty_u16(0)
            
        # ESTADO 2: Estacionando 
        else:
            if 50 <= avg_dist <= 150:
                set_color(np, (255, 255, 0)) # Amarelo
                if time.ticks_diff(current_time, last_buzzer_toggle) > 200:
                    last_buzzer_toggle = current_time
                    buzzer_state = not buzzer_state
                    if buzzer_state:
                        buzzer.freq(500)
                        buzzer.duty_u16(32768)
                    else:
                        buzzer.duty_u16(0)
            else:
                set_color(np, (255, 0, 0)) # Vermelho
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