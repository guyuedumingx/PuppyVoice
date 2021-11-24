from assistantlib.configuration import Configuration
from assistantlib.build_in import *

configuration = Configuration()

devices = []
for name,config in configuration.devices.items():
    config[name] = name
    devices.append(eval(config['type'])(config))

print(devices)
print(devices[1].port)
