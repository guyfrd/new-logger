import os
import sys
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QMainWindow, QMessageBox, QPushButton, QWidget,QVBoxLayout, QFileDialog,QComboBox,QGridLayout,QLineEdit,QCheckBox, QLabel, QAction, QGroupBox, QTableView,QHBoxLayout
from GUI.controller.controller import dataController
import re

icon_path = ''
if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS,'resources')
else:
    icon_path = os.path.join(sys.path[0], 'resources', 'images')

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.json_path = ''
        self.dc = dataController()
        self.centralWidget = MainWidget(self.dc)
        self.setCentralWidget(self.centralWidget)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.resize(1500, 600)


    def open(self):
        fileName, filtr =  QFileDialog.getOpenFileName(self)
        print("open file")
        if fileName:
            self.loadFile(fileName)

    def openJson(self):
        print("openJson")
        fileName, filtr =  QFileDialog.getOpenFileName(self)
        if fileName:
            self.loadJSONFile(fileName)

    def openDB(self):
        print("openDB")
        fileName, filtr =  QFileDialog.getOpenFileName(self)
        if fileName:
            self.loadDb(fileName)



    def createActions(self):
        icon_path = '/home/osboxes/log/new-log/files/icons/'
        open_bin_file = os.path.join(icon_path,'bin.png')

        self.openAct = QAction( QIcon(open_bin_file),
                "&Open...", self, shortcut= QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        open_json_file = os.path.join(icon_path,'json.png')

        self.openJSONAct =  QAction( QIcon(open_json_file),
                            "&Open...", self, shortcut= QKeySequence.Open,
                            statusTip="Open JSON file", triggered=self.openJson)
        open_db= os.path.join(icon_path,'db.png')
        self.openDBact = QAction( QIcon(open_db),
                            "&Open...", self, shortcut= QKeySequence.Open,
                            statusTip="Open DB", triggered=self.openDB)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.openJSONAct)
        self.fileMenu.addAction(self.openDBact)
        self.fileMenu.addSeparator()


        self.editMenu = self.menuBar().addMenu("&Edit")
        self.menuBar().addSeparator()



    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.openJSONAct)
        self.fileToolBar.addAction(self.openDBact)


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def loadFile(self, fileName):
        file = QFile(fileName)
        if self.json_path == '':
            QMessageBox.warning(self, "Application", "load json file first\n")
            return
        self.dc.initBinFile(fileName, self.json_path)
        self.centralWidget.initDomainCombo()

    def loadJSONFile(self, fileName):
        self.json_path = fileName


    def loadDb(self, fileName):
        self.dc.initDB(fileName)
        self.centralWidget.initDomainCombo()

    def loadMsgExpand(self, index):
        model = self.data_model.getMsgexpandModel(index)
        self.central_view.setSourceMsgExpanf(model)


