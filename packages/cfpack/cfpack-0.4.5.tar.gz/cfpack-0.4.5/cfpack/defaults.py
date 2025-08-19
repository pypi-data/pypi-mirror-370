from . import print # overload print function to activate colours and function signatures
from . import stop # simple 'stop()' in any script to drop into python debugger mode
from . import matplotlibrc # load default matplotlib styles
from matplotlib import get_backend
print("matplotlib backend: '"+get_backend()+"'", color='green')
# forward physical constants for quick access to enable interactive calculations (speed_of_light, pc, m_sol, etc.)
from .constants import *
