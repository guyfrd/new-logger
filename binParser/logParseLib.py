import json
import sys
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
    'char[15#]' : '15p',
    'bool': '?'
}

type_to_field_dict = {
    'uint8' : 'INTEGER', #one byte unsigned
    'int8' : 'INTEGER', #one byte signed
    'uint16': 'INTEGER', #two byte
    'int16' : 'INTEGER',
    'uint32' : 'INTEGER', #four byte
    'float' : 'REAL',
    'char[15#]' : 'TEXT',
    'bool' : 'TEXT'
}

log_file = None
if len(sys.argv) > 1 and sys.argv[1] == 'log':
    log_file = open('files/log', "w")
    log_file.write(strftime("%a, %d %b %Y %H:%M:%S\n", gmtime()))
    log_file.flush()

class parseLib:
    def __init__(self, bin_file, json_file, db_path):
        self.meta_domain = []
        self.domain = []
        self.msg_type_name = []
        self.msg_type_struct = []

        self.compile_msg_struct = []
        self.meta_domain_dic = {}


        if db_path:
            self.db = sqlite3.connect(db_path, uri=True)
            self.cur = self.db.cursor()
            self.retriveJSONfromDB()
        else:
            json_f = open(json_file, "r")
            json_text = json_f.read()
            self.json_data = json.loads(json_text, object_pairs_hook=OrderedDict)
            json_f.close()
            bin_f = open(bin_file,"rb")
            self.bin_data = bin_f.read()
            self.curr_byte = 0
            self.file_size = os.path.getsize(bin_file)
            head, tail = ntpath.split(bin_file)

            tail += '.db'

            new_db_path =''
            if getattr(sys, 'frozen', False):
                new_db_path = os.path.join(sys._MEIPASS, 'files', tail)
            else:
                new_db_path = os.path.join(sys.path[0], 'files', tail)

            self.db = sqlite3.connect(new_db_path, uri=True)
            self.cur = self.db.cursor()
            self.initDb()
            self.build_helper_lists(None)
            self.parse()

            bin_f.close()
            self.db.commit()


    def build_helper_lists(self,db_path):
        for meta_domain_key in self.json_data.keys():
            self.cur.execute("INSERT INTO meta_domain(meta_domain_text) VALUES(\'{}\')".format(meta_domain_key))
            self.meta_domain.append(meta_domain_key)
            for domain_key in self.json_data[meta_domain_key].keys():
                self.cur.execute("INSERT INTO domain(domain_text, meta_domain) VALUES(\'{}\',\'{}\')".format(domain_key,meta_domain_key))
                self.domain.append(domain_key)
                self.meta_domain_dic[domain_key] = meta_domain_key
                msg_struct_name_tmp = []
                msg_struct_tmp = []
                msg_compile_struct_tmp = []
                for msg_type_key in self.json_data[meta_domain_key][domain_key].keys():
                    msg_type_struct = self.json_data[meta_domain_key][domain_key][msg_type_key]
                    msg_struct_name_tmp.append(msg_type_key)
                    msg_struct_tmp.append(msg_type_struct)
                    str = "INSERT INTO msg_type(msg_type_name,msg_type_struct,domain) VALUES(\'{}\',\"{}\",\'{}\')".format(msg_type_key,msg_type_struct, domain_key)
                    self.cur.execute(str)
                    #------------------------------------------------------
                    msg_compile_struct = self.createCompileMsgStruct(msg_type_struct)
                    msg_compile_struct_tmp.append(msg_compile_struct)
                    #------------------------------------------------------

                    if not db_path:
                        self.creteMsgTable(msg_type_key, msg_type_struct)

                self.compile_msg_struct.append(msg_compile_struct_tmp)
                self.msg_type_struct.append(msg_struct_tmp)
                self.msg_type_name.append(msg_struct_name_tmp)



    def retriveJSONfromDB(self):
        self.cur.execute("SELECT meta_domain_text FROM meta_domain")
        self.meta_domain = self.cur.fetchall()
        self.cur.execute("SELECT domain_text FROM domain")

        for i in self.cur.fetchall():
            self.domain.append(i[0])

        for i in self.domain:
            temp_name = []
            temp_struct = []
            self.cur.execute( "SELECT * FROM msg_type WHERE domain =\'{}\'".format(i))
            for j in self.cur.fetchall():
                temp_name.append(j[1])
                temp_struct.append(j[2])
            self.msg_type_name.append(temp_name)
            self.msg_type_struct.append(temp_struct)



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

            insert_str= ''
            if 'null' in curr_msg_struct and 'void' in curr_msg_struct.values():
                insert_str = self.createInsertExp(curr_msg_id, curr_date, curr_hour,'null', curr_msg_name , None)
                if log_file:
                    log_file.write(insert_str)
                    log_file.flush()
                self.cur.execute(insert_str)
                self.cur.execute("""INSERT INTO messages(msg_id, date, hour, domain ,msg_type, payload)
                                    VALUES (?, ?, ?, ?, ?, ? )""",
                                    (curr_msg_id, curr_date,curr_hour, curr_domain_string ,curr_msg_name, ''))

            elif 'char*' in curr_msg_struct .values():
                decode_msg = self.readFlexMsg().rstrip('\x00')
                insert_str = self.createInsertExp(curr_msg_id,curr_date, curr_hour,'flex', curr_msg_name, decode_msg)
                if log_file:
                    log_file.write(insert_str)
                    log_file.flush()
                self.cur.execute(insert_str)
                self.cur.execute("""INSERT INTO messages(msg_id, date, hour, domain, msg_type, payload)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (curr_msg_id , curr_date, curr_hour, curr_domain_string ,curr_msg_name, decode_msg))

            else:
                msg = self.readMsgStruct(curr_domain,curr_msg)
                insert_str = self.createInsertExp(curr_msg_id,curr_date, curr_hour,'struct', curr_msg_name,msg)
                if log_file:
                    log_file.write(insert_str)
                    log_file.flush()
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
        unpack = msg_struct.unpack_from(self.bin_data, self.curr_byte)
        size = msg_struct.size
        self.curr_byte += msg_struct.size

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
        self.cur.execute(drop_str)
        self.cur.execute(create_table_str)
        self.db.commit()


    def initDb(self):
        self.cur.execute("DROP TABLE IF EXISTS meta_domain")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS meta_domain(
                            meta_domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            meta_domain_text text
                            )""")

        self.cur.execute("DROP TABLE IF EXISTS domain")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS domain(
                     domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     domain_text text,
                     meta_domain text
                     )""")

        self.cur.execute("DROP TABLE IF EXISTS msg_type")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS msg_type(
                         msg_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         msg_type_name text,
                         msg_type_struct text,
                         domain text
                         )""")


        self.cur.execute("DROP TABLE IF EXISTS messages")

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

        s = struct.Struct(format)
        return s

    def queryMsgByDomain(self, domain):
        self.cur.execute("SELECT * FROM messages WHERE domain=?", (domain,))
        return  self.cur.fetchall()

    def queryMsgByType(self, msg_type):
        self.cur.execute("SELECT * FROM {}".format(msg_type))
        return self.cur.fetchall()

    def queryMsgAll(self, arr_size):
        self.cur.execute("SELECT * FROM messages")
        return self.cur.fetchall()

    def fetchManyAllTable(self, arr_size):
        data = self.cur.fetchmany(arr_size)
        return data

    def getAllMsgTableSize(self):
        return self.cur.rowcount

    def getDomainList(self):
        return self.domain

    def getMsgList(self):
        return self.msg_type_name

    def getTableData(self):
        return self.cur.description

    def getMsgMulti(self, msg_list):
        select_str = "SELECT * FROM messages WHERE "
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

        self.cur.execute(select_str)
        return self.cur.fetchall()


    def queryDate(self,domain, from_d,from_h ,to_d, to_h):
        exec_str = "SELECT * FROM messages WHERE "
        if from_d == '' and to_d == '':
            if from_h != '' and to_h == '':
                exec_str += "hour >= \'{}\'".format(from_h)
            elif from_h == '' and to_h != '':
                exec_str += "hour <= \'{}\'".format(to_h)
            else:
                exec_str += "hour BETWEEN \'{}\' AND \'{}\'".format(from_h, to_h)
        else:
            exec_str += "date BETWEEN \'{}\' AND \'{}\' AND hour BETWEEN \'{}\' AND \'{}\' ".format(from_d,to_d,from_h, to_h)
        self.cur.execute(exec_str)

        return self.cur.fetchall()
