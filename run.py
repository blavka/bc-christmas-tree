#!/usr/bin/env python3
"""
Effects takeover of here
https://raw.githubusercontent.com/jgarff/rpi_ws281x/master/python/examples/strandtest.py
"""
import time
import base64
import json
import logging as log
from logging import DEBUG, INFO
import paho.mqtt.client as mqtt

LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


class Led_Strip:
    def __init__(self, client, count, mode='rgbw', brightest=255):
        self.count = count
        self.rgbw = mode == 'rgbw'
        self.buf = ([0, 0, 0, 0] if self.rgbw else [0, 0, 0]) * count
        self.ltime = 0
        self.lcnt = 0
        self.client = client

    def setPixelColor(self, i, color):
        if i >= self.count:
            return
        offset = (4 if self.rgbw else 3) * i
        self.buf[offset] = color[0]
        self.buf[offset + 1] = color[1]
        self.buf[offset + 2] = color[2]

    def show(self):
        pixels = base64.b64encode(bytearray(self.buf)).decode()
        t = int(time.time())
        if t != self.ltime:
            log.debug("fps %d" % self.lcnt)
            self.ltime = t
            self.lcnt = 0

        self.lcnt += 1

        self.client.publish('nodes/base/led-strip/-/set', json.dumps({'pixels': pixels}))


def colorWipe(strip, color, wait_ms=55):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.count):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChase(strip, color, wait_ms=55, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.count, 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.count, 3):
                strip.setPixelColor(i+q, (0, 0, 0))


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=55, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.count):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def rainbowCycle(strip, wait_ms=55, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.count):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.count) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChaseRainbow(strip, wait_ms=55):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.count, 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.count, 3):
                strip.setPixelColor(i+q, (0, 0, 0))


def mgtt_on_connect(client, userdata, flags, rc):
    log.info('Connected to MQTT broker (code %s)', rc)


if __name__ == '__main__':
    log.basicConfig(level=DEBUG, format=LOG_FORMAT)

    client = mqtt.Client()
    client.on_connect = mgtt_on_connect
    client.connect('localhost', 1883, keepalive=10)

    client.loop_start()

    strip = Led_Strip(client, 150, 'rgb')
    # strip = Led_Strip(client, 144, 'rgbw')

    print('Press Ctrl-C to quit.')
    while True:
        # Color wipe animations.
        colorWipe(strip, (255, 0, 0))  # Red wipe
        colorWipe(strip, (0, 255, 0))  # Blue wipe
        colorWipe(strip, (0, 0, 255))  # Green wipe
        # # Theater chase animations.
        theaterChase(strip, (127, 127, 127))  # White theater chase
        theaterChase(strip, (200, 0, 0))  # Red theater chase
        theaterChase(strip, (0, 0, 200))  # Blue theater chase
        # Rainbow animations.
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
