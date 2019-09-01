# Test program for MicroPython asyncio
# Author: David Perdue
# Copyright David Perdue 2019
# 
# 

import esp32
import uasyncio as asyncio
import neopixel
import logging
import machine
import network
import socket
from machine import Pin, I2C
import micropython
from time import sleep
import time
from ntptime import settime 
import gc
import ure
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("Testing")

global np 
np = neopixel.NeoPixel(machine.Pin(4), 6)


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
        await asyncio.sleep_ms(25)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        await asyncio.sleep_ms(60)

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


async def nptset():
    while True:
        try:
            log.debug('{} : Timeset'.format(timeout()))
            settime()
            log.debug('{} : Timeset'.format(timeout()))
        except KeyboardInterrupt:
            raise
        except:
            log.warning('{} : timeout exception'.format(timeout()))
        await asyncio.sleep(3600)


def timeout():
    tm =str("{}/{}/{} {:02d}:{:02d}:{:02d}.{:06d}".format(machine.RTC().datetime()[0],machine.RTC().datetime()[1],
                                                    machine.RTC().datetime()[2], machine.RTC().datetime()[4]-4, 
                                                    machine.RTC().datetime()[5], machine.RTC().datetime()[6],
                                                    machine.RTC().datetime()[7])
                                                    )
    return(tm)


async def test():
    i = 0
    while True:
        log.debug('{} : async loop count {}'.format(timeout(), i))
        i += 1
        await asyncio.sleep_ms(0)


async def mainloop():
    while True:
        lightcmd = web_serv(s)
        log.info('{} : {}'.format(timeout(), lightcmd))
        log.debug('{} : Time thru the loop'.format(timeout()))
        npset(lightcmd)
        await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.create_task(nptset())
#loop.create_task(test())
loop.create_task(demo())

loop.run_forever()
