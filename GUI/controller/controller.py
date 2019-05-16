from binParser.logParseLib import parseLib
from time import gmtime, strftime
from itertools import cycle
from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtGui import QStandardItemModel
from PySide2.QtCore import Qt, QSortFilterProxyModel
import cProfile


class dataController:
    def __init__(self):

        self.curr_data = []
        self.domain_list = []
        self.cycle_list = None
        self.model_cache = []
        self.curr_index_model_cache = 0
        self.date_left_to_show = 0
        self.date_show_so_far = 0
        self.model_size = 100

    def initBinFile(self,file_path,json_path):
        self.parser_lib = parseLib(file_path,json_path, None)
        self.domain_list = self.parser_lib.getDomainList()
        self.msg_list = self.parser_lib.getMsgList()


    def initDB(self,db_path):

        self.parser_lib = parseLib(None, None, db_path)
        self.domain_list = self.parser_lib.getDomainList()
        self.msg_list = self.parser_lib.getMsgList()

    def getInitData(self):
        return self.domain_list


    def createModel(self, table):
        print("createModel")
        self.curr_data_size = len(self.curr_data)
        data_to_fetch = min(self.date_left_to_show , self.model_size)
        table_data = self.parser_lib.getTableData()

        model = QStandardItemModel(data_to_fetch, len(table_data) - 1)
        print("+++++{}".format(model.rowCount()))
        for i in range(1, len(table_data)):
            model.setHeaderData(i -1 , Qt.Horizontal, table_data[i][0])

        for row in range(data_to_fetch):
            data = next(self.cycle_list)
            for col in range(0, len(table_data)-1):
                model.setData(model.index(row, col), str(data[col+1]))

        self.date_left_to_show -= data_to_fetch
        self.date_show_so_far += data_to_fetch
        self.curr_model_num_display += 1
        self.model_cache.append(model)
        return model

    def fetchAllMsg(self):
        print("getAllMsg")
        self.curr_data = self.parser_lib.queryMsgAll(self.model_size)
        num_msg = len(self.curr_data)
        print(num_msg)
        self.date_left_to_show = num_msg
        self.cycle_list = cycle(self.curr_data)

        self.date_show_so_far = 0
        self.curr_model_num_display = 0
        self.model_cache = []

        self.curr_data_size = len(self.curr_data)
        model = self.createModel('messages')

        return model

    # def fetchMoreAllMsg(self):
    #
    #     if self.curr_model_num_display == len(self.model_cache):
    #         self.curr_data = self.parser_lib.fetchManyAllTable(self.model_size)
    #         self.cycle_list = cycle(self.curr_data)
    #         model = self.createModel('messages')
    #     else:
    #         model = self.model_cache[self.curr_model_num_display]
    #         self.curr_model_num_display +=1
    #
    #     print("---------------------------------")
    #     print("fetchMoreAllMsg\ncurr_model_num_display {} model_cache_num {}".format(self.curr_model_num_display, len(self.model_cache)))
    #
    #     return model


    def getMsgListByDomain(self,domain_index):
        return self.msg_list[domain_index]


    def fetchDataByMsg(self,msg):
        self.curr_data = self.parser_lib.queryMsgByType(msg)
        self.cycle_list = cycle(self.curr_data)
        num_msg = len(self.curr_data)
        self.date_left_to_show = num_msg
        print(num_msg)
        print("getDataByMsg {} len {}".format(msg, len(self.curr_data)))

        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel(msg)
        self.date_show_so_far = 0

        return model

    def fetchOpenText(self, list):
        print("fetchOpenText {}".format(list))
        self.curr_data = self.parser_lib.getMsgMulti(list)
        self.cycle_list = cycle(self.curr_data)

        self.date_show_so_far = 0
        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel('messages')

        return model


    def fetchDatabyDomain(self, domain):
        print('controller- getDataByDomain')
        self.curr_data = self.parser_lib.queryMsgByDomain(domain)
        self.cycle_list = cycle(self.curr_data)
        num_msg = len(self.curr_data)
        self.date_left_to_show = num_msg

        self.date_show_so_far = 0
        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel('messages')

        return model

    def fetchBetweenDate(self, domain, msg, from_d, from_h, to_d, to_h):

        self.curr_data = self.parser_lib.queryDate(domain, from_d, from_h, to_d, to_h)
        self.cycle_list = cycle(self.curr_data)
        self.date_left_to_show = len(self.curr_data)

        print("getDataByMsg {} len {}".format(msg, len(self.curr_data)))
        self.date_show_so_far = 0
        self.curr_model_num_display = 0
        self.model_cache = []

        model = self.createModel(msg)

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
            self.curr_model_num_display -= 1
            model = self.model_cache[self.curr_model_num_display-1]
            self.date_show_so_far -= model.rowCount()

        print("---------------------------------")
        print("fetchLess\ncurr_model_num_display {} model_cache_num {}".format(self.curr_model_num_display, len(self.model_cache)))
        return model

    def numDomain(self, domain):
        if domain =='ALL':
            num = self.parser_lib.countAll()
        else:
            num = self.parser_lib.countAllDomain(domain)
        return num

    def numMsg(self, msg):
        return self.parser_lib.countMsg(msg)


    def setModelSize(self, size):
        self.model_size = size


    def dataShowedSoFar(self):
        return self.date_show_so_far
    def countRows(self):
        return len(self.curr_data)