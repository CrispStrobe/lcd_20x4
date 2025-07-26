# ESP32 LCD 20x4 Display Library

A simple MicroPython library for controlling 20x4 I2C LCD displays with e.g. ESP32 microcontrollers. Features basic functionality, error handling, methods for text display, cursor control, custom characters, and some more.

## Features

- ✅ **20x4 LCD Support** - Optimized for 2004A displays with PCF8574T I2C backpack
- ✅ **MicroPython Compatible** - Works perfectly with ESP32 MicroPython firmware  
- ✅ **I2C Communication** - Simple 4-wire connection (VCC, GND, SDA, SCL)
- ✅ **Custom Characters** - Create and display custom 5x8 pixel characters
- ✅ **Text Positioning** - Cursor control and line-based text placement
- ✅ **Scrolling Support** - Horizontal display scrolling functions
- ✅ **Backlight Control** - Turn display backlight on/off
- ✅ **Extended Characters** - Support for hex character notation `{0xFF}`
- ✅ **Debugging Tools** - Built-in I2C scanner and basic troubleshooting utilities

## Hardware Requirements

### Components
- **ESP32 Development Board** (ESP-WROOM-32 or compatible)
- **20x4 LCD Display** (2004A or compatible)
- **I2C Backpack Module** (PCF8574T or PCF8574AT)
- **Jumper Wires** (4 pieces)
- **Breadboard** (optional)

### Wiring Diagram

```
ESP32          LCD I2C Module
-----          --------------
GND      →     GND
3.3V     →     VCC  (or 5V if needed)
GPIO 21  →     SDA
GPIO 22  →     SCL
```

**Pin Configuration:**
- **SDA (Data):** GPIO 21 (default I2C data pin)
- **SCL (Clock):** GPIO 22 (default I2C clock pin)
- **Power:** 3.3V or 5V depending on your LCD module
- **Ground:** GND

## Installation

### 1. Flash MicroPython to ESP32

```bash
# Install esptool
pip install esptool

# Erase flash
esptool.py --chip esp32 --port COM3 erase_flash

# Flash MicroPython firmware
esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-version.bin
```

### 2. Upload Library Files

Upload the files to your ESP32 using Thonny IDE or ampy.

### 3. Find Your LCD I2C Address

```python
import machine

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
devices = i2c.scan()
print("I2C devices found:", [hex(d) for d in devices])
```

Common addresses: `0x27`, `0x3F`, `0x20`

## Quick Start

### Basic Usage

```python
import machine
from improved_lcd import LCD

# Initialize I2C and LCD
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
lcd = LCD(i2c, addr=0x27, cols=20, rows=4)

# Display text
lcd.clear()
lcd.print_line("Hello ESP32!", 0, center=True)
lcd.print_line("LCD is working!", 1)
lcd.set_cursor(0, 2)
lcd.print("Custom position")
```

### Advanced Features

```python
# Custom characters
heart = [0b00000, 0b01010, 0b11111, 0b11111, 0b01110, 0b00100, 0b00000, 0b00000]
lcd.create_char(0, heart)
lcd.write(0)  # Display heart symbol

# Extended character printing
lcd.print_ext("Temperature: 25{0x01}C")  # With degree symbol

# Scrolling display
lcd.scroll_display_right()
lcd.scroll_display_left()

# Backlight control
lcd.backlight()      # Turn on
lcd.no_backlight()   # Turn off
```

## API Reference

### Initialization

```python
LCD(i2c, addr=0x27, cols=20, rows=4, charsize=LCD_5x8DOTS)
```

### Basic Display Methods

| Method | Description |
|--------|-------------|
| `clear()` | Clear entire display |
| `home()` | Move cursor to top-left position |
| `set_cursor(col, row)` | Set cursor to specific position (0-indexed) |
| `print(text)` | Print text at current cursor position |
| `print_line(text, line, center=False)` | Print text on specific line |

### Display Control

| Method | Description |
|--------|-------------|
| `display()` | Turn display on |
| `no_display()` | Turn display off |
| `backlight()` | Turn backlight on |
| `no_backlight()` | Turn backlight off |

### Cursor Control

| Method | Description |
|--------|-------------|
| `cursor()` | Show cursor |
| `no_cursor()` | Hide cursor |
| `blink()` | Enable cursor blinking |
| `no_blink()` | Disable cursor blinking |

### Advanced Features

| Method | Description |
|--------|-------------|
| `create_char(location, charmap)` | Create custom character (0-7) |
| `print_ext(text)` | Print with hex character support |
| `scroll_display_left()` | Scroll display left |
| `scroll_display_right()` | Scroll display right |
| `clear_line(line)` | Clear specific line |

## Contributing

Contributions are welcome!

## Acknowledgements

Takes some ideas and details from https://github.com/a13ssandr0/liquidcrystal_i2c-linux
