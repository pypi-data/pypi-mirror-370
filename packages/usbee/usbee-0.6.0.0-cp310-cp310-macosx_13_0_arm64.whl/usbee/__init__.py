import os
import sys

module_name = __name__

# The following is needed to put everything into the usbee namespace. Otherwise it will end up in usbee.usbee.

usbee_dir_path = os.path.dirname(__file__)

sys.path.insert(0, usbee_dir_path)

del sys.modules[module_name]
sys.modules[module_name] = __import__("usbee")

del usbee_dir_path, module_name
