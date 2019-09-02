#!/usr/bin/env micropython
"""
MIT license
(C) Konstantin Belyalov 2017-2018
"""



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
import tinyweb



logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("Testing")

global np

lightcmd = [1,6,5,5,5]
np = neopixel.NeoPixel(machine.Pin(4), 6)


# Init our customers DB with some fake values
db = {'1': {'firstname': 'Alex', 'lastname': 'River'},
      '2': {'firstname': 'Lannie', 'lastname': 'Fox'}}
next_id = 3


# If you're familiar with FLaskRestful - you're almost all set! :)
# Tinyweb have only basic functionality comparing to Flask due to
# environment where it intended to run on.
class CustomersList():

    def get(self, data):
        """Return list of all customers"""
        return db

    def post(self, data):
        """Add customer"""
        global next_id
        db[str(next_id)] = data
        next_id += 1
        # Return message AND set HTTP response code to "201 Created"
        return {'message': 'created'}, 201


# Simple helper to return message and error code
def not_found():
    page = '<!doctype html><html lang="en"><form> <input class="MyButton" type="button" value="Your Text Here" onclick="window.location.href=\'http://www.hyperlinkcode.com/button-links.php\'" /> </form></html>'
    return page


# Detailed information about given customer
class Customer():

    def not_exists(self):
        page = '<form> <input class="MyButton" type="button" value="Your Text Here" onclick="window.location.href=\'http://www.hyperlinkcode.com/button-links.php\'" /> </form>'
        return page

    def get(self, data, user_id):
        """Get detailed information about given customer"""
        if user_id not in db:
            return not_found()
        return db[user_id]

    def put(self, data, user_id):
        """Update given customer"""
        if user_id not in db:
            return not_found()
        db[user_id] = data
        return {'message': 'updated'}

    def delete(self, data, user_id):
        """Delete customer"""
        if user_id not in db:
            return not_found()
        del db[user_id]
        return {'message': 'successfully deleted'}


def run():
    # Create web server application
    app = tinyweb.webserver()
    # Add our resources
    
    @app.route('/')
    @app.route('/index.html')
    async def index(req, resp):
        # Just send file
        await resp.send_file('static/index.simple.html')
    
    app.add_resource(CustomersList, '/customers')
    app.add_resource(Customer, '/customers/<user_id>')
    app.add_resource(lightShow, '/light')
    app.run(host='0.0.0.0', port=8081, loop_forever=False)

class lightShow():
    
    def get(self, data):
        global lightcmd
        lightcmd = data['lightcmd'].split(',')
        lightcmd = [int(i) for i in lightcmd]
        return('Lights set to: {}'.format(data['lightcmd']))
    
    def not_exists(self):
        return {'message': 'no such customer'}, 404

    def put(self, data, user_id):
        """Update given customer"""
        if user_id not in db:
            return not_found()
        db[user_id] = data
        return {'message': 'updated'}

    def delete(self, data, user_id):
        """Delete customer"""
        if user_id not in db:
            return not_found()
        del db[user_id]
        return {'message': 'successfully deleted'}



def demo():
    n = np.n

    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep(.025)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep(.060)

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



def npset():
    for i in range(lightcmd[0]-1, lightcmd[1]):
        np[i] = (lightcmd[2], lightcmd[3], lightcmd[4])


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

async def changelights():
    while True:
        log.debug('{} : {}'.format(timeout(), lightcmd))
        npset()
        np.write()
        await asyncio.sleep(.5)
        

if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    run()
    loop.create_task(nptset())
    loop.create_task(changelights())
    
    loop.run_forever()

    # To test your server run in terminal:
    # - Get all customers:
    #       curl http://localhost:8081/customers
    # - Get detailed information about particular customer:
    #       curl http://localhost:8081/customers/1
    # - Add customer:
    #       curl http://localhost:8081/customers -X POST -d "firstname=Maggie&lastname=Stone"
    # - Update customer:
    #       curl http://localhost:8081/customers/2 -X PUT -d "firstname=Margo"
    # - Delete customer:
    #       curl http://localhost:8081/customers/1 -X DELETE
