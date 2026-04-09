from machine import Pin, PWM, ADC
import time

# ======== MODOS ========
MODO_MANUAL = 0
MODO_RETORNO = 1
MODO_SECUENCIA = 2

modo = MODO_MANUAL

# ======== ADC ========
Pot1 = ADC(Pin(34))
Pot1.width(ADC.WIDTH_12BIT)

Pot2 = ADC(Pin(35))
Pot2.width(ADC.WIDTH_10BIT)

# ======== BOTONES ========
botonRetorno = Pin(23, Pin.IN, Pin.PULL_UP)
botonSecuencia = Pin(22, Pin.IN, Pin.PULL_UP)

# ======== LEDS ========
ledV = Pin(17, Pin.OUT)
ledR = Pin(16, Pin.OUT)

# ======== BUZZER (PWM) ========
buzzer = PWM(Pin(18))
buzzer.freq(500)   
buzzer.duty(0)

# ======== SERVOS ========
Servo1 = PWM(Pin(21), freq=50)
Servo2 = PWM(Pin(19), freq=50)

# ======== ANTIRREBOTE ========

ultimo_tiempo = 0

# ======== FUNCIONES ========

def angulo_a_duty(angulo):
    return int(40 + (angulo / 180) * 115)

def mover_servo(servo, angulo):
    servo.duty(angulo_a_duty(angulo))

# ======== INTERRUPCIONES ========

def retorno(pin):
    global modo, ultimo_tiempo
    t = time.ticks_ms()
    if time.ticks_diff(t, ultimo_tiempo) > 200:
        modo = MODO_RETORNO
        ultimo_tiempo = t

def secuencia(pin):
    global modo, ultimo_tiempo
    t = time.ticks_ms()
    if time.ticks_diff(t, ultimo_tiempo) > 200:
        modo = MODO_SECUENCIA
        ultimo_tiempo = t

botonRetorno.irq(trigger=Pin.IRQ_FALLING, handler=retorno)
botonSecuencia.irq(trigger=Pin.IRQ_FALLING, handler=secuencia)

# ======== POSICIONES ========
base_ini = 90
brazo_ini = 0

# ======== LOOP PRINCIPAL ========

while True:

    # ======== MODO MANUAL ========
    if modo == MODO_MANUAL:
        ledV.on()
        ledR.off()
        buzzer.duty(0)

        val1 = Pot1.read()
        val2 = Pot2.read()

        ang1 = (val1 / 4095) * 180
        ang2 = (val2 / 1023) * 180

        mover_servo(Servo1, ang1)
        mover_servo(Servo2, ang2)

        time.sleep(0.05)

    # ======== MODO RETORNO ========
    elif modo == MODO_RETORNO:
        ledV.off()
        ledR.on()

        buzzer.freq(1000)    
        buzzer.duty(500) 

        # llevar ambos servos a 0°
        for ang in range(90, -1, -2):
            mover_servo(Servo1, ang)
            mover_servo(Servo2, ang)
            time.sleep(0.02)

        # volver a la posición de los potenciómetros
        val1 = Pot1.read()
        val2 = Pot2.read()

        ang1 = (val1 / 4095) * 180
        ang2 = (val2 / 1023) * 180

        for i in range(50):
            mover_servo(Servo1, ang1)
            mover_servo(Servo2, ang2)
            time.sleep(0.02)

        buzzer.duty(0)
        modo = MODO_MANUAL

    # ======== MODO SECUENCIA ========
    elif modo == MODO_SECUENCIA:
        ledV.off()
        ledR.on()

        buzzer.freq(1000)  
        buzzer.duty(200)

        # Secuencia automática
        for ang in range(60, 120, 2):
            mover_servo(Servo1, ang)
            mover_servo(Servo2, 120 - (ang - 60))
            time.sleep(0.05)

        for ang in range(120, 60, -2):
            mover_servo(Servo1, ang)
            mover_servo(Servo2, 120 - (ang - 60))
            time.sleep(0.05)

        # Retorno al punto inicial
        for ang in range(60, base_ini, 2 if base_ini > 60 else -2):
            mover_servo(Servo1, ang)
            time.sleep(0.02)

        for ang in range(120, brazo_ini, -2 if brazo_ini < 120 else 2):
            mover_servo(Servo2, ang)
            time.sleep(0.02)

        buzzer.duty(0)
        modo = MODO_MANUAL