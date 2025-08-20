from .utils import *

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QLineEdit, QHBoxLayout, QGroupBox, QCheckBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QMouseEvent, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QFileInfo
import cv2
from fabio.edfimage import EdfImage
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import numpy
import matplotlib.pyplot as plt
import string
from PIL import Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
import copy
import time as timelib
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys
import re
import argparse
import cv2
import matplotlib

import matplotlib.pyplot as plt

matplotlib.use('Agg')





def main_gui():
    
    app = QApplication(sys.argv)
    cropper = ImageCropper()
    sys.exit(app.exec_())


