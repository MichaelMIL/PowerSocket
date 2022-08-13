import time
from machine import Pin, Timer
import uasyncio


class PowerSocket:
    socket_count = 0 # number of sockets

    def __init__(self, led_pin, button_pin, relay_pin,long_press_duration_sec=1, auto_turn_off_time_mins = 30, debug =None):
        PowerSocket.socket_count += 1 # incrementing number of sockets
        self.socket_id = PowerSocket.socket_count # setting socket id
        self.state = 0 # 0 = off, 1 = on
        self.led = Pin(led_pin, Pin.OUT) # setting led pin to output
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP) # setting button pin to input with pull up resistor
        self.relay = Pin(relay_pin, Pin.OUT) # setting relay pin to output
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.toggle) # setting button to trigger rising edge - toggle on button press
        self.time_pressed = 0 # time when button was pressed (ms)
        self.auto_turn_off_timer = Timer() # timer for auto turn off
        self.auto_turn_off_time_mins = auto_turn_off_time_mins # time in minutes to auto turn off
        self.long_press_duration_sec = long_press_duration_sec * 1000 # time in seconds to long press
        self.debug = debug # debug mode, prints state and time when button was pressed
        self.blink_task = None # loop for blinking led
        self.main_loop = uasyncio.get_event_loop() # getting main loop
        self.turn_off() # setting socket to off
        

    def turn_on(self, timer_time= None):
        if timer_time == None:
            timer_time = self.auto_turn_off_time_mins * 60 * 1000 # converting time to ms
        self.state = 1 # setting state to on
        self.led.value(1) # setting led to on
        self.relay.value(1) # setting relay to on
        if timer_time > 0:
            if not self.auto_turn_off_timer: 
                self.auto_turn_off_timer = Timer() # creating timer for auto turn off
            self.auto_turn_off_timer = self.auto_turn_off_timer.init(period= timer_time , mode=Timer.ONE_SHOT, callback=self.turn_off) # setting timer for auto turn off
        if timer_time == 0:
            # Blink led and run infinitly
            if self.blink_task:
                self.blink_task.cancel() # cancel blinking task
            self.blink_task = self.main_loop.create_task(infinet_blink(self.led)) # creating task for blinking led
        if self.debug:
            print(f'Socket ID: {self.socket_id}, State: {self.state}')

    def turn_off(self, timer = None):
        if self.blink_task:
            self.blink_task.cancel() # cancel blinking task
        if timer:
            print(f'Socket ID: {self.socket_id}, auto turn off')
            timer.deinit() # deinitializing timer
            self.blink(times=10) # blinking 10 times (warning before turning off)
        self.state = 0 # setting state to off
        self.led.value(0) # setting led to off
        self.relay.value(0) # setting relay to off
        if self.debug:
            print(f'Socket ID: {self.socket_id}, State: {self.state}')
        
    def blink(self, times=1):
        # blinking socket led
        for i in range(times):
            self.led.value(1)
            time.sleep(0.1)
            self.led.value(0)
            time.sleep(0.1)
            if self.debug:
                print(f'Socket ID: {self.socket_id}, Blinking: {i}')   
    
    def toggle(self, pin=None):
        start_time = time.ticks_ms() # getting time when button was pressed (ms)
        if abs_time_diff(start_time, self.time_pressed) > 500: # if time difference is greater than 250ms
            press_duration = self.button_press_duration(start_time) # getting button press time (ms)
            if self.debug:
                print(f' press duration: {press_duration}, long press duration: {self.long_press_duration_sec}')

            if press_duration > self.long_press_duration_sec: # if button was pressed for more than 1s
                self.time_pressed = start_time # setting time when button was pressed (ms)
                if self.debug:
                    print(f'Long press: time from last click {abs_time_diff(start_time, self.time_pressed)} -- press_duration: {press_duration}') # long press  
                self.turn_on(timer_time=0) # turn on socket


            if press_duration > 50 and press_duration < self.long_press_duration_sec: # prevent double click, debouncing
                if self.debug:
                    print(f'Short press: time from last click {abs_time_diff(start_time, self.time_pressed)} -- press_duration: {press_duration}') # short press
                self.time_pressed = start_time
                if self.state == 0:
                    self.turn_on()
                else:
                    self.turn_off()
        else:
            self.time_pressed = start_time

    def button_press_duration(self, start_time, max=1000):
        last_time= time.ticks_ms()
        while not self.button.value(): # while button is pressed
            last_time = time.ticks_ms() # getting time when button was pressed (ms)
            if abs_time_diff(last_time, start_time) > max:
                self.turn_on(timer_time=0) # turn on socketreturn abs_time_diff(last_time, start_time)
                break
        return abs_time_diff(last_time, start_time) # returning button press time (ms)

def abs_time_diff(time1, time2):
    # returns absolute time difference in ms
    return abs(time.ticks_diff(time1 , time2))

async def infinet_blink(led):
        # Blink led and run infinitly
        while True:
            led.value(1)
            await uasyncio.sleep(0.5)
            led.value(0)
            await uasyncio.sleep(0.5)
