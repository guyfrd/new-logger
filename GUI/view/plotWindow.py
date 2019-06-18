from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
from PySide2.QtWidgets import QPushButton,QSpacerItem, QHBoxLayout,QLineEdit,QWidget,QDialog, QMainWindow,QTextEdit, QVBoxLayout,QGridLayout,QLabel, QComboBox,QGroupBox, QGridLayout

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PySide2 import QtCore, QtWidgets, QtCharts

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



progname = os.path.basename(sys.argv[0])
progversion = "0.1"


# class MyMplCanvas(FigureCanvas):
#     """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

#     def __init__(self,  x, y, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)
#         FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#         for tick in self.axes.get_xticklabels():
#             tick.set_rotation(45)
#         self.axes.plot(x, y, "-r*")
#         print(type(self.axes))
#     def compute_initial_figure(self):
#         pass

    


class plotMainWidget( QWidget):
    def __init__(self):
        super(plotMainWidget, self).__init__()
        print("plotMainWidget")

       
        self.filter_groupBox = QGroupBox("Filters")
        self.filter_msg_comboBox = QComboBox()
        self.filter_msg_label = QLabel("Message:")
        self.filter_msg_label.setBuddy(self.filter_msg_comboBox)
        
        layout = QGridLayout()
        layout.setColumnMinimumWidth(9,500)
        layout.setColumnMinimumWidth(1,30)
        layout.addWidget(self.filter_msg_label, 0,0)
        layout.addWidget(self.filter_msg_comboBox, 0, 2, 0, 8)
        self.filter_groupBox.setLayout(layout)
        
        self.chart_groupBox = QGroupBox("Chart")


        mainLayout = QGridLayout()
        mainLayout.addWidget(self.filter_groupBox, 0, 0)
        mainLayout.addWidget(self.chart_groupBox, 1,0, 9,0)
        self.setLayout(mainLayout)

