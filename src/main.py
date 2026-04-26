from machine import Pin
import time

def test_led():
    # Inicializa o LED no GPIO 22 como saida
    led_verde = Pin(22, Pin.OUT)
    
    # Pisca o LED
    led_verde.value(1)
    time.sleep(0.5)
    led_verde.value(0)
    time.sleep(0.5)
    led_verde.value(1)
    
    print("LED_TEST_OK")

if __name__ == '__main__':
    test_led()