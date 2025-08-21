import os
from abstract_gui import getInitForAllTabs,startConsole
ABS_PATH = os.path.abspath(__name__)
ABS_DIR = os.path.dirname(ABS_PATH)

getInitForAllTabs(ABS_DIR)
from .imageViewerTab import imageViewerTab,startImageViewerConsole
