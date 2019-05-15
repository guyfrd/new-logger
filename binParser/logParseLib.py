import json
import os
import struct
from collections import OrderedDict
import sqlite3
from time import gmtime, strftime
import ntpath

struct_format_dict = {
    'uint8' : 'B', #one byte unsigned
    'int8' : 'b', #one byte signed
    'uint16': 'H', #two byte
    'int16' : 'h',
    'uint32' : 'i', #four byte
    'float' : 'f',
    'char[15#]' : '15p'
}

type_to_field_dict = {
    'uint8' : 'INTEGER', #one byte unsigned
    'int8' : 'INTEGER', #one byte signed
    'uint16': 'INTEGER', #two byte
    'int16' : 'INTEGER',
    'uint32' : 'INTEGER', #four byte
    'float' : 'REAL',
    'char[15#]' : 'TEXT'
}



class parseLib:
    def __init__(self, bin_file, json_file, db_path):
        json_f = open(json_file, "r")
        json_text = json_f.read()
        self.json_data = json.loads(json_text, object_pairs_hook=OrderedDict)
        self.meta_domain = []
        self.domain = []
        self.msg_type_name = []
        self.msg_type_struct = []

        self.compile_msg_struct = []
        self.meta_domain_dic = {}

        json_f.close()

        if db_path:
            print(db_path)
            self.db = sqlite3.connect(db_path, uri=True)
            self.cur = self.db.cursor()
            self.build_helper_lists(db_path)
        else:
            print("no db open {}".format(bin_file))
            bin_f = open(bin_file,"rb")
            self.bin_data = bin_f.read()
            self.curr_byte = 0
            self.file_size = os.path.getsize(bin_file)
            head, tail = ntpath.split(bin_file)

            tail += '.db'
            new_db_path = '../../files/' + tail
            print("open db {}".format(new_db_path))
            self.db = sqlite3.connect(new_db_path, uri=True)
            self.cur = self.db.cursor()
            self.build_helper_lists(None)
            self.initDb()
            self.parse()


            bin_f.close()
            self.db.commit()


    def build_helper_lists(self,db_path):
        for meta_domain_key in self.json_data.keys():
            self.meta_domain.append(meta_domain_key)

        for meta_domain_key in self.json_data.keys():
            for domain_key in self.json_data[meta_domain_key].keys():
                #self.cur.execute("INSERT INTO domain(domain_text) VALUES (?)", (domain_key,))
                self.domain.append(domain_key)
                self.meta_domain_dic[domain_key] = meta_domain_key


        for meta_domain_key in self.json_data.keys():
            for domain_key in self.json_data[meta_domain_key].keys():
                msg_struct_name_tmp= []
                msg_struct_tmp= []
                msg_compile_struct_tmp = []
                for msg_type_key in self.json_data[meta_domain_key][domain_key].keys():
                    msg_struct_name_tmp.append(msg_type_key)
                    msg_struct_tmp.append(self.json_data[meta_domain_key][domain_key][msg_type_key])
                    msg_compile_struct = self.createCompileMsgStruct(self.json_data[meta_domain_key][domain_key][msg_type_key])
                    msg_compile_struct_tmp.append(msg_compile_struct)

                    if not db_path:
                        self.creteMsgTable(msg_type_key, self.json_data[meta_domain_key][domain_key][msg_type_key])

                self.compile_msg_struct.append(msg_compile_struct_tmp)
                self.msg_type_struct.append(msg_struct_tmp)
                self.msg_type_name.append(msg_struct_name_tmp)






    def parse(self):

        time_format = '=HL'
        time_struct = struct.Struct(time_format)
        curr_msg_id = 0

        while self.curr_byte  < self.file_size:

            if self.curr_byte + 8 > self.file_size:
                break

            unpack = time_struct.unpack_from(self.bin_data, self.curr_byte )
            self.curr_byte += 6

            time_str = "{}.{}".format(str(unpack[1]), str(unpack[0]))

            curr_date = strftime("%Y-%m-%d",gmtime(float(time_str)))
            curr_hour = strftime("%H:%M:%S",gmtime(float(time_str)))

            curr_domain = self.bin_data[self.curr_byte ]
            self.curr_byte += 1
            curr_msg = self.bin_data[self.curr_byte]
            self.curr_byte += 1
            curr_msg_id += 1
            curr_domain_string = self.domain[curr_domain]
            curr_meta_string = self.meta_domain_dic[curr_domain_string]
            curr_msg_name = self.msg_type_name[curr_domain][curr_msg]
            curr_msg_struct = self.msg_type_struct[curr_domain][curr_msg]
            # print("-----------------------------------------------------")
            # print("curr_meta_string:{} curr_domain_string {}\ncurr_msg_name: {} curr_msg_struct: {}\ncurr_date: {}  curr_hour: {} curr_byte: {}"
            #       .format(curr_meta_string,curr_domain_string , curr_msg_name, curr_msg_struct , curr_date, curr_hour, self.curr_byte))

            insert_str= ''
            if 'null' in curr_msg_struct and 'void' in curr_msg_struct.values():
                insert_str = self.createInsertExp(curr_msg_id, curr_date, curr_hour,'null', curr_msg_name , None)
                #print(insert_str)
                self.cur.execute(insert_str)
                self.cur.execute("""INSERT INTO messages(msg_id, date, hour, domain ,msg_type, payload)
                                    VALUES (?, ?, ?, ?, ?, ? )""",
                                    (curr_msg_id, curr_date,curr_hour, curr_domain_string ,curr_msg_name, ''))

            elif 'char*' in curr_msg_struct .values():
                decode_msg = self.readFlexMsg().rstrip('\x00')
                # print("decode msg: {}".format(decode_msg))
                insert_str = self.createInsertExp(curr_msg_id,curr_date, curr_hour,'flex', curr_msg_name, decode_msg)
                # print("insert_str: {}".format(insert_str))
                self.cur.execute(insert_str)
                self.cur.execute("""INSERT INTO messages(msg_id, date, hour, domain, msg_type, payload)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (curr_msg_id , curr_date, curr_hour, curr_domain_string ,curr_msg_name, decode_msg))

            else:
                msg = self.readMsgStruct(curr_domain,curr_msg)
                # print("msg: {}".format(msg))
                insert_str = self.createInsertExp(curr_msg_id,curr_date, curr_hour,'struct', curr_msg_name,msg)
                # print("insert_str: {}".format(insert_str))
                self.cur.execute(insert_str)
                self.cur.execute("""INSERT INTO messages(msg_id,date, hour, domain, msg_type, payload)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (curr_msg_id, curr_date, curr_hour, curr_domain_string ,curr_msg_name, str(msg)))

        self.db.commit()

    def createInsertExp(self,msg_id, date, hour ,msg_type, msg_name ,msg):
        insert_str = "INSERT INTO {} VALUES ({}, {}, \'{}\', \'{}\'".format(msg_name, 'null', msg_id, date, hour)
        if msg_type == 'struct':
            for i in msg:
                insert_str += ', '
                insert_str += str(msg[i])
        elif msg_type == 'flex':
            insert_str += ', '
            insert_str += str(len(msg))
            insert_str += ', '
            insert_str += '\'{}\''.format(msg)

        insert_str += ")"

        return insert_str


    def readFlexMsg(self):
        flex_size = self.bin_data[self.curr_byte]
        self.curr_byte += 1

        if self.curr_byte + flex_size > self.file_size:
            return

        msg_byte_arr = bytearray()
        for i in range(flex_size):
            msg_byte_arr.append(self.bin_data[self.curr_byte])
            self.curr_byte += 1
        decode_msg = msg_byte_arr.decode()
        return decode_msg

    def readMsgStruct(self, domain, msg_type):
        # build format string for the struct

        msg_struct = self.compile_msg_struct[domain][msg_type]
        # print(msg_struct )
        unpack = msg_struct.unpack_from(self.bin_data, self.curr_byte)
        size = msg_struct.size
        # print("struct size: {}".format(size))
        self.curr_byte += msg_struct.size
        # print("format: {} unpack:{}".format(format, unpack))

        # convert from bytestring to string
        unpack_list = []
        for i in unpack:
            if type(i) is bytes:
                bytes_without_null = i.partition(b'\0')[0]
                unpack_list.append(bytes_without_null.decode("utf-8").strip())
            else:
                unpack_list.append(i)

        msg_with_value = {}
        index = 0
        # print(unpack)
        for i in self.msg_type_struct[domain][msg_type]:
            msg_with_value[i] = unpack_list[index]
            index += 1

        return msg_with_value

    def creteMsgTable(self, msg_type, msg):
        drop_str = "DROP TABLE IF EXISTS " + msg_type

        create_table_str = """CREATE TABLE IF NOT EXISTS {}(
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   msg_id INTEGER,
                                   date TEXT,
                                   hour TEXT""".format(msg_type)
        for i in msg:
            if msg[i] == 'void':
                break
            elif msg[i] == 'char*':
                create_table_str += ", value TEXT"
            else:
                create_table_str += ", {} {}".format(i, type_to_field_dict[msg[i]])

        create_table_str += ")"
        print(create_table_str)
        self.cur.execute(drop_str)
        self.cur.execute(create_table_str)
        self.db.commit()


    def initDb(self):

        self.cur.execute("DROP TABLE IF EXISTS domain")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS domain(
                     domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     domain_text text
                     )""")

        self.cur.execute("DROP TABLE IF EXISTS sub_domain")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS msg_type(
                         domain_id int,
                         msg_type_id integer,
                         msg_type_text text,
                         PRIMARY KEY (domain_id, msg_type_id)
                         FOREIGN KEY (domain_id) REFERENCES domain(domain_id)
                         )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS messages(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            msg_id INTEGER,
                            date text,
                            hour text,
                            domain text,
                            msg_type text,
                            payload text
                            )""")

        self.db.commit()




    def createCompileMsgStruct(self, msg):

        format = '='  # for packed

        for i in msg:
            if msg[i] == 'void' or msg[i] == 'char*':
                return

            format += struct_format_dict[msg[i]]
        format_size = struct.calcsize(format)
        # print("msg: {} format size : {}".format(msg, format_size))

        s = struct.Struct(format)
        return s

    def queryMsgByDomain(self, domain):
        self.cur.execute("SELECT * FROM messages WHERE domain=?", (domain,))
        return  self.cur.fetchall()

    def queryMsgByType(self, msg_type):
        print('queryMsgByType')
        self.cur.execute("SELECT * FROM {}".format(msg_type))
        return self.cur.fetchall()

    def queryMsgAll(self, arr_size):
        self.cur.execute("SELECT * FROM messages")
        print("queryMsgAll {}".format(self.cur))
        return self.cur.fetchmany(arr_size)

    def fetchManyAllTable(self, arr_size):
        print("fetchManyAllTable")

        data = self.cur.fetchmany(arr_size)
        return data

    def getAllMsgTableSize(self):
        return self.cur.rowcount

    def getDomainList(self):
        return self.domain

    def getMsgList(self):
        return self.msg_type_name

    def getTableData(self,msg_type):
        print("getTableData")
        #self.cur.execute("SELECT * FROM {}".format(msg_type))
        return self.cur.description

    def getMsgMulti(self, msg_list):
        select_str = "SELECT * FROM messages WHERE "
        print("createSelectExp")
        temp =[]
        if msg_list:
            for domain_key in msg_list:
                for msg_type in msg_list[domain_key]:
                    if msg_type != '':
                        temp.append( 'domain=\'{}\' AND msg_type=\'{}\' '.format(domain_key,msg_type))
                    else:
                        temp.append('domain=\'{}\'  '.format(domain_key))

        select_str += temp[0]
        for i in range(1 , len(temp)):
            select_str+= 'OR '
            select_str+= temp[i]

        print(temp)
        print(select_str)

        self.cur.execute(select_str)
        return self.cur.fetchall()