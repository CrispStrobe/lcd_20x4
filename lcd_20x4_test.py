import machine
import time
from lcd_20x4 import LCD

print("MicroPython LCD Test Starting...")

# Initialize I2C and LCD
try:
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
    
    # Scan for devices first
    devices = i2c.scan()
    print("I2C devices found:", [hex(d) for d in devices])
    
    if not devices:
        print("No I2C devices found! Check wiring.")
        exit()
    
    # Try common addresses
    lcd_addr = None
    for addr in [0x27, 0x3F, 0x20]:
        if addr in devices:
            lcd_addr = addr
            break
    
    if lcd_addr is None:
        print("No LCD found at common addresses. Try:", [hex(d) for d in devices])
        exit()
    
    print(f"Using LCD at address: 0x{lcd_addr:02x}")
    
    # Initialize LCD
    lcd = LCD(i2c, addr=lcd_addr, cols=20, rows=4)
    print("LCD initialized successfully!")
    
except Exception as e:
    print(f"LCD initialization failed: {e}")
    exit()

# Simple tests that work in MicroPython
def test_basic_display():
    print("Test 1: Basic display")
    lcd.clear()
    lcd.print_line("MicroPython LCD", 0, center=True)
    lcd.print_line("Basic Test", 1, center=True)
    lcd.print_line("Line 3", 2)
    lcd.print_line("Line 4", 3)
    time.sleep(3)

def test_cursor_positioning():
    print("Test 2: Cursor positioning")
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.print("Top Left")
    
    lcd.set_cursor(10, 1)
    lcd.print("Mid Right")
    
    lcd.set_cursor(5, 2)
    lcd.print("Center")
    
    lcd.set_cursor(0, 3)
    lcd.print("Bottom Left")
    time.sleep(3)

def test_scrolling_text():
    print("Test 3: Scrolling text")
    lcd.clear()
    lcd.print_line("Scrolling Test:", 0)
    
    message = "This message is longer than 20 characters and will scroll!"
    
    for i in range(len(message) - 19):
        lcd.set_cursor(0, 1)
        # Clear line manually since we can't use ljust
        lcd.print(" " * 20)
        lcd.set_cursor(0, 1)
        lcd.print(message[i:i+20])
        time.sleep(0.2)
    
    time.sleep(2)

def test_counter():
    print("Test 4: Counter")
    lcd.clear()
    lcd.print_line("Counter Test:", 0)
    
    for i in range(20):
        lcd.set_cursor(0, 1)
        # Manual string formatting since f-strings might not work in older MicroPython
        counter_text = "Count: " + str(i)
        # Pad manually
        counter_text = counter_text + " " * (20 - len(counter_text))
        lcd.print(counter_text)
        time.sleep(0.5)

def test_button_interactive():
    print("Test 5: Button test (press BOOT button)")
    button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    
    lcd.clear()
    lcd.print_line("Button Test", 0, center=True)
    lcd.print_line("Press BOOT button", 1)
    lcd.print_line("Count: 0", 2)
    
    count = 0
    last_state = 1
    
    while count < 5:
        current_state = button.value()
        
        if last_state == 1 and current_state == 0:  # Button pressed
            count += 1
            lcd.set_cursor(0, 2)
            count_text = "Count: " + str(count)
            count_text = count_text + " " * (20 - len(count_text))
            lcd.print(count_text)
            time.sleep(0.2)  # Debounce
        
        last_state = current_state
        time.sleep(0.05)
    
    lcd.print_line("Button test complete!", 3)
    time.sleep(2)

def test_backlight():
    print("Test 6: Backlight control")
    lcd.clear()
    lcd.print_line("Backlight Test", 0, center=True)
    
    for i in range(3):
        lcd.print_line("Backlight OFF in " + str(3-i), 1)
        time.sleep(1)
    
    lcd.no_backlight()
    time.sleep(2)
    lcd.backlight()
    lcd.print_line("Backlight ON!", 1, center=True)
    time.sleep(2)

# Run all tests
try:
    test_basic_display()
    test_cursor_positioning()
    test_scrolling_text()
    test_counter()
    test_backlight()
    test_button_interactive()
    
    # Final message
    lcd.clear()
    lcd.print_line("All Tests Complete!", 0, center=True)
    lcd.print_line("LCD Working Great!", 1, center=True)
    lcd.print_line("MicroPython Ready", 2, center=True)
    
    print("All tests completed successfully!")
    
except Exception as e:
    print(f"Test failed: {e}")
    lcd.clear()
    lcd.print_line("Test Error:", 0)
    error_msg = str(e)[:20]
    lcd.print_line(error_msg, 1)
