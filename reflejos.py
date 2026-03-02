from machine import Pin, mem32
from micropython import const
import time
import random

# CONFIGURACIÓN PINES

led_R = Pin(5, Pin.OUT)
led_A = Pin(17, Pin.OUT)
led_V = Pin(16, Pin.OUT)
Buzzer = Pin(18, Pin.OUT)

# BOTONES JUGADOR 1

boton_p1_R = Pin(27, Pin.IN, Pin.PULL_UP)
boton_p1_A = Pin(26, Pin.IN, Pin.PULL_UP)
boton_p1_V = Pin(25, Pin.IN, Pin.PULL_UP)
boton_p1_Z = Pin(21, Pin.IN, Pin.PULL_UP)

# BOTONES JUGADOR 2

boton_p2_R = Pin(12, Pin.IN, Pin.PULL_UP)
boton_p2_A = Pin(14, Pin.IN, Pin.PULL_UP)
boton_p2_V = Pin(19, Pin.IN, Pin.PULL_UP)
boton_p2_Z = Pin(13, Pin.IN, Pin.PULL_UP)

boton_Start = Pin(4, Pin.IN, Pin.PULL_UP)
boton_End = Pin(23, Pin.IN, Pin.PULL_UP)
boton_Game = Pin(22, Pin.IN, Pin.PULL_UP)

GPIO_OUT_REG = const(0x3FF44004)

# CONTROL DE MODO

modo_simon = False

# SALIDAS (REGISTROS)

def TODO_OFF():
    mem32[GPIO_OUT_REG] = 0

def led_R_ON():
    mem32[GPIO_OUT_REG] = 0b00000000000000000000000000100000 

def led_A_ON():
    mem32[GPIO_OUT_REG] = 0b00000000000000100000000000000000 

def led_V_ON():
    mem32[GPIO_OUT_REG] = 0b00000000000000010000000000000000 

def Buzzer_ON():
    mem32[GPIO_OUT_REG] = 0b00000000000001000000000000000000 

# ANTIREBOTE
def presionado(boton):
    if boton.value() == 0:
        time.sleep_ms(20)
        if boton.value() == 0:
            while boton.value() == 0: pass 
            return True
    return False

# VERIFICAR CAMBIO DE MODO
def verificar_cambio_modo():
    global modo_simon
    
    if presionado(boton_Game):
        modo_simon = not modo_simon
        TODO_OFF()
        time.sleep_ms(300)

# LÓGICA SIMON DICE
def encender_indice(indice):
    TODO_OFF()
    if indice == 0: led_R_ON()
    elif indice == 1: led_A_ON()
    elif indice == 2: led_V_ON()
    elif indice == 3: Buzzer_ON()
    time.sleep(1) 
    TODO_OFF()
    time.sleep(1)

def juego_simon():
    global modo_simon
    print("//// MODO SIMON DICE ////")
    secuencia = []
    
    while modo_simon:
        
        verificar_cambio_modo()
        if not modo_simon:
            return
        
        secuencia.append(random.randint(0, 3))
        
        for s in secuencia:
            verificar_cambio_modo()
            if not modo_simon:
                return
            encender_indice(s)
        
        for s in secuencia:
            esperando = True
            while esperando:
                
                verificar_cambio_modo()
                if not modo_simon:
                    return 
                
                eleccion = -1
                if presionado(boton_p1_R): eleccion = 0
                elif presionado(boton_p1_A): eleccion = 1
                elif presionado(boton_p1_V): eleccion = 2
                elif presionado(boton_p1_Z): eleccion = 3
                
                if eleccion != -1:
                    encender_indice(eleccion)
                    if eleccion != s:
                        print(f"ERROR: Fallaste en nivel {len(secuencia)}")
                        Buzzer_ON()
                        time.sleep(1)
                        TODO_OFF()
                        modo_simon = False
                        return
                    esperando = False
        
        print(f"Nivel {len(secuencia)} completado!")
        time.sleep(1)

