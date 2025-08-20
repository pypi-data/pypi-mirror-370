#!/usr/bin/env python3
from typing import *
from functools import partial
from abstract_utilities import eatAll
from abstract_utilities.type_utils import MIME_TYPES
from PyQt6.QtGui import QTextCursor, QColor, QBrush # add this import
from PyQt6.QtCore import (
    Qt, QObject, QThread, pyqtSignal, qInstallMessageHandler,
    QtMsgType, QTimer
)
from PyQt6.QtWidgets import (
    QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout,
    QCompleter, QFileDialog, QHeaderView, QLineEdit, QWidget,
    QListView, QComboBox, QFormLayout, QAbstractItemView, QCheckBox,
    QMainWindow, QTableWidgetItem, QTableWidget, QTextEdit,
    QApplication, QSizePolicy, QStatusBar, QMessageBox
    )
import time, re, pydot, inspect, threading, enum, sys, requests, subprocess, os, logging, traceback, re, json
from abstract_utilities import is_number,make_list,safe_read_from_json,read_from_file,make_dirs
from abstract_paths import invert_to_function_map,start_analyzer
from functools import partial, lru_cache
