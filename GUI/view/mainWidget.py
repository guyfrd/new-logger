import os
import sys
import re
import datetime
from PySide2.QtWidgets import QMainWindow,QApplication,QStackedWidget, QMessageBox, QTextEdit, QPushButton, QWidget,QVBoxLayout, QFileDialog,QComboBox,QGridLayout,QLineEdit,QCheckBox, QLabel, QAction, QGroupBox, QTableView,QHBoxLayout




class MainWidget( QWidget):
    def __init__(self, controller):
        super(MainWidget, self).__init__()
        self.dc = controller
        self.curr_view_state = ''
        self.curr_model = None
        # >>>>>>>>>>>>INIT TREE VIEW <<<<<<<<<<<<<<<<<<<<
        self.msg_view = QTableView()
        self.msg_view.setAlternatingRowColors(True)
        self.msg_view.setSortingEnabled(True)
        self.msg_view.setSelectionBehavior(QTableView.SelectRows)
        self.fetch_up_button =  QPushButton("up")
        self.fetch_down_button =  QPushButton("down")
        self.num_row_to_show_label= QLabel("lines to show:")
        self.num_row_to_show_combbox = QComboBox()
        self.num_row_to_show_combbox.addItems(['10', '50', '100', '200'])
        self.jump_to_msg_label= QLabel("jump to message")
        self.jump_to_msg_lineEdit = QLineEdit()
        self.jump_to_msg_button = QPushButton("Show")

        
        # layout #1 - dataView
        dataLayout = QGridLayout()
        dataLayout.addWidget(self.msg_view, 0, 1, 11, 3)
        dataLayout.addWidget(self.jump_to_msg_label,3,0)
        dataLayout.addWidget(self.jump_to_msg_lineEdit,4,0)
        dataLayout.addWidget(self.jump_to_msg_button,5,0)
        dataLayout.addWidget(self.num_row_to_show_label, 0, 0)
        dataLayout.addWidget(self.num_row_to_show_combbox, 1,0)
        dataLayout.addWidget(self.fetch_down_button ,9 ,0,)
        dataLayout.addWidget(self.fetch_up_button , 10, 0)
        dataLayout.setColumnMinimumWidth(0,30)
        dataLayout.setColumnStretch(1, 30)
        dataLayout.setColumnStretch(2, 10)
        self.sourceGroupBox = QGroupBox("Data")
        self.sourceGroupBox.setLayout(dataLayout)

        #>>>>>>>>>>>>>>meta box<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        self.metaGroupBox = QGroupBox("messages")
        meta_Layout = QGridLayout()
        self.num_msg_label = QLabel()
        self.num_msg_label.setText("no messages")
        meta_Layout.addWidget(self.num_msg_label)
        self.metaGroupBox.setLayout(meta_Layout)



        # >>>>>>>>>>>>>>>>>>>>>combobox filter <<<<<<<<<<<<<<<<<<
        self.filterGroupBox_1 = QGroupBox("Filter by domain")
        self.filterDomainComboBox = QComboBox()
        self.filterDomainLabel = QLabel("Filter &domain:")
        self.filterDomainLabel.setBuddy(self.filterDomainComboBox)
        self.filterMsgComboBox = QComboBox()
        self.filterMsgLabel = QLabel("Filter &Msg:")
        self.filterMsgLabel.setBuddy(self.filterDomainComboBox)

        filterLayout_1 = QGridLayout()
        filterLayout_1.addWidget(self.filterDomainLabel, 0, 0, 1,1)
        filterLayout_1.addWidget(self.filterDomainComboBox, 0, 1, 1, 10)
        filterLayout_1.addWidget(self.filterMsgLabel,1,0,2,1)
        filterLayout_1.addWidget(self.filterMsgComboBox, 1, 1,1,10)
        self.filterGroupBox_1.setLayout(filterLayout_1)


        #>>>>>>>>>>>>>>>>>>>>>>>.open text filter <<<<<<<<<<<<<<<<<<<<<,
        self.filterGroupBox_2 = QGroupBox("Filter by text")
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

        #>>>>>>>>>>>>>>> time filter  <<<<<<<<<<<<<<<<<<<<<<<<<<
        time_filter_layout = QGridLayout()
        self.from_date_label= QLabel("from date")
        self.from_date_line_edit = QLineEdit("2019-05-04")
        self.from_hour_label = QLabel("from hour")
        self.from_hour_line_edit = QLineEdit("12:39:48")
        self.to_date_label = QLabel("to date")
        self.to_date_line_edit = QLineEdit("2019-05-04")
        self.to_hour_label = QLabel("to hour")
        self.to_hour_line_edit = QLineEdit("12:40:20")
        self.time_filter_button = QPushButton("Find")

        time_filter_layout.addWidget(self.from_date_label, 0,0)
        time_filter_layout.addWidget(self.from_date_line_edit, 0,1)
        time_filter_layout.addWidget(self.from_hour_label, 0,2)
        time_filter_layout.addWidget(self.from_hour_line_edit, 0,3)
        time_filter_layout.addWidget(self.to_date_label, 0, 4)
        time_filter_layout.addWidget(self.to_date_line_edit, 0, 5)
        time_filter_layout.addWidget(self.to_hour_label, 0, 6)
        time_filter_layout.addWidget(self.to_hour_line_edit, 0, 7)
        time_filter_layout.addWidget(self.time_filter_button , 0, 8)

        self.time_filter_groupBox = QGroupBox("Filter by time")
        self.time_filter_groupBox.setLayout(time_filter_layout)

        #>>>>>>>>>>>> function connect <<<<<<<<<<<<<<<<<<<<<<<,,
        self.filterDomainComboBox.currentIndexChanged.connect(self.domainComboChange)
        self.filterMsgComboBox.currentIndexChanged.connect(self.msgComboChange)
        self.fetch_up_button.clicked.connect(self.fetchMoreClicked)
        self.fetch_down_button.clicked.connect(self.fetchLessClicked)
        self.filterPatternButton.clicked.connect(self.openTextFeatchMsg)
        self.num_row_to_show_combbox.currentIndexChanged.connect(self.numLineComboChange)
        self.time_filter_button.clicked.connect(self.timeFilterButtonPushed)
        self.jump_to_msg_button.clicked.connect(self.jumpToMsg)
        # parent layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sourceGroupBox,1)
        mainLayout.addWidget(self.metaGroupBox)
        mainLayout.addWidget(self.filterGroupBox_1)
        mainLayout.addWidget(self.filterGroupBox_2)
        mainLayout.addWidget(self.time_filter_groupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("log message parser")

    def initDomainCombo(self):
        self.filterDomainComboBox.clear()
        self.filterDomainComboBox.addItem('ALL')
        self.filterDomainComboBox.addItems(self.dc.getInitData())


    def domainComboChange(self):
        if self.filterDomainComboBox.currentText() == '':
            return
        self.dc.setModelSize(int(self.num_row_to_show_combbox.currentText()))
        if self.filterDomainComboBox.currentText() == 'ALL':
            self.curr_model = self.dc.fetchAllMsg()
            self.filterMsgComboBox.clear()
        else:
            domain = self.filterDomainComboBox.currentText()
            self.curr_model= self.dc.fetchDatabyDomain(domain)
            self.filterMsgComboBox.clear()
            self.filterMsgComboBox.addItem("ALL")
            msg_by_domain = self.dc.getMsgListByDomain(self.filterDomainComboBox.currentIndex() - 1)
            self.filterMsgComboBox.addItems(msg_by_domain)

        num_rows = self.dc.countRows()
        rows_showed =min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed, num_rows))
        self.curr_view_state = 'domain'
        self.msg_view.setModel(self.curr_model)

    def msgComboChange(self):
        msg_type = self.filterMsgComboBox.currentText()
        if msg_type == 'ALL' or not msg_type:
            return
        self.dc.setModelSize(int(self.num_row_to_show_combbox.currentText()))
        self.curr_model = self.dc.fetchDataByMsg(msg_type)
        num_rows = self.dc.countRows()
        rows_showed = min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed , num_rows))
        self.msg_view.setModel(self.curr_model)
        self.curr_view_state = 'msg'
        
        


    def fetchMoreClicked(self):
        self.curr_model = self.dc.fetchMore(self.filterDomainComboBox.currentText())
        num_rows = self.dc.countRows()
        rows_showed = min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed, num_rows))
        self.msg_view.setModel(self.curr_model)


    def fetchLessClicked(self):
        self.curr_model = self.dc.fetchLess()
        num_rows = self.dc.countRows()
        rows_showed = min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed, num_rows))
        self.msg_view.setModel(self.curr_model)

    def openTextFeatchMsg(self):
        x= re.split(r',\s*(?![^()]*\))', self.filterPatternLineEdit.text())
        list = {}
        for i in x:
            list[i[:i.find("(")]] = (i[i.find("(")+1:i.find(")")].split(', '))
        self.curr_model = self.dc.fetchOpenText(list)

        num_rows = self.dc.countRows()
        rows_showed =  min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed , num_rows))
        self.msg_view.setModel(self.curr_model)
        self.curr_view_state = 'domain'

    def numLineComboChange(self):
        if self.curr_view_state == 'domain':
            self.domainComboChange()
        elif self.curr_view_state == 'msg':
            self.msgComboChange()

        self.dc.setModelSize(int(self.num_row_to_show_combbox.currentText()))

    def timeFilterButtonPushed(self):
        from_d = self.from_date_line_edit.text()
        from_h = self.from_hour_line_edit.text()
        to_d = self.to_date_line_edit.text()
        to_h = self.to_hour_line_edit.text()
        domain = self.filterDomainComboBox.currentText()
        msg = self.filterMsgComboBox.currentText()
        try:
            datetime.datetime.strptime(from_d, "%Y-%m-%d")
            datetime.datetime.strptime(to_d, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        try:
            datetime.datetime.strptime(from_h, "%H:%M:%S")
            datetime.datetime.strptime(to_h, "%H:%M:%S")
        except ValueError:
            raise ValueError("Incorrect data format, should be HH:MM:SS")

        self.curr_model = self.dc.fetchBetweenDate(domain,msg,from_d,from_h ,to_d, to_h)
        num_rows = self.dc.countRows()
        rows_showed =  min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed , num_rows))
        self.msg_view.setModel(self.curr_model)
        self.curr_view_state = 'domain'

    def jumpToMsg(self):
        self.curr_model = self.dc.fetchJumpToMsg(self.jump_to_msg_lineEdit.text())
        self.filterMsgComboBox.clear()
        num_rows = self.dc.countRows()
        rows_showed = min(self.dc.dataShowedSoFar(), num_rows)
        self.num_msg_label.setText("{} from {} messages".format(rows_showed, num_rows))
        self.curr_view_state = 'domain'
        self.msg_view.setModel(self.curr_model)

    def CW_exportToFile(self, path):
        self.dc.DC_exportToFile(path)
