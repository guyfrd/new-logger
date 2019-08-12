import os
import sys
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMainWindow,QApplication,QStackedWidget, QMessageBox, QTextEdit, QPushButton, QWidget,QVBoxLayout, QFileDialog,QComboBox,QGridLayout,QLineEdit,QCheckBox, QLabel, QAction, QGroupBox, QTableView,QHBoxLayout
from GUI.controller.controller import dataController
import re
import datetime
from GUI.view.plotWindow import plotMainWidget
from  GUI.view.mainWidget import MainWidget

icon_path = ''
if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS,'files')
else:
    icon_path = os.path.join(sys.path[0], 'files', 'icons')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.json_path = ''
        self.currDB = ''
        self.dc = dataController()
        self.createWidgetStack()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.resize(1400, 800)
        self.setWindowTitle("Logger")
        self.setCentralWidget(self.widget_stack)


    def createWidgetStack(self):
        self.widget_stack = QStackedWidget()
        self.centralWidget = MainWidget(self.dc)
        self.plotWidget =  plotMainWidget(self.dc)
        self.widget_stack.addWidget(self.centralWidget)
        self.widget_stack.addWidget(self.plotWidget)
        self.widget_stack.setCurrentIndex(0)

    def open(self):
        fileName =  QFileDialog.getOpenFileName(self)[0]
        if self.json_path == '':
            QMessageBox.warning(self, "Application", "load json file first\n")
            return
        
        if fileName != '':
            print(fileName)
            self.dc.initBinFile(fileName, self.json_path)
            self.centralWidget.initDomainCombo()
            self.createNewPlotView()  
            self.widget_stack.setCurrentIndex(0)

    def openJson(self):
        fileName =  QFileDialog.getOpenFileName(self)[0]
        if fileName:
            self.json_path = fileName
        self.widget_stack.setCurrentIndex(0)

    def openDB(self):
        fileName=  QFileDialog.getOpenFileName(self)[0]
        if fileName:
            self.dc.initDB(fileName)
            self.centralWidget.initDomainCombo()
            if fileName != self.currDB:
                self.createNewPlotView()            
                self.currDB = fileName 
        self.widget_stack.setCurrentIndex(0)    
    
    def createNewPlotView(self):
        self.widget_stack.removeWidget(self.plotWidget)
        self.plotWidget =  plotMainWidget(self.dc)
        self.widget_stack.addWidget(self.plotWidget)
    
    def saveToFile(self):
        path, filtr =  QFileDialog.getSaveFileName(self)
        if path:
            self.centralWidget.CW_exportToFile(path)
    
    def openChart(self):
        if not self.dc:
            QMessageBox.warning(self, "Application", "load json file first\n")
            return
        self.widget_stack.setCurrentIndex(1)
    
    def goBack(self):
       self.widget_stack.setCurrentIndex(0)


    def createActions(self):
        open_bin_file = os.path.join(icon_path,'bin.png')

        self.openAct = QAction( QIcon(open_bin_file),
                "&Open...", self, shortcut= QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        open_json_file = os.path.join(icon_path,'json.png')

        self.openJSONAct =  QAction( QIcon(open_json_file),
                            "Open...", self, shortcut= QKeySequence.Open,
                            statusTip="Open JSON file", triggered=self.openJson)
        open_db= os.path.join(icon_path,'db.png')
        self.openDBact = QAction( QIcon(open_db),
                            "Open...", self, shortcut= QKeySequence.Open,
                            statusTip="Open DB", triggered=self.openDB)
        disk_icon_path= os.path.join(icon_path,'save.png')
        self.saveToFileAct = QAction( QIcon(disk_icon_path),
                            "Save to file...", self, shortcut= QKeySequence.Open,
                            statusTip="save to file", triggered=self.saveToFile)
        chart_icon_path= os.path.join(icon_path,'chart.png')
        self.openChartAct = QAction( QIcon(chart_icon_path),
                            "Open chart windows", self, shortcut= QKeySequence.Open,
                            statusTip="open chart windows", triggered=self.openChart)
        back_icon_path= os.path.join(icon_path,'back.png')
        self.goBackAct = QAction( QIcon(back_icon_path),
                            "Go Back", self, shortcut= QKeySequence.Open,
                            statusTip="Go back", triggered=self.goBack)
   
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.openJSONAct)
        self.fileMenu.addAction(self.openDBact)
        self.fileMenu.addAction(self.saveToFileAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openChartAct)
        self.fileMenu.addAction(self.goBackAct)
     

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.openJSONAct)
        self.fileToolBar.addAction(self.openDBact)
        self.fileToolBar.addAction(self.saveToFileAct)
        self.fileToolBar.addAction(self.openChartAct)
        self.fileToolBar.addAction(self.goBackAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    

  
        
