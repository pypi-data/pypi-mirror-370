# kmpico - MicroPython Library for Raspberry Pi Pico

A user-friendly MicroPython library for Raspberry Pi Pico to easily control various sensors and modules like LEDs, buzzers, motors, DHT sensors, OLED displays, and more.

## ⚠️ Important Note
This is a **MicroPython** library. It cannot be installed on a standard computer using `pip`. You need to transfer the files to your Raspberry Pi Pico's filesystem.

## Installation
1. Connect your Raspberry Pi Pico to your computer.
2. Using a tool like Thonny IDE, copy the entire `kmpico` folder to the `/lib` directory on your Pico.

## Dependencies
This library requires the following external libraries to be present on your Pico's filesystem. Please install them separately:
- `dht.py`
- `ssd1306.py`
- `neopixel.py`

## Basic Usage
```python
from kmpico import DigitalLED
from time import sleep

# Assuming an LED is connected to GP15
led = DigitalLED(15)

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
    