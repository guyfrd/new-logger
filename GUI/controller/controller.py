from binParser.logParseLib import parseLib
from time import gmtime, strftime
from itertools import cycle
from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtGui import QStandardItemModel
from PySide2.QtCore import Qt, QSortFilterProxyModel



class dataController:
    def __init__(self):

        self.curr_data = []
        self.domain_list = []
        self.cycle_list = None
        self.model_cache = []
        self.curr_index_model_cache = 0
        self.curr_index_in_data = 0

    def initBinFile(self,file_path):
        print("initBinFile {}".format(file_path))
        self.parser_lib = parseLib(file_path,
                                   '/home/osboxes/log/new-log/files/icon_common.json',
                                   None)
        self.domain_list = self.parser_lib.getDomainList()
        self.msg_list = self.parser_lib.getMsgList()
        # print('get msg list {}'.format(self.msg_list))


    def initDB(self,db_path):
        print("initDB {}".format(db_path))
        self.parser_lib = parseLib('/home/osboxes/log/new-log/files/icon_log_emmc_full2',
                                   '/home/osboxes/log/new-log/files/icon_common.json',
                                   db_path)
        self.domain_list = self.parser_lib.getDomainList()
        self.msg_list = self.parser_lib.getMsgList()

    def getInitData(self):
        print("getInitData")
        return self.domain_list


    def createModel(self, table):
        self.curr_data_size = len(self.curr_data)
        data_to_fetch = min(self.curr_data_size, 100)
        table_data = self.parser_lib.getTableData('messages')

        model = QStandardItemModel(data_to_fetch, len(table_data) - 1)
        for i in range(1, len(table_data)):
            model.setHeaderData(i -1 , Qt.Horizontal, table_data[i][0])

        for row in range(data_to_fetch):
            data = next(self.cycle_list)
            for col in range(0, len(table_data)-1):
                model.setData(model.index(row, col), str(data[col+1]))

        self.curr_index_in_data += data_to_fetch

        self.curr_model_num_display += 1
        self.model_cache.append(model)
        return model

    def getAllMsg(self):
        print("getAllMsg")
        self.curr_data = self.parser_lib.queryMsgAll(100)

        self.cycle_list = cycle(self.curr_data)

        self.curr_model_num_display = 0
        self.model_cache = []

        self.curr_data_size = len(self.curr_data)
        model = self.createModel('messages')

        return model

    def fetchMoreAllMsg(self):

        if self.curr_model_num_display == len(self.model_cache):
            self.curr_data = self.parser_lib.fetchManyAllTable(100)
            self.cycle_list = cycle(self.curr_data)
            model = self.createModel('messages')
        else:
            model = self.model_cache[self.curr_model_num_display]
            self.curr_model_num_display +=1

        print("---------------------------------")
        print("fetchMoreAllMsg\ncurr_model_num_display {} model_cache_num {}".format(self.curr_model_num_display, len(self.model_cache)))

        return model


    def getMsgListByDomain(self,domain_index):
        return self.msg_list[domain_index]


    def getDataByMsg(self,msg):

        self.curr_data = self.parser_lib.queryMsgByType(msg)
        self.cycle_list = cycle(self.curr_data)
        print("getDataByMsg {} len {}".format(msg, len(self.curr_data)))

        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel(msg)

        return model

    def fetchOpenText(self, list):
        print("fetchOpenText {}".format(list))
        self.curr_data = self.parser_lib.getMsgMulti(list)
        self.cycle_list = cycle(self.curr_data)

        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel('messages')

        return model


    def getDatabyDomain(self, domain):

        self.curr_data = self.parser_lib.queryMsgByDomain(domain)
        self.cycle_list = cycle(self.curr_data)

        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel('messages')

        return model


    def fetchMore(self, table):

        if self.curr_model_num_display == len(self.model_cache):
            model = self.createModel(table)
        else:
            model = self.model_cache[self.curr_model_num_display]
            self.curr_model_num_display +=1


        print("---------------------------------")
        print("fetchMore\ncurr_model_num_display {} model_cache_num {}".format(self.curr_model_num_display, len(self.model_cache)))

        return model



    def fetchLess(self):

        if self.curr_model_num_display == 1:
            model = self.model_cache[0]
        else:
            self.curr_model_num_display  -= 1
            model = self.model_cache[self.curr_model_num_display-1]

        print("---------------------------------")
        print("fetchLess\ncurr_model_num_display {} model_cache_num {}".format(self.curr_model_num_display, len(self.model_cache)))
        return model



