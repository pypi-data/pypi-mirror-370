
# VL53L3CX Python

  Simple library for interacting with VL53L3CX sensors via python. This project is based on the [VL53L0X_rasp_python](https://github.com/johnbryanmoore/VL53L0X_rasp_python) project by John Bryan Moore. 

Connect your VL35L3CX module of choice via V+, GND, I2C clock, I2C data and xshut if you are using more then one sensor. The default address is 0x29. If you are using more sensors, drive the xshut high for all sensors but one, change address, then drive next xshut low, change address and repeat the process until all sensors have unique addresses.

*(Note that there is no support for multiplexers as I originally built this for my own use and later I thought to myself the library might come in handy for someone and it is probably worth sharing.)* 

  

# Installing

  

```
pip install VL53L3CX
```

  

# Usage

Look into examples to get basic gist of the usage. There are two simple python scripts - distance and change-address that probably cover all the usage cases you would ever need.

**Basic functions are:**  
`VL53L3CX.open()` - starts I2C  
`VL53L3CX.start_ranging()` - starts the sensor itself  
`VL53L3CX.stop_ranging()` - stops the sensor  
`VL53L3CX.get_distance()` - returns the measured distance in millimeters, should be called with `if VL53L3CX.is_ranging_ready():`  
`VL53L3CX.is_ranging_ready()` - returns true if sensor is ready to be read  
`VL53L3CX.change_address(new_address)` - changes the current I2C address to a new one specified  

**Not properly tested bonus functions I didn't end up using:**  
`VL53L3CX.set_distance_mode(mode)` - set distance mode to 1-short, 2-medium, 3-long  
`VL53L3CX.set_timing_budget(timing_budget)` - in microseconds  
`VL53L3CX.wait_for_data()` - interrupt the program until data is ready  





