# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import machine
import network
import socket
from machine import Pin, I2C
import micropython
# import ssd1306
from time import sleep
import time
from ntptime import settime 
import neopixel
import _thread
import gc
import ure
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("LightShow")


global np 
np = neopixel.NeoPixel(machine.Pin(4), 6)


# ESP32 Pin assignment 
# i2c = I2C(-1, scl=Pin(17), sda=Pin(5))


#oled_width = 128
#oled_height = 64
#oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)


async def demo():
    n = np.n

    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(25)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()


def Convert(string): 
    li = list(string.split(b","))
    lo = []
    j = 0
    for i in li:
        lo.append(int(i))
        j += 1
    return lo 


def web_serv(s):
    html = """<!DOCTYPE html>
    <html>
        <head> <title>ESP32 Pins</title> </head>
        <body> <h1>ESP32 Pins</h1>
            <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
        </body>
         <h3>Pick a Color:</h3>
    <div style="margin:auto;width:236px;">
    </html>
    """
    regex = ure.compile('\(')
    regex2 = ure.compile('\)')
    regex3 = ure.compile('led')

        
    cl, addr = s.accept()
    log.info('{} : client connected from: {}'.format(timeout(), addr))
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        log.debug('{} : {}'.format(timeout(), line))
        if regex3.search(line):
            out1 = regex.split(line)
            log.debug('{} : {}'.format(timeout(), out1))
            lightraw = regex2.split(out1[1])[0]
            lightcmd = Convert(lightraw)
            
        if not line or line == b'\r\n':
            break
    #response = html % '\n'.join(rows)
    cl.send(line)
    cl.close()
    return lightcmd



def npset(lightcmd):
    for i in range(lightcmd[0]-1, lightcmd[1]):
        np[i] = (lightcmd[2], lightcmd[3], lightcmd[4])
    np.write()

def nptset():
    while True:
        try:
            settime()
            log.debug('{} : Timeset'.format(timeout()))
        except KeyboardInterrupt:
            raise
        except:
            log.warning('{} : timeout exception'.format(timeout()))
        time.sleep(20)

def timeout():
    tm =str("{}/{}/{} {:02d}:{:02d}:{:02d}".format(machine.RTC().datetime()[0],machine.RTC().datetime()[1], machine.RTC().datetime()[2], machine.RTC().datetime()[4]-4, machine.RTC().datetime()[5], machine.RTC().datetime()[6]))
    return(tm)



#oled.text('Booting...', 0, 10)
#oled.show()
_thread.start_new_thread(demo, ())
_thread.start_new_thread(nptset, ())

run = 1
#oled.fill(0)
#oled.show()
while run:
    lightcmd = web_serv(s)
    log.info('{} : {}'.format(timeout(), lightcmd))
    #tm =str(machine.RTC().datetime()[4]-4) + ":" + str(machine.RTC().datetime()[5]) + ":" + str(machine.RTC().datetime()[6])
    log.debug('{} : Time thru the loop'.format(timeout()))
#    oled.fill(0)
#    oled.text('Light Show!', 0, 10)
#    oled.text('Last Command @:', 0, 20)
#    oled.text(timeout(), 0, 30)
#    oled.text(str(lightcmd), 0, 40)
#    oled.show()
    npset(lightcmd)
    time.sleep(1)
    run = 1


