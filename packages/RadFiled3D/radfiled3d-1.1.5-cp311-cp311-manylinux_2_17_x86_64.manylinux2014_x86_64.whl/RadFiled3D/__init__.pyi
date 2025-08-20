import ctypes
import os

# Module imports:



lib_path = os.path.join(os.path.dirname(__file__), 'RadFiled3D.cpython-311-x86_64-linux-gnu.so')
lib = ctypes.CDLL(lib_path)

