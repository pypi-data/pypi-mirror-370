# ElectroBlocks

**ElectroBlocks** is a Python library for communicating with Arduino-based educational hardware using a custom serial protocol. It simplifies control of servos, RGB LEDs, LCD screens, and more—especially in block-based coding environments like Blockly.

## Upgrade To New Version

- Go to this file [pyproject.toml](pyproject.toml)
- Change the version number by .1 `version = "0.1.8"`
- Push to main

## Features

- Auto-detects the first available Arduino Uno or Mega over USB
- Sends `config:` and control commands to the Arduino firmware
- Waits for `"System:READY"` and `"DONE_NEXT_COMMAND"` to sync logic
- Supports digital write, RGB LEDs, LCD printing, and servo control

## Installation

```bash
pip install electroblocks
```

## Example

```python
from electroblocks import ElectroBlocks

eb = ElectroBlocks()
eb.config_servo(5)
eb.move_servo(5, 90)
eb.config_rgb(3, 5, 6)
eb.set_rgb(255, 128, 0)
eb.config_lcd()
eb.lcd_print(0, 0, "Hello")
eb.lcd_clear()
eb.digital_write(13, 1)
eb.close()
```
