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


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self,  x, y, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(45)
        self.axes.plot(x, y, "-r*")
        
    def compute_initial_figure(self):
        pass

    
plot_msg = ['RAM_free']

class plotMainWidget( QWidget):
    def __init__(self, controller):
        super(plotMainWidget, self).__init__()
        print("plotMainWidget")
        self.dc = controller
        self.plot = None
        self.filter_groupBox = QGroupBox("Filters")
        self.filter_msg_comboBox = QComboBox()
        self.filter_msg_label = QLabel("Message:")
        self.filter_msg_label.setBuddy(self.filter_msg_comboBox)
        self.filter_msg_comboBox.addItems(plot_msg)
        self.filter_msg_button = QPushButton("Show")
        self.filter_msg_button.clicked.connect(self.filterButtonClicked)
        
        layout = QGridLayout()
        # layout.setColumnMinimumWidth(9,100)
        # layout.setColumnMinimumWidth(1,30)
        layout.addWidget(self.filter_msg_label, 0,0)
        layout.addWidget(self.filter_msg_comboBox, 0, 2, 0, 8)
        layout.addWidget(self.filter_msg_button, 0, 10)
        self.filter_groupBox.setLayout(layout)
        
        self.plot_groupBox = QGroupBox("Chart")


        mainLayout = QGridLayout()
        mainLayout.addWidget(self.filter_groupBox, 0, 0)
        mainLayout.addWidget(self.plot_groupBox, 1,0, 9,0)
        self.setLayout(mainLayout)

    def filterButtonClicked(self):
        msg = self.filter_msg_comboBox.currentText()
        data_set = self.dc.getDataSet(msg) 
        time_axis = []
        val_axis = []
        for i in data_set:
            time_axis.append(i[3])
            val_axis.append(i[4])
        
        self.plot = MyMplCanvas(time_axis, val_axis)
        self.curr_plot_layout = QVBoxLayout()
        self.curr_plot_layout.addWidget(self.plot)
        self.plot_groupBox.setLayout(self.curr_plot_layout)

    def cleanPlot(self):
        if(self.plot):
            print("clean")
            self.curr_plot_layout.removeWidget(self.plot)