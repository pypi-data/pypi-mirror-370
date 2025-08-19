<div style="text-align: center; align: center;">
  <h1 align="center">
    <a href="https://drx.works/"><img src="https://drx.works/wp-content/themes/drx/images/logo.jpg" width="300"></a>
    <br>
    <i>DrX Works Lissajoux API</i>
    <br>
  </h1>
</div>

This library provides the python API for a DrX Works Lissajoux device.

## Installation
Install the lastest python3 version.
Open command line interface (cmd) and type `pip3 install --upgrade drx-lissajoux`

## Usage examples

The examples below can be run by first saving the example code as a `example.py` file using for instance Notepad.
Place the license xml file which was provided by DrX Works during delivery of the Lissajoux in the same location as where you saved `example.py`.
Please adjust the `HOST` constant in each of the example scripts to the IP adress of your Lissajoux.
Please adjust the `KEY_FILE` constant in each of the example scripts to the location of your license file.
Note that the license file name is diffrent for each device since it contains the organization and serial number, for example `key_TFS_L15.4-7021151.xml`
The example can now be run using `python3 example.py` from the command line.
The path of the command line needs to be set `cd "path/to/the/example/folder"` to the folder of the `example.py` file.

### Normal operation of the API

The example below demonstrates the normal use of this API library.

```
import logging

from drx_lissajoux.api import Lissajoux, cmd

# Set the debug level, normal operation: "INFO"
logging.basicConfig(level="DEBUG")

HOST = "192.168.1.100"
KEY_FILE = "./key_file.xml"

# constuct the API object
api = Lissajoux(host=HOST, key_file=KEY_FILE)

# retrieve all properties from the lissajoux and store in the cache, call this each time the properties need to be updated
api.get_state()

# Get some values from the cache and print them
print(f"Global interlock: {api.global_interlock}")
print(f"F1 power: {api.F1_power}")
print(f"Frequency: {api.F1_frequency}")
print(f"Cavity temperature: {api.Cavity_temperature}")
print(f"PSU 5V: {api.PSU_5_volt}")

# Set the frequency of the lissajoux to a new value
api.F1_frequency = 2418.0

# Close the connection
api.close()
```

### Available properties

The example below will print all available properties of the Lissajoux that can be used with this library.

```
from drx_lissajoux.api import Lissajoux

HOST = "192.168.1.100"
KEY_FILE = "./key_file.xml"

api = Lissajoux(host=HOST, key_file=KEY_FILE)

print("\nAvailable properties:")
for prop in api.available_properties:
    print(prop)
```

### Sending custom commands to the Lissajoux

The example below demonstrates how to send custom commands to the Lissajoux.
A full list of the available commands for the Lissajoux can be found in the API section in the manual supplied with the device.

```
from drx_lissajoux.api import Lissajoux, cmd

HOST = "192.168.1.100"
KEY_FILE = "./key_file.xml"

# constuct the API object
api = Lissajoux(host=HOST, key_file=KEY_FILE)

# send a single command to GET the frequency
cmd_freq = api.send_command(cmd("Frq"))
print(f"Frequency: {cmd_freq.value}")

# send a single command to SET the frequency
cmd_freq = api.send_command(cmd("Frq", "=", 2417.0))
print(f"Frequency: {cmd_freq.value}")

# send 5 commands in one message to GET all PSU voltages
response = api.send_command([cmd("V05"), cmd("V55"), cmd("V15"), cmd("Vm5"), cmd("V24")])
for val in response.values():
    print(f"{val.cmd}: {val.value}")

# Close the connection
api.close()
```