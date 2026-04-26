from machine import Pin, PWM
import time

def test_buzzer():
    # Inicializa o Buzzer no GPIO 23 com PWM
    buzzer = PWM(Pin(23))
    
    # Emite um bipe de 1kHz com 50% de duty cycle
    buzzer.freq(1000)
    buzzer.duty_u16(32768)
    time.sleep(1)
    
    # Desliga o bipe
    buzzer.duty_u16(0)
    time.sleep(0.5)
    
    print("BUZZER_TEST_OK")

if __name__ == '__main__':
    test_buzzer()