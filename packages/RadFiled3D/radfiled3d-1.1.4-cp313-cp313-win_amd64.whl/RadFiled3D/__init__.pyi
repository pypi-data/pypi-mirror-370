import ctypes
import os

# Module imports:



lib_path = os.path.join(os.path.dirname(__file__), 'RadFiled3D.cp313-win_amd64.pyd')
lib = ctypes.CDLL(lib_path)

