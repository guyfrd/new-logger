from PySide2.QtGui import QStandardItemModel
from PySide2.QtCore import Qt


class dataList:
    def __init__(self, data, block_size, model_meta):
        print("new_data_list")
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

        if self.curr_end >=  len(self.data):
            print("no more to fetch curr_end {} len {}".format(self.curr_end,len(self.data)))
            return self.model_list[self.curr_index]

        elif self.curr_index == 0 and len(self.model_list) == 0:
            print("min :{}".format(min(self.block_size, len(self.data))))
            num_data = min(self.block_size, len(self.data))
            model = self.createModel(0, num_data)
            self.model_list.append(model)
            self.curr_start = 0
            self.curr_end = num_data
        elif self.curr_index == len(self.model_list) -1:
            num_data = min(self.curr_end + self.block_size, len(self.data))
            self.curr_start = self.curr_end
            self.curr_end = num_data
            model = self.createModel(self.curr_start , num_data)
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
            if not self.model_list[self.curr_index]:
                self.curr_end = self.curr_start
                self.curr_start -= self.block_size
                self.model_list[self.curr_index] = self.createModel(self.curr_start, self.curr_end)
                return self.model_list[self.curr_index]
            model = self.model_list[self.curr_index]
            self.curr_end = self.curr_start
            self.curr_start -= self.block_size

        return model

    def createModel(self, start, end):
        print("createModel start {} end: {} num-col:{}".format(start, end, self.model_col_num))

        model = QStandardItemModel(min(self.block_size, len(self.data) - self.curr_start),  len(self.model_meta_data) - 1)
        step = 1 if start < end else -1

        for i in range(1, self.model_col_num):
            model.setHeaderData(i - 1, Qt.Horizontal, self.model_meta_data[i][0])
        i = 0
        for row in range(start, end, step):
            data = self.data[row]
            #print("build model index {}, data: {}".format(row, data))
            for col in range(0, self.model_col_num - 1):
                model.setData(model.index(i, col), str(data[col + 1]))
            i += 1
        return model

    def getDataShowd(self):
        return self.curr_end

    def jumpToMsg(self, msg_num):
        if int(msg_num) > len(self.data):
            return

        block_num = int(msg_num) // self.block_size
        self.curr_index = block_num
        self.model_list = [None] * (block_num)
        self.curr_start = block_num * self.block_size
        self.curr_end = min(self.curr_start + self.block_size , len(self.data))
        model = self.createModel(self.curr_start, self.curr_end)
        self.model_list.append(model)
        print(self.model_list)

        return model