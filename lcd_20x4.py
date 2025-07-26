import machine
import time
from re import match

# LCD Commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Entry mode flags
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Display control flags
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Cursor/display shift flags
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Function set flags
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

# PCF8574 pin mapping
En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit

class LCD:
    def __init__(self, i2c, addr=0x27, cols=20, rows=4, charsize=LCD_5x8DOTS):
        """Initialize LCD with I2C connection
        
        Args:
            i2c: MicroPython I2C object
            addr: I2C address (default 0x27)
            cols: Number of columns (default 20)
            rows: Number of rows (default 4)
            charsize: Character size (default 5x8)
        """
        self._i2c = i2c
        self._addr = addr
        self._cols = cols
        self._rows = rows
        self._charsize = charsize
        self._backlightval = LCD_BACKLIGHT
        
        # Set display function based on rows and character size
        if self._rows > 1:
            self._displayfunction = LCD_4BITMODE | LCD_2LINE
        elif not self._charsize == 0 and self._rows == 1:
            self._displayfunction = LCD_1LINE | LCD_5x10DOTS
        else:
            self._displayfunction = LCD_1LINE | LCD_5x8DOTS

        # Initialize LCD according to HD44780 datasheet
        time.sleep_ms(50)  # Wait for power-up
        
        # Put LCD into 4-bit mode (this is according to HD44780 datasheet)
        self.write4bits(0x03 << 4)
        time.sleep_ms(5)
        self.write4bits(0x03 << 4)
        time.sleep_ms(5)
        self.write4bits(0x03 << 4)
        time.sleep_us(150)
        
        # Finally, set to 4-bit interface
        self.write4bits(0x02 << 4)
        
        # Set number of lines, font size, etc.
        self.command(LCD_FUNCTIONSET | self._displayfunction)
        
        # Turn display on with no cursor or blinking
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()
        
        # Clear display
        self.clear()
        
        # Initialize text direction (left to right)
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)
        
        # Return home
        self.home()

    def write4bits(self, data):
        """Write 4 bits to the LCD"""
        self.expander_write(data)
        self.pulse_enable(data)

    def expander_write(self, cmd):
        """Write byte to I2C expander"""
        self._i2c.writeto(self._addr, bytes([cmd | self._backlightval]))
        time.sleep_us(100)  # Short delay

    def pulse_enable(self, data):
        """Pulse the enable bit to latch command"""
        self.expander_write(data | En)
        time.sleep_us(500)  # Enable pulse width
        self.expander_write(data & ~En)
        time.sleep_us(100)  # Hold time

    def send(self, cmd, mode=0):
        """Send command or data to LCD"""
        self.write4bits(mode | (cmd & 0xF0))
        self.write4bits(mode | ((cmd << 4) & 0xF0))

    def command(self, value):
        """Send command to LCD"""
        self.send(value, 0)

    def write(self, value):
        """Write data to LCD"""
        self.send(value, Rs)

    # High-level commands
    def clear(self):
        """Clear the display"""
        self.command(LCD_CLEARDISPLAY)
        time.sleep_ms(2)  # Clear command takes longer

    def home(self):
        """Return cursor to home position"""
        self.command(LCD_RETURNHOME)
        time.sleep_ms(2)  # Home command takes longer

    def set_cursor(self, col, row):
        """Set cursor position (0-indexed)"""
        # Corrected row offsets for 20x4 displays
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self._rows:
            row = self._rows - 1
        if col >= self._cols:
            col = self._cols - 1
        self.command(LCD_SETDDRAMADDR | (col + row_offsets[row]))

    # Display control
    def no_display(self):
        """Turn display off"""
        self._displaycontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def display(self):
        """Turn display on"""
        self._displaycontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def no_cursor(self):
        """Turn cursor off"""
        self._displaycontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def cursor(self):
        """Turn cursor on"""
        self._displaycontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def no_blink(self):
        """Turn blinking cursor off"""
        self._displaycontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def blink(self):
        """Turn blinking cursor on"""
        self._displaycontrol |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    # Scrolling functions
    def scroll_display_left(self):
        """Scroll display left"""
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scroll_display_right(self):
        """Scroll display right"""
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    # Text direction
    def left_to_right(self):
        """Set text direction left to right"""
        self._displaymode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def right_to_left(self):
        """Set text direction right to left"""
        self._displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def autoscroll(self):
        """Enable autoscroll"""
        self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def no_autoscroll(self):
        """Disable autoscroll"""
        self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    # Custom characters
    def create_char(self, location, charmap):
        """Create custom character
        
        Args:
            location: Character location (0-7)
            charmap: List of 8 integers defining character pattern
        """
        if not isinstance(charmap, list):
            raise TypeError(f"charmap must be a list, got {type(charmap)}")
        
        if location < 0 or location > 7:
            raise ValueError(f"location must be 0-7, got {location}")
        
        if len(charmap) > 8:
            raise ValueError(f"charmap too long: {len(charmap)}, max 8")
        
        # Pad shorter characters with blank lines
        while len(charmap) < 8:
            charmap.append(0x00)
        
        # Validate charmap values
        for i, row in enumerate(charmap):
            if not isinstance(row, int):
                raise TypeError(f"charmap[{i}] must be int, got {type(row)}")
            if row < 0 or row > 0x1F:
                raise ValueError(f"charmap[{i}] must be 0-31, got {row}")
        
        # Write character to CGRAM
        self.command(LCD_SETCGRAMADDR | (location << 3))
        for row in charmap:
            self.write(row)

    # Backlight control
    def no_backlight(self):
        """Turn backlight off"""
        self._backlightval = LCD_NOBACKLIGHT
        self.expander_write(0)

    def backlight(self):
        """Turn backlight on"""
        self._backlightval = LCD_BACKLIGHT
        self.expander_write(0)

    # String printing
    def print(self, string):
        """Print string to LCD"""
        for char in string:
            self.write(ord(char))

    def print_ext(self, string):
        """Print extended string with hex character support
        
        Use {0xFF} syntax for special characters
        """
        while string:
            # Look for hex pattern {0xFF}
            hex_match = match(r'\{0[xX][0-9a-fA-F]{2}\}', string)
            if hex_match:
                # Convert hex to integer and write
                hex_value = int(hex_match.group(0)[1:-1], 16)
                self.write(hex_value)
                string = string[6:]  # Skip the {0xFF} part
            else:
                # Normal character
                self.write(ord(string[0]))
                string = string[1:]

    # Convenience methods
    def print_line(self, text, line, center=False):
        """Print text on specific line, optionally centered"""
        self.set_cursor(0, line)
        
        if center:
            # Center the text
            padding = (self._cols - len(text)) // 2
            text = " " * padding + text
        
        # Pad or truncate to fit line - MicroPython compatible
        text = text[:self._cols]  # Truncate if too long
        text = text + " " * (self._cols - len(text))  # Pad with spaces
        self.print(text)

    def clear_line(self, line):
        """Clear specific line"""
        self.set_cursor(0, line)
        self.print(" " * self._cols)
