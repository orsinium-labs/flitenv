
import os
import platform


MAIN_ENV = 'main'
IS_WINDOWS = (os.name == 'nt' or platform.system() == 'Windows')
VENVS = '.venvs'