class MainWidget( QWidget):
    def __init__(self, controller):
        super(MainWidget, self).__init__()
        self.dc = controller

        self.filterGroupBox_1 = QGroupBox("Filter by domain")
        self.filterGroupBox_2 = QGroupBox("Filter by text")

        # >>>>>>>>>>>>INIT TREE VIEW <<<<<<<<<<<<<<<<<<<<
        self.msg_view = QTableView()
        self.msg_view.setAlternatingRowColors(True)
        self.msg_view.setSortingEnabled(True)
        self.msg_view.setSelectionBehavior(QTableView.SelectRows);

        self.msg_expand_view = QTableView()
        self.msg_expand_view.setAlternatingRowColors(True)
        self.fetch_up_button =  QPushButton("up")
        self.fetch_down_button =  QPushButton("down")

        # layout #1 - dataView
        dataLayout = QGridLayout()
        dataLayout.addWidget(self.fetch_down_button ,1 ,0,)
        dataLayout.addWidget(self.fetch_up_button , 2, 0)

        dataLayout.addWidget(self.msg_view, 0, 1, 3, 3)
        dataLayout.addWidget(self.msg_expand_view, 0, 4, 3, 4)
        dataLayout.setColumnMinimumWidth(0,60)
        dataLayout.setColumnStretch(1, 30)
        dataLayout.setColumnStretch(2, 10)

        self.sourceGroupBox = QGroupBox("Data")
        self.sourceGroupBox.setLayout(dataLayout)
        # >>>>>>filter group #1 <<<<<<<<<<<<,,
        self.filterDomainComboBox = QComboBox()
        self.filterDomainLabel = QLabel("Filter &domain:")
        self.filterDomainLabel.setBuddy(self.filterDomainComboBox)
        self.filterMsgComboBox = QComboBox()
        self.filterMsgLabel = QLabel("Filter &Msg:")
        self.filterMsgLabel.setBuddy(self.filterDomainComboBox)

        # checksboxes
        self.sortCaseSensitivityCheckBox = QCheckBox("Case sensitive sorting")
        self.filterCaseSensitivityCheckBox = QCheckBox("Case sensitive filter")
        self.filterCaseSensitivityCheckBox.setChecked(True)
        self.sortCaseSensitivityCheckBox.setChecked(True)

        # filter optons
        self.filterPatternLineEdit = QLineEdit()
        self.filterPatternLineEdit.setText("init(system_start, system_shutdown), pam_busybox_shadow(login_attempt), FOTA_app()")
        self.filterPatternLabel = QLabel("&Filter pattern:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)
        self.filterPatternButton = QPushButton("Find")

        open_text_layout = QGridLayout()
        open_text_layout.addWidget(self.filterPatternLabel, 0, 0, 1 ,1)
        open_text_layout.addWidget(self.filterPatternLineEdit, 0, 1, 1, 11)
        open_text_layout.addWidget(self.filterPatternButton, 0, 12)
        self.filterGroupBox_2.setLayout(open_text_layout)


        self.filterDomainComboBox.currentIndexChanged.connect(self.domainComboChange)
        self.filterMsgComboBox.currentIndexChanged.connect(self.msgComboChange)
        self.fetch_up_button.clicked.connect(self.fetchMoreClicked)
        self.fetch_down_button.clicked.connect(self.fetchLessClicked)
        self.filterPatternButton.clicked.connect(self.openTextFeatchMsg)



        # LAYOUTS
        filterLayout_1 = QGridLayout()
        filterLayout_1.addWidget(self.filterDomainLabel, 0, 0, 1,1)
        filterLayout_1.addWidget(self.filterDomainComboBox, 0, 1, 1, 10)

        filterLayout_1.addWidget(self.filterMsgLabel,1,0,2,1)
        filterLayout_1.addWidget(self.filterMsgComboBox, 1, 1,1,10)
        self.filterGroupBox_1.setLayout(filterLayout_1)


        # parent layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sourceGroupBox,1)
        mainLayout.addWidget(self.filterGroupBox_1)
        mainLayout.addWidget(self.filterGroupBox_2)
        self.setLayout(mainLayout)

        self.setWindowTitle("log message parser")
        self.modle = None

    def initDomainCombo(self):
        self.filterDomainComboBox.clear()
        self.filterDomainComboBox.addItem('ALL')
        self.filterDomainComboBox.addItems(self.dc.getInitData())

    def domainComboChange(self, i):
        if self.filterDomainComboBox.currentText() == '':
            return
        print("domainComboChange {}".format(self.filterDomainComboBox.currentText()))

        if self.filterDomainComboBox.currentText() == 'ALL':
            self.modle = self.dc.getAllMsg()
            self.filterMsgComboBox.clear()
        else:
            domain = self.filterDomainComboBox.currentText()
            self.modle = self.dc.getDatabyDomain(domain)
            self.filterMsgComboBox.clear()
            self.filterMsgComboBox.addItem("ALL")
            msg_by_domain = self.dc.getMsgListByDomain(self.filterDomainComboBox.currentIndex() - 1)
            self.filterMsgComboBox.addItems(msg_by_domain)

        self.msg_view.setModel(self.modle)

    def msgComboChange(self):
        msg_type = self.filterMsgComboBox.currentText()
        if msg_type == 'ALL' or not msg_type:
            return

        print("msgComboChange {}".format(msg_type))
        self.modle = self.dc.getDataByMsg(msg_type)
        self.msg_view.setModel(self.modle)



    def fetchMoreClicked(self):
        if self.filterDomainComboBox.currentText() == 'ALL':
            model = self.dc.fetchMoreAllMsg()
        else:
            model = self.dc.fetchMore(self.filterDomainComboBox.currentText())

        self.msg_view.setModel(model)


    def fetchLessClicked(self):
        modle = self.dc.fetchLess()
        self.msg_view.setModel(modle)

    def openTextFeatchMsg(self):
        x= re.split(r',\s*(?![^()]*\))', self.filterPatternLineEdit.text())
        list = {}
        for i in x:
            list[i[:i.find("(")]] = (i[i.find("(")+1:i.find(")")].split(', '))
        modle = self.dc.fetchOpenText(list)
        self.msg_view.setModel(modle)
