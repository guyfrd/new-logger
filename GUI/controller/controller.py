from binParser.logParseLib import parseLib

from GUI.controller.dataList import dataList

class dataController:
    def __init__(self):

        self.curr_data = []
        self.domain_list = []
        self.data_list = None
        self.parser_lib = None

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


    def fetchJumpToMsg(self, msg_num):
        self.curr_data = self.parser_lib.queryMsgAll(self.model_size)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data, self.model_size, col_num)
        model = self.data_list.jumpToMsg(msg_num)
        return model



    def getMsgListByDomain(self,domain_index):
        return self.msg_list[domain_index]


    def fetchAllMsg(self):
        self.curr_data = self.parser_lib.queryMsgAll(self.model_size)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data,self.model_size, col_num)
        model = next(self.data_list)
        return model

    def fetchDataByMsg(self,msg):
        self.curr_data = self.parser_lib.queryMsgByType(msg)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data, self.model_size, col_num)
        model = next(self.data_list)
        return model

    def fetchOpenText(self, list):
        self.curr_data = self.parser_lib.getMsgMulti(list)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data, self.model_size, col_num)
        model = next(self.data_list)
        return model


    def fetchDatabyDomain(self, domain):
        self.curr_data = self.parser_lib.queryMsgByDomain(domain)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data, self.model_size, col_num)
        model = next(self.data_list)
        return model

    def fetchBetweenDate(self, domain, msg, from_d, from_h, to_d, to_h):
        self.curr_data = self.parser_lib.queryDate(domain, from_d, from_h, to_d, to_h)
        col_num = self.parser_lib.getTableData()
        self.data_list = dataList(self.curr_data, self.model_size, col_num)
        model = next(self.data_list)
        return model


    def fetchMore(self,  msg ='ALL'):
        return next(self.data_list)


    def fetchLess(self):
        return self.data_list.prev()

    def dataShowedSoFar(self):
        return self.data_list.getDataShowd()







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

    def countRows(self):
        return len(self.curr_data)