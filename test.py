import sys
import platform
import importlib.util

print("Python EXE     : " + sys.executable)
print("Architecture   : " + platform.architecture()[0])
#print(importlib.util.find_spec("arcpy"))

