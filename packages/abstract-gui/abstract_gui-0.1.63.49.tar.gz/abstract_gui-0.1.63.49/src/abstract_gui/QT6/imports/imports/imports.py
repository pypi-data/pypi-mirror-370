#!/usr/bin/env python3
from typing import *
from functools import partial
from abstract_utilities import eatAll
from abstract_utilities.type_utils import MIME_TYPES
from PyQt6.QtGui import QTextCursor # add this import
from PyQt6.QtCore import (
    Qt, QObject, QThread, pyqtSignal, qInstallMessageHandler,
    QtMsgType
)
from PyQt6.QtWidgets import (
    QLabel, QListView, QCompleter, QComboBox, QSizePolicy,
    QApplication, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget,
    QPushButton, QMessageBox, QAbstractItemView, QLineEdit,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout
    )
import os,re,subprocess,sys,re,traceback,pydot, enum, inspect, sys, traceback, threading,json,traceback,logging,requests
from abstract_utilities import is_number,make_list,safe_read_from_json,read_from_file,make_dirs
from abstract_paths import invert_to_function_map,start_analyzer
from functools import partial, lru_cache