# PROGRAMA
while True:

    verificar_cambio_modo()

    if modo_simon:
        juego_simon()
        modo_simon = False
        TODO_OFF()
        time.sleep_ms(300)
        continue

    TODO_OFF()
    print("//// JUEGO DE REFLEJOS ////")
    print("//// Pulse BOTON GRIS para iniciar ////")
    print("//// Pulse BOTON BLANCO para SIMON DICE ////")
    
    while not presionado(boton_Start): 
        verificar_cambio_modo()
        if modo_simon:
            break

    if modo_simon:
        continue

    print("//// SELECIONE # JUGADORES ////")
    print("BOTON ROJO = 1 Jugador  BOTON AMARILLO = 2 Jugadores")
    
    game = 0
    while game == 0:
        verificar_cambio_modo()
        if modo_simon:
            break
        if presionado(boton_p1_R): game = 1
        elif presionado(boton_p1_A): game = 2

    if modo_simon:
        continue

    p1, p2, ronda = 0, 0, 0

    # MODO 1 JUGADOR
    if game == 1:
        print("MODO 1 JUGADOR")
        while True:
            verificar_cambio_modo()
            if modo_simon:
                break

            TODO_OFF()
            time.sleep(random.uniform(1, 3))

            salidaR = random.randint(0, 3)

            if salidaR == 0: led_R_ON()
            elif salidaR == 1: led_A_ON()
            elif salidaR == 2: led_V_ON()
            elif salidaR == 3: Buzzer_ON()

            inicio, acierto, salir = time.ticks_ms(), False, False
            
            while not acierto:
                verificar_cambio_modo()
                if modo_simon:
                    break

                if presionado(boton_End): 
                    salir = True
                    break
                
                if salidaR == 0 and presionado(boton_p1_R): acierto = True
                elif salidaR == 1 and presionado(boton_p1_A): acierto = True
                elif salidaR == 2 and presionado(boton_p1_V): acierto = True
                elif salidaR == 3 and presionado(boton_p1_Z): acierto = True

            if modo_simon or salir:
                break 
            
            tiempo = time.ticks_diff(time.ticks_ms(), inicio)
            TODO_OFF()
            p1 += 1
            ronda += 1
            print(f"Ronda: {ronda} | Tiempo: {tiempo} ms | Puntos: {p1}")
            time.sleep(1.5) 

        print(f"\n--- PARTIDA FINALIZADA ---")
        print(f"Puntaje Final: {p1} puntos en {ronda} rondas.")
        time.sleep(2)

    # MODO 2 JUGADORES
    elif game == 2:
        print("MODO 2 JUGADORES")
        while True:
            verificar_cambio_modo()
            if modo_simon:
                break

            TODO_OFF()
            time.sleep(random.uniform(1, 3))
            salidaR = random.randint(0, 3)

            if salidaR == 0: led_R_ON()
            elif salidaR == 1: led_A_ON()
            elif salidaR == 2: led_V_ON()
            elif salidaR == 3: Buzzer_ON()

            inicio, quien, salir = time.ticks_ms(), 0, False
            
            while quien == 0:
                verificar_cambio_modo()
                if modo_simon:
                    break

                if presionado(boton_End): 
                    salir = True
                    break

                if salidaR == 0 and presionado(boton_p1_R): quien = 1
                elif salidaR == 1 and presionado(boton_p1_A): quien = 1
                elif salidaR == 2 and presionado(boton_p1_V): quien = 1
                elif salidaR == 3 and presionado(boton_p1_Z): quien = 1
                elif salidaR == 0 and presionado(boton_p2_R): quien = 2
                elif salidaR == 1 and presionado(boton_p2_A): quien = 2
                elif salidaR == 2 and presionado(boton_p2_V): quien = 2
                elif salidaR == 3 and presionado(boton_p2_Z): quien = 2

            if modo_simon or salir:
                break
            
            tiempo = time.ticks_diff(time.ticks_ms(), inicio)
            TODO_OFF()
            ronda += 1
            if quien == 1: p1 += 1
            else: p2 += 1
            print(f"Ronda: {ronda} | Gano P{quien} | Tiempo: {tiempo} ms | Marcador: {p1}-{p2}")
            time.sleep(1.5)

        print("RESULTADOS FINALES")
        print(f"Rondas jugadas: {ronda}")
        print(f"Puntaje P1: {p1} | Puntaje P2: {p2}")

    time.sleep(1)