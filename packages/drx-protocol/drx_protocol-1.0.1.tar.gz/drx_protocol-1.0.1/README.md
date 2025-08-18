# DrX Works communication protocol

This library is not intended to be used on its own.
Instead each DrX works device has its own API library which uses this drx_protocol library as a dependency for the basic communication protocol.

## Installation
Install the lastest python3 version.
Open command line interface (cmd) and type `pip3 install --upgrade drx-protocol`

## Usage example

See the manual of the DrX device for the full list of available commands for your device.
However it is recommended to use the dedicated API libary of your device which already includes all commands.

```
import logging

from drx_protocol.protocol import drx_protocol, drx_command as cmd

# Set the debug level, normal operation: "INFO"
logging.basicConfig(level="DEBUG")

HOST = "192.168.1.100"
SERIAL = "fill in the serial number of the device"
ORGANIZATION = "fill in the organization from the software license provided with the device"
SIGNATURE = "fill in the signature from the software license provided with the device"

##########################################################################################################################################################
# Normal operation of the API
##########################################################################################################################################################

# constuct the API object
api = drx_protocol(
    host = HOST,
    serial = SERIAL,
    organization = ORGANIZATION,
    signature = SIGNATURE,
)

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