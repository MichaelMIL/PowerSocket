from PowerSocket import PowerSocket
import uasyncio



async def main():
    socket1 = PowerSocket(led_pin=7, button_pin=0, relay_pin=8,long_press_duration_sec=1, auto_turn_off_time_mins = 30, debug=True) # creating socket 1
    socket2 = PowerSocket(led_pin=4, button_pin=1, relay_pin=9,long_press_duration_sec=1, auto_turn_off_time_mins = 30, debug=True) # creating socket 2
    socket3 = PowerSocket(led_pin=5, button_pin=2, relay_pin=10,long_press_duration_sec=1, auto_turn_off_time_mins = 30, debug=True) # creating socket 3
    socket4 = PowerSocket(led_pin=6, button_pin=3, relay_pin=11,long_press_duration_sec=1, auto_turn_off_time_mins = 30, debug=True) # creating socket 4
    while True:
        await uasyncio.sleep(0)
    

loop = uasyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()



