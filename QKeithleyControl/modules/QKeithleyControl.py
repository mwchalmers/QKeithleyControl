#!/bin/python 
import visa
import time
import numpy as np

# Import d_plot and keithley driver
import drivers.keithley_2400

# Import Keithley control widgets
import modules.QKeithleyConfig
import modules.QKeithleySweep 
import modules.QKeithleyBias


# Import QT backends
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QStackedWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QCheckBox, QLabel
from PyQt5.QtCore import Qt

# Import matplotlibQT backends
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


# Subclass QMainWindow to customise your application's main window
class QKeithleyControl(QMainWindow):

	def __init__(self, *args, **kwargs):
		super(QKeithleyControl, self).__init__(*args, **kwargs)
		self.setWindowTitle("Keithley Control v0.1")

		# Generate main menu and toplevel widget. We will 
		# Render our controls into self.toplevel on menu selection
		self._gen_menu()		
		self.ui_stack = QStackedWidget(self)

		# Create widgets for each ui-mode
		self.ui_config = modules.QKeithleyConfig.QKeithleyConfig()
		self.ui_sweep = modules.QKeithleySweep.QKeithleySweep()
		self.ui_bias = modules.QKeithleyBias.QKeithleyBias()

		# Add ui-mode widgets to stack
		self.ui_stack.addWidget(self.ui_config)
		self.ui_stack.addWidget(self.ui_sweep)
		self.ui_stack.addWidget(self.ui_bias)

		# Set window central widget to stacked widget
		self.setCentralWidget(self.ui_stack)

		# Create empty keithley object
		self.keithley = None

	# Callback to update menu
	def _menu_callback(self, q):		

		if q.text() == "Configuration":
			self.ui_stack.setCurrentIndex(0)

		if q.text() == "Sweep Mode": 
			
			# Get Keithley handle
			self.keithley=self.ui_config._get_keithley_handle()

			# If Keitheley handle is initialized, pass to sweep widget. 
			if self.keithley is not None:
				self.ui_sweep._set_keithley_handle(self.keithley)
				self.ui_stack.setCurrentIndex(1)

			# Otherwise, display Keithley not initilized message
			else:				
				self._gen_warning_box("pyVISA Error","Keitheley GPIB not Initialized")		
				self.ui_stack.setCurrentIndex(0)

		if q.text() == "Bias Mode": 		

			# Get Keithley handle
			self.keithley=self.ui_config._get_keithley_handle()

			# If Keitheley handle is initialized, pass to bias widget. 
			if self.keithley is not None:
				self.ui_bias._set_keithley_handle(self.keithley)
				self.ui_stack.setCurrentIndex(2)

			# Otherwise, display Keithley not initilized message
			else:
				self._gen_warning_box("pyVISA Error","Keitheley GPIB not Initialized")		
				self.ui_stack.setCurrentIndex(0)

	# Generate Menu
	def _gen_menu(self):

		# Main Menu
		self.menu_bar = self.menuBar()
		
		# Add a selector menu items
		self.menu_selector = self.menu_bar.addMenu('Measurement Setup')

		# Add some various modes. These will generate windows in main layout
		self.menu_config = QAction("Configuration",self)
		self.menu_selector.addAction(self.menu_config)

		# Sweep Mode
		self.menu_sm = QAction("IV-Sweep Control",self)
		self.menu_selector.addAction(self.menu_sm)

		# Bias Mode
		self.menu_bm = QAction("IV-Bias Control",self)
		self.menu_selector.addAction(self.menu_bm)

		# Callback Trigge
		self.menu_selector.triggered[QAction].connect(self._menu_callback)

	# Method to generate warning box
	def _gen_warning_box(self, _title, _text): 
					
		# Message box to display error
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setText(_text)
		msg.setWindowTitle(_title)
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()	