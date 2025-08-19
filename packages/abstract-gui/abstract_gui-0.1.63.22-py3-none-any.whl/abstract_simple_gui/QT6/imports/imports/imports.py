#!/usr/bin/env python3
import os,re,subprocess,sys,re,traceback,pydot, enum, inspect
from pathlib import Path
from typing import *
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import (
    QThread, pyqtSignal, 
     Qt 
    )
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QListWidgetItem, QMessageBox, QRadioButton,
    QButtonGroup, QCheckBox,QWidget,QTabWidget,
    QScrollArea, QGroupBox, QComboBox, QLayout,
    QWidget, QVBoxLayout, QLabel, QListWidget
)
from abstract_utilities import is_number,make_list,safe_read_from_json,read_from_file,make_dirs
from abstract_paths import invert_to_function_map,start_analyzer
from functools import partial, lru_cache
