from PySide2.QtGui import QStandardItemModel
from PySide2.QtCore import Qt


class dataList:
    def __init__(self, data, block_size, model_meta):
        self.data = data
        self.block_size = block_size
        self.model_list = []
        self.curr_index = 0
        self.model_meta_data = model_meta
        self.model_col_num = len(model_meta)
        self.curr_start = 0
        self.curr_end = 0
    def __iter__(self):
        return self

    def __next__(self):
        print("next curr_index:{}".format(self.curr_index))

        if self.curr_index == 0 and len(self.model_list) == 0:

            model = self.createModel(0, min(self.block_size, len(self.data)))
            self.model_list.append(model)
            self.curr_start = 0
            self.curr_end = self.block_size
            #self.curr_index += 1
        elif self.curr_index == len(self.model_list) -1:
            self.curr_start = self.curr_end
            self.curr_end += self.block_size
            model = self.createModel(self.curr_start , self.curr_end)
            self.curr_index += 1
            self.model_list.append(model)
        elif self.curr_index < len(self.model_list):
            self.curr_index += 1
            self.curr_start = self.curr_end
            self.curr_end += self.block_size
            model = self.model_list[self.curr_index]

        return model

    def prev(self):
        print("prev curr_index: {}".format(self.curr_index))
        if self.curr_index == 0:
            model = self.model_list[0]
            self.curr_end = self.block_size
            self.curr_start = 0

        else:
            self.curr_index -= 1
            model = self.model_list[self.curr_index]
            self.curr_end = self.curr_start
            self.curr_start -= self.block_size

        return model

    def createModel(self, start, end):
        print("createModel start {} end: {} num-col:{}".format(start, end, self.model_col_num))
        model = QStandardItemModel(self.block_size,  len(self.model_meta_data) - 1)
        step = 1 if start < end else -1

        for i in range(1, self.model_col_num):
            model.setHeaderData(i - 1, Qt.Horizontal, self.model_meta_data[i][0])

        i = 0
        for row in range(start, end, step):
            data = self.data[row]
            for col in range(0, self.model_col_num - 1):
               # print("build model index {},{}, data: {}".format(row,col, data))
                model.setData(model.index(i, col), str(data[col + 1]))
            i += 1
        return model

    def getDataShowd(self):
        return self.curr_end