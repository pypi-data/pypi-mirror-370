#region imports
import pyodbc
import json
import re
import time
import socket 
import select
from multiprocessing import Process, Queue #type:ignore
from queue import Empty #type:ignore
from typing import Any #type:ignore
import json #type:ignore
from datetime import datetime as dt
import traceback
import logging
import os
import csv
#endregion 
#region logging
#endregion
#region functions

def get_args_as_dict(sys_args:str) -> dict[str, str]:
    argsin = [
    i.split("=") for i in sys_args
    ]
    dictout = {}
    for t in argsin:
        dictout[t[0]] = t[1]

    return dictout


def strip_space(string_in: str) -> list[str]:
    """_summary_ removes extra spaces from HMS 3000 output files

    Args:
        string_in (str):string that is then broken up without spaces

    Returns:
        list[str]: a list of strings delimeted by spaces and then put into list
    """
    no_space: list[str] = []
    word = ""
    i = 0
    for char in string_in:
        
        if char  != " ":
            word += char
        else:
            if word != "":
                no_space.append(word)
            word = ""

        i += 1
    
    if word != "":
        no_space.append(word)
     
    return no_space

def parse(filepath:str) -> tuple[list[str],list[str]]:
    """_summary_takes HMS3000 files and gives a list of headers and data

    Args:
        filepath (str):  path to HMS 3000 data file

    Returns:
        tuple[list[str],list[str]]: outputs headers then data such that all normal values happen first then all -I then
        all values with +I
    """
    i = 0
    headers: list[str]= []
    datas: list[str] = []

    temp: list[str] = []


    with open(filepath,"r") as f:
        lines = f.readlines()
    for line in lines:
        if line.find("----") == -1 and line.find("===") == -1:
            temp = strip_space(line.strip())
            if temp != []:
                #dealing with non- numeric data
                if i == 0:
                    for obj in temp:headers.append(obj)
                if i == 1:
                    for obj in temp:datas.append(obj)
                if i != 0 and i != 1:
                    try:
                        float(temp[0])
                        for obj in temp:datas.append(obj)
                    except ValueError:
                        for obj in temp:headers.append(obj)

            i += 1
    # 19 to 28 need to be fixed 29 and 30 need to be removed


    i = 19
    plus = headers[29][:-1]
    minus = headers[30][:-1]
    last = headers[-1]
    new = headers[:29]

    for header in headers[19:28]: #type:ignore
        new.append(headers[i] + minus)
        new[i] =  headers[i] + plus
    
        i += 1

    new.append(last)  
    return new,datas

#endregion

#region classes

class sample():
    def __init__(self):
        """_summary_         main use is to keep track of sample measurements and current sample id\n
        keeps track of what inst has been used using a dict
        """
        
        self.id:str = ""
        
        self.description: str = "None"
        
        self.insts = {
            'fourpp': False,
            "nearir": False,
            "rdt": False,
            "hall": False,
        }
        self.test = False

    def check(self) -> bool:
        """_summary_ checks if instrument has a measurement yet

        Returns:
            bool:  True if measurement is done\n
            false if measurement is not done \n
        """
        if self.test: 
            return True

        for key in self.insts.keys():
            if not self.insts[key]:
                return False
        return True

class sql_client():
    
    def __init__(self, config_path: str) -> None:
        """_summary_ init sql class for connecting to sql database

        Args:
            config_path (str): path to config.json
        """
        self.host: str = ""
        self.user: str = ""
        self.pw: str = ""
        self.db: str = ""
        
        #config 
        self.config_path:str = config_path
        self.config_db:dict[str, str] = {
            
            }
        self.config_tools:dict[str, str] = {
            
        }
        self.hall_sys: str = ""
        #server connection
        self.sql: pyodbc.Connection
        self.cursor: pyodbc.Cursor
        #for building tables
        
        #sql querries
        self.tools:list[str] = []
        self.tables: list[str] = []
        self.missing_col_error:str = "207"
        self.illegal_char: list[str] = ["+","(",")","-",","]
        self.illegal_val: list[str] = ["hour", "second", "minute", "min", "-", ":"]
        self.hall_cols: list[str] = []
        
        #col check flags
        self.col_flags = []
        
        
        
        #int prefixes
        self.prefixes: dict[str,str] = {
            
        }
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        self.logger = logging.getLogger(name)
        self.logger.info("Connected to Server")
    
    def load_config(self):
        '''
        loads db connection config from config file
        '''
        with open(self.config_path, 'r') as file:
            config: dict[str, dict[str, str]]  = json.load(file)
            self.fpp_db_config = config["fourpp"]["db"]
            print(self.fpp_db_config)
            self.hall_sys: str = config["Hall"]["sys"]
            self.config_db: dict[str,str] = config["Database_Config"]
            self.config_tools: dict[str,str] = config["Tool_ip"]
            self.prefixes: dict[str,str] = config["Tool_pre"]
        #connection string from files
        self.host = self.config_db["host"]
        self.user = "pylocal"
        self.pw =  "pyvitro"
        self.driver = self.config_db["driver"]
        self.db = self.config_db["db"]
        #tool names from file
        self.tools = list(self.config_tools.values())
        #default col from sys
        col_dict = self.config_db["default_col"]
        self.def_col_names = []
        self.def_col_sizes = []
        self.fpp_col_names = []
        self.fpp_col_sizes = []
        
        for key, value in col_dict.items():
            self.def_col_names.append(key)
            self.def_col_sizes.append(value)
        self.col_flags = [False] * len(self.tools)
        for key, value in self.fpp_db_config.items():
                self.fpp_col_names.append(key)
                self.fpp_col_sizes.append(value)
    def connect(self):
        '''
        connects to sql server using configuration from json file\n
        if connects to server but cannot find correct db will create db\n
        '''
        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            driver = self.driver,
            password = self.pw,
            autocommit = True
        )
        self.cursor = self.sql.cursor()
        
        # #checking for db then connecting
        
        self.cursor.execute("SELECT name FROM sys.databases;")
        
        self.dbs = [x[0] for x in self.cursor]
        self.cursor.commit()
         
        
        if self.db not in self.dbs:
            self.cursor.execute(f"CREATE DATABASE {self.db}")
        self.cursor.commit()
        self.sql.close()
        
        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            password = self.pw,
            driver = self.driver,
            database = self.db,
            autocommit = False
        )

        self.cursor = self.sql.cursor()
        
        self.closed = self.sql.closed
        
    def check_columns(self, table: str , columns: str) -> None:
        """_summary_         takes table and cols in and then checks table for all cols inputted\n
        ADDS TABLE PREFIXES IS NOT PRESENT

        Args:
            table (str): table on sql db, should match the config tools section
            columns (str): string of columns seperated by comma
        """
        try:
            # print("FROM DB HANDLER")
            # print(columns)
            column_check: str = f"SELECT "#\"{columns}\" FROM {table}"
            temp_list = columns.split(",")
            for column in temp_list:
                column_check += f"\"{self.prefixes[table]}_{column}\", "
            column_check = column_check[:-2] + f" FROM {table}"
                
            self.cursor.execute(column_check)
            self.cursor.fetchall()
            
        except pyodbc.Error as e:
            error: str = str(e)
            positions = [match.start() for match in re.finditer(self.prefixes[table]+"_", error)]
            query = f"ALTER TABLE {table} ADD "
            cols_to_add: list[str] = []
            if len(positions) != 0:
                for pos in positions:
                    end = error[pos:].index("\'") + pos
                    val = f"{error[pos:end]}"
                    cols_to_add.append(val)
                
                
                i: int = 0
                for col in cols_to_add:
                    pref:str = f"{self.prefixes[table]}_"
                    if pref not in col:
                        cols_to_add[i] = f"\"{self.prefixes[table]}_{cols_to_add[i]}\" VARCHAR(255)"
                    else:
                        cols_to_add[i] = f"\"{cols_to_add[i]}\" VARCHAR(255)"
                    #dealing with ending chars we don't like
                    if ":" in cols_to_add[i]:
                        idx = cols_to_add[i].index(":")
                        cols_to_add[i] = cols_to_add[i][:idx] + cols_to_add[i][idx+1:]
                    
                    i += 1

                query += ",".join(cols_to_add)
   
                # print(f"adding {cols_to_add}")
                #  \"{col_to_add}\" VARCHAR(255)"
                # print(query)
                self.cursor.execute(query)
                self.sql.commit()
    
    def table_query_builder(self, tool:str, prefix:str, cols:list[str], data_types:list[str], data_sizes:list[str]) -> str:
        """ used to build table generating queries for SQL

        Args:
            tool (str):name of tool, gives name of table
            prefix (str): prefix that goes in front of the columns
            cols (list[str]): column names
            data_types (list[str]): each columns data type
            data_sizes (list[str]): each columns data size

        Returns:
            str: argument for self.cursor.execute()
        """
        query_pre:str = f"CREATE TABLE {tool} ("

        query_as_list = []
        i = 0 
        print(data_types,cols)
        for col in cols:
            if "(" in data_types[i] and ")" in data_types[i]:temp = f"{prefix}_{col} {data_types[i]}"
            else: 
                temp = f"{prefix}_{col} {data_types[i]}({data_types[i]})"
            query_as_list.append(temp)
            i += 1
            
            
        query_col = ",".join(query_as_list)
        query = f"{query_pre} {query_col})"

        return query

    
                        
    
    def check_tables(self):
        '''
        using tools from config file checks if corres. table exist, if not makes them
        '''
        self.logger.info("checking tables and building missing")
        temp: pyodbc.Cursor|None = None
        temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        self.tables = [x[2] for x in temp]
        hall_name:str = ""
        cols = self.def_col_names.copy()#["sample_id", "pos", "time", "description"]
        sizes = self.def_col_sizes.copy()#["255"] * 4
        #sizes.append("8000")
        #data_types = ["VARCHAR"] * 4
        #removing debugging and hosting tools
        tools = [i for i in self.tools if i != "host" and i != "testing"]
        
        for tool in tools:
            cols = self.def_col_names.copy()
            sizes = self.def_col_sizes.copy()
            
            if tool == "hall":hall_name = tool #seems unneeded but the var is used
            
            if tool not in self.tables:
                if tool == "fourpp":
                    k = 0
                    for name in self.fpp_col_names:
                        cols.append(name)
                        sizes.append(self.fpp_col_sizes[k])
                        k += 1
                        
                query = self.table_query_builder(tool,self.prefixes[tool],cols,sizes,[])
                self.cursor.execute(query)

        self.sql.commit()
        
        time.sleep(1) #wait for sql changes to come in
        if self.hall_sys == "HMS":
            temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            self.tables = [x[2] for x in temp]
            #self.hall_cols,_ = parse(r"sample_file.txt")
            self.hall_cols = ['DATE', 'User_Name', 'Sample_Name', 'I(mA)', 'B', 'D', 'D_T', 'MN', 'T(K)', 'Nb', 'u', 'rho', 'RH', 'RHA', 'RHB', 'NS', 'SIGMA', 'DELTA', 'ALPHA', 'Vab+I', 'Vbc+I', 'Vac+I', 'Vmac+I', 'V-mac+I', 'Vcd+I', 'Vda+I', 'Vbd+I', 'Vmbd+I', 'V-mbd', 'Vab-I', 'Vbc-I', 'Vac-I', 'Vmac-I', 'V-mac-I', 'Vcd-I', 'Vda-I', 'Vbd-I', 'Vmbd-I', 'Rs']
            self.check_columns(hall_name, (",").join(self.hall_cols))                    
        
        #checking that extra cols got added for other 4 tools
       


    def check_for_illegals(self, col_name: str) -> bool:
        """_summary_ checks for sql banned chars in col name

        Args:
            col_name (str):name you want to check
        Returns:
            bool: 
            false if any illegal char exist\n
            true if there are no illegal char
        """
        for char in self.illegal_char:
            if col_name.find(char) != -1:
                return False
        return True
    
    def check_val(self, val: str) -> bool:
        """_summary_

        Args:
            val (str): value you want to check

        Returns:
            bool: false if any illegal char exist\n
            true if there are no illegal char
        """
        
        for char in self.illegal_val:
            if val.find(char) != -1:
                return False
        return True
    
    def write(self, table: str, values : list[list[str]]):
        """_summary_        writes to sql database\n
        ADDS TABLE PREFIX IF NOT ADDED\n

        Args:
            table (str):table to put the data into
            values (list[list[str]]):a list of values formmated as follows\n
                    [[col1,val1], [col2,val2],...,[coln, valn]]
        """
        # self.cursor.execute("insert into fourpp(fpp_time, fpp_sample_id, fpp_resistance) values ('12:30', '30', '123')")
        # self.cursor.commit()
        #values is going to be formatted as         
        # values = [[col1, val1] , [col2, val2]]
        
        query = f"insert into {table}("
        end = "("
        for value in values:
            if self.prefixes[table] not in value[0]:
                if self.check_for_illegals(value[0]):
                    query += f"{self.prefixes[table]}_{value[0]}, " #building query 
                else:
                    query += f"\"{self.prefixes[table]}_{value[0]}\", "
            else:
                if self.check_for_illegals(value[0]):
                    query += f"{value[0]}, " #building query 
                else:
                    query += f"\"{value[0]}\", "#building query 
            
            if self.check_val(value[1]):
                end += f"\'{value[1]}\',"
            else:
                end += f"\'{value[1]}\', "
        end = end[:-1] 
        
        query = query[:-2] 
        
        query = query + ")" + " values " + end + ")"
        print(query)
        self.cursor.execute(query)
        self.sql.commit()
       
    def quit(self):
        '''
        ends connection to sql db
        '''
        #closes
        self.sql.close()

class tcp_multiserver():
    
    def __init__(self, config:str, ip:str, port:int, gui:Any, max_connections:int = 5):#, bus_out:"Queue[Any]" , bus_in:"Queue[Any]", max_connections:int = 5):
        """_summary_        class for handing multithreaded operation of a tcp server, handles communication to all intrument computer,\n
        to sql servers, and displaying information on the gu

        Args:
            config (str): path to config.json
            ip (str): ip to launch the server on
            port (int): port to open for server please use a port > 5000
            bus_out (Queue[Any]): a queue to communicate between server and other processes
            bus_in (Queue[Any]): used to communicate into server from other processes
            max_connections (int, optional): number of connections allowed to server. Defaults to 5.
        """
        self.ADDR: tuple[str, int] = (ip, port)
        print(self.ADDR)
        self.max_connections: int = max_connections
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_sockets: list[socket.socket] = []  # list of the client sockets being connected
        
        self.starttime: float
        
        self.display = gui
        
        # print("From TCP SERVER:",self.display.teststr)
        #data managementjson
        self.client_data: str
        #self.bus_out: "Queue[Any]" = bus_out
       # self.bus_in: "Queue[Any]" = bus_in
        self.SQL: sql_client = sql_client("config.json")
        self.samples: list[sample] = []  # list of samples
        
        #client ids
        self.read_to_read: list[socket.socket] = []
        
        #connection flags
        self.retries: int = 0
        self.network_status: bool = False
        self.db_status: bool|None = False
        
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        self.logger.info("Server initalized")


        self.logger.debug(f"Opening config from{config}")
        with open(config, 'r') as file:
            config_dict: dict[str,dict[str,str]] = json.load(file)
            self.config: dict[str, str] = config_dict['Tool_ip']
            self.prefixes: dict[str, str] = config_dict['Tool_pre'] 
        self.logger.debug("Loaded config")
        return
        
    def get_sample(self, tool, sample_id):
            self.logger.debug(f"searching for {sample_id}")
            found:bool = False
            i: int = 0
            current_sample:sample
            for samp in self.samples:
                if samp.id == sample_id:
                    current_sample = samp
                    samp.insts[tool] = True
                    found = True
                    insts = list(samp.insts.values())
                    if all(insts):
                        self.logger.debug(f" all measurements for {sample_id}, removing sample from local mem")
                        del self.samples[i]
                    self.logger.debug(f"found {sample_id}")
                    break
                i += 1
            if not found:
                self.logger.debug(f"{sample_id} not found creating new sample object")
                temp_samp:sample = sample()
                temp_samp.id = sample_id
                temp_samp.insts[tool] = True
                self.samples.append(temp_samp)
                current_sample = temp_samp
            return current_sample

    
    def SQL_startup(self):
        '''
        starts up sql server using the sql_client class
        '''
        try:
            self.SQL.load_config()
            self.SQL.connect()
            self.SQL.check_tables()
            self.db_status = True
        except Exception:
            print(traceback.format_exc())
            self.db_status = False
            
        return
          
    def connections(self, host:str = "8.8.8.8", port: int = 53, timeout: int = 30):
        """        checks the connection to the internet as well as connection to the db, if the db connection fails
        it attempts to reconnect
        

        Args:
            host (str, optional): host to ping. Defaults to "8.8.8.8"(google-public-dns-a.google.com).
            port (int, optional): port to check on. Defaults to 53.
            timeout (int, optional): how long to wait. Defaults to 3.
        """
        self.network_status = False
        self.db_status = False
        try:
            # socket.setdefaulttimeout(3) #removed to allow desc through might lead to future errors need to find better solution
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.network_status = True
        except socket.error:
            print(traceback.format_exc())
            self.network_status = False
        try:
            self.db_status  = self.SQL.quit()
            self.SQL_startup()
        except Exception:
            print(traceback.format_exc())
            self.SQL_startup()
        
    def all_sockets_closed(self):
        """closes the server socket and displays the duration of the connection"""
        print("\n\nAll Clients Disconnected\nClosing The Server...")
        endtime: float = time.time()
        elapsed = time.strftime("%H:%M:%S", time.gmtime(endtime - self.starttime))
        unit = (
            "Seconds"
            if elapsed < "00:01:00"
            else "Minutes"
            if "01:00:00" > elapsed >= "00:01:00"
            else "Hours"
        )
        self.server_socket.close()
        print(f"\nThe Server Was Active For {elapsed} {unit}\n\n")
        
    def active_client_sockets(self):
        """prints the IP and PORT of all connected sockets"""
        print("\nCurrently Connected Sockets:")
        for c in self.connected_sockets:
            print("\t", c.getpeername())
        
        self.display.test_connections() #tests connections to gui
    
    def serve_client(self, current_socket : socket.socket):
        '''Takes the msg received from the client and handles it accordingly'''
        t: dt  = dt.now()
        try:               
            self.tool = self.config[current_socket.getpeername()[0]]
            self.logger.debug(f"serving client {current_socket.getpeername()[0]}")
        except KeyError:
            # client_data = "Tool not found" ### UNCOMMENT FOR DEPLOYMENT COMMENTED FOR DEBUGGING
            self.logger.error(f"{self.tool} not found please add to config")
        try:
            client_data:str = current_socket.recv(1024).decode()
            self.logger.debug(f"got message from {self.tool} at {t}")
            #client has 3 tries to send something
            zero_byte_count:int = 0
            while zero_byte_count < 3:
                if client_data:
                    break
                else:
                    zero_byte_count += 1
                    print(zero_byte_count)
                    raise ConnectionResetError
                    
            if zero_byte_count == int(3):
                current_socket.close()
           # self.bus_out.put(client_data)  # put the data in the bus for the main app to handle
          #  incoming = self.bus_in.get(timeout=5)  # wait for the main app to process the data
          #  print(incoming)
            date_time: str = time.strftime("%d/%m/%Y, %H:%M:%S")
            print(
                f"\nReceived new message form client {current_socket.getpeername()} at {date_time}:"
            )
            print(client_data)

        except ConnectionResetError or Exception:
            print(f"\nThe client {current_socket.getpeername()} has disconnected...")
            self.connected_sockets.remove(current_socket)
            current_socket.close()
            
            if len(self.connected_sockets) != 0:  # check for other connected sockets
                self.active_client_sockets()
            else:
                print("No more clients connected")
                self.active_client_sockets()
                
        except Exception:
            self.connected_sockets.remove(current_socket)
            current_socket.close()
            if len(self.connected_sockets) != 0:  # check for other connected sockets
                self.active_client_sockets()
            else:
                print("No more clients connected")
                self.active_client_sockets()
            print("serving client error")
            print(traceback.format_exc())
        else:
            # print(client_data)
            try:
                if (client_data == "Bye" or client_data.upper() == "QUIT" or client_data.upper() == "Q"):self.disconnect_socket(current_socket)
                elif client_data == "ID":self.get_id(current_socket)
                elif client_data == "META":sample_id = self.send_meta(current_socket, self.tool)
                elif client_data == "MEAS":self.meas_prot(current_socket, self.tool, t)
                elif client_data == "UPDATE":self.update(current_socket, self.tool)
                
                else:
                    self.tool = current_socket.getpeername()[0]
                    current_socket.send(client_data.encode())
            except ConnectionResetError:
                self.connected_sockets.remove(current_socket)
                
    def update(self, current_socket:socket.socket, tool:str):
        self.logger.debug(f"{tool} requested sample list")
        ids: list[str] = []
        if len(self.samples) != 0:
            for samp in self.samples:
                if not samp.insts[tool]:
                    ids.append(samp.id)
            msg: str = ",".join(ids)
        if len(ids) == 0:#if len(ids) == 0:
            print("No samples to update")
            msg:str = "None"
        self.logger.debug(f"current samples {msg} need measurent on {tool}")
        current_socket.send(msg.encode())

    def disconnect_socket(self, current_socket:socket.socket):
        self.logger.debug(f"Closing the socket with client {current_socket.getpeername()} now...")
        current_socket.send("Bye".encode())
        current_socket.recv(1024)
        self.logger.debug("removing client from active list and closing server side socket")
        self.connected_sockets.remove(current_socket)
        current_socket.close()
        self.logger.debug(" double checking active list")
                
        if len(self.connected_sockets) != 0:
            self.active_client_sockets()
        else:
            self.active_client_sockets()
    
    def send_meta(self, current_socket:socket.socket, tool:str):
        self.logger.debug(f"asking for sample id")
        
        current_socket.send("awaiting sampleid".encode())
        sample_id = current_socket.recv(1024).decode()
        
        self.logger.debug(f"sample {sample_id} is in {tool}")
        self.logger.debug(f"getting meta data for {sample_id}")
        
        self.logger.debug("asking position")
        
        current_socket.send("pos".encode())
        self.pos = current_socket.recv(1024).decode()
        
        self.logger.debug(f"got position {self.pos}")
        samp:sample = self.get_sample(tool, sample_id)
        self.logger.debug("sending description to client")
        
        current_socket.send(samp.description.encode())
        self.logger.debug(f"sent {samp.description} to client")
        
   
    def meas_prot(self, current_socket:socket.socket, tool:str, t:str):
        
        self.logger.debug(f"asking for sample id")
        current_socket.send("awaiting sampleid".encode())
        sample_id = current_socket.recv(1024).decode()
        self.logger.debug(f"{sample_id} is in {tool}")
        self.logger.debug("acquiring sample object")
        current_sample:sample = self.get_sample(tool, sample_id)
            
        values: list[list[str]]#list[list[str | dt] | list[str]] | list[list[str|float|int]]#list[list[str]] | list[str] 
        
        current_socket.send("send description please".encode())
        current_sample.description = current_socket.recv(1024).decode()
        
        
        self.logger.debug(f"recv {current_sample.description}")
        values = [
                    ["time", str(t)],
                    ["sample_id", sample_id],
                    ["Description", current_sample.description],
                    ["pos", self.pos]
                    ]
                              
        current_socket.send(f"awaiting value from {tool}".encode())
        value = current_socket.recv(32768).decode()

        current_socket.send("data received".encode())

        if tool == "fourpp":
            values.append(["resistance", value]) 
                    
            self.SQL.write(tool, values)
                
        if tool == "nearir":
            wvs: list[str]  = value.split(",")
            spec = current_socket.recv(32768).decode()
            time.sleep(1)
            spec = spec.split(",")
            current_socket.send("data received".encode())
            i: int = 0
            col: list[str] = []
            cols: list[str] = [] 
            for wv in wvs:
                wv2 = wv[:wv.index(".")]
                        # print(wv2)
                col = [f"{self.prefixes[tool]}_{wv2}", spec[i]]
                values.append(col)
                        
                cols.append(f"{wv2}")
                i += 1
                    #check if each wavelenght has a col
                    
            self.SQL.check_columns(tool, (",").join(cols))
                    
            self.SQL.write(tool, values)
                    
        if tool == "hall":
            data = value.split(",")
            i = 0
            for sql_col in self.SQL.hall_cols:
                values.append([sql_col, data[i]])
                i += 1
                    
                    # value = float(value)
                    # values.append(["nb", str(value)])
                    
                    
                    
            self.SQL.write(tool, values)
        
    def get_id(self, current_socket):
        id: str = self.config[current_socket.getpeername()[0]]
        current_socket.send(id.encode())
             #   print("Responded by: Sending the message back to the client")   
        
    def server(self):
        """server setup and socket handling"""
        print("Setting up server...")
        try:
            self.logger.debug(f"setting up server at {self.ADDR}")
            self.server_socket.bind(self.ADDR)  
        except OSError:
            traceback.print_exc()
        self.server_socket.listen()
        self.retries = 0
        print("\n* Server is ON *\n")
        print("Waiting for clients to establish connection...")
        self.starttime = time.time()
        self.connected_sockets = []  # list of the client sockets being connected
        while True:            
            try:       
                ready_to_read, _, _ = select.select( #
                    [self.server_socket] + self.connected_sockets, [], []
                )                
                if len(ready_to_read) != 0:
                    for current_socket in ready_to_read:
                        if (
                            current_socket is self.server_socket
                        ):  # if the current socket is the new socket we receive from the server
                            (client_socket, client_address) = current_socket.accept()
                            print("\nNew client joined!", client_address)
                            self.connected_sockets.append(client_socket)
                            self.active_client_sockets()
                            continue
                        self.serve_client(current_socket)
            
            except ValueError:
                while self.retries < 5:
                    self.server()
                    time.sleep(1)
                    self.retries += 1
                #all retries failed hard restarting server
                # traceback.print_exc()
                print(" VALUE ERROR")
                self.server_socket.close()
                
                self.server()
            except KeyboardInterrupt:
                self.all_sockets_closed()
                
            except Exception:
                print("Server issue")
                # print(traceback.format_exc())
                while self.retries < 5:
                    self.server()
                    time.sleep(1)
                    self.retries += 1
                #all retries failed hard restarting server
                
                self.server_socket.close()
                
                self.server()

    def quit(self):
        """
        closes tcp server then calls sql quit function
        """
        self.server_socket.close()
        self.SQL.quit()

class client():
    
    def __init__(self, ip:str , port:int):
        """_summary_ class for tool code to talk to main tcp server

        Args:
            ip (str): ip of server
            port (int):port of server
        """
        self.ADDR = (ip, port)
        
        self.data = ""
        self.flag = 0
        self.tool = ""
        
        self.soc: socket.socket
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.debug(f"tcp client starts with ip {ip} and port {port}")
        # self.msg_in = msg_in
        # self.msg_out = msg_out

    def connect(self):
        ''' connects to server
        '''
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.soc.connect(self.ADDR)
            self.logger.debug(f"connected to server at {self.ADDR}")
        except OSError or ConnectionRefusedError as e:
            self.logger.error(f"Connection to server at {self.ADDR} failed. Please check if the server is connected to the internet and that the IP and PORT numbers are correct on both ends")
            self.logger.error(traceback.format_exc())
            return e
            # sys.exit()
            
    def disconnect(self):
        '''
        disconnects
        '''
        self.logger.info(f"Disconnecting from server at {self.ADDR}")
        self.soc.send("Q".encode())
        self.soc.close()
            
    def id(self):
        '''
        gets id of client
        '''
        self.logger.debug("Requesting ID from server")
        if self.tool == "":
            self.soc.send("ID".encode())
            
            self.tool = self.soc.recv(1024).decode()
            self.logger.debug(f"Received ID from server: {self.tool}")
            # print(self.tool)
        else:
            return self.tool
        
class FileManager:
    def __init__(self, tool: str, size_lim: str) -> None:
        """_summary_

        Args:
            tool (str): _description_
            size_lim (str): _description_
        """
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.debug(f"file manager starts with tool {tool} and size limit {size_lim} GB")
        
        self.tool = tool
        self.path: str = os.path.join(os.getcwd(),"tools", tool, "data")
        self.logger.debug(f"looking for data folder at {self.path}")
        if not os.path.exists(self.path):
            self.logger.debug(f"data folder not found at {self.path}, creating it")
            os.mkdir(self.path)    
        self.logger.debug(f"data folder found at {self.path}")
        
        self.size_lim = size_lim #in gb
    #first check folder size

    def rotating_file_handler(self) -> None:
        '''
        checks size of folder and compares it to size_lm if larger delete oldest file
        '''
        
        #get file size
        byte_lim: float = float(self.size_lim) * 1024 * 1024 * 1024
        total_size = 0
        self.logger.debug(f"checking folder size, limit is {byte_lim} bytes")
        for dirpath,_,filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)                  
        
        
        if total_size > byte_lim:
            self.logger.debug(f"folder size {total_size} bytes is larger than limit {byte_lim} bytes, deleting oldest file")
            #sort files by date
            files = os.listdir(self.path)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.path, x)))
            #delete oldest file
            oldest_file = os.path.join(self.path, files[0])
            self.logger.debug(f"deleting oldest file {oldest_file}")
            os.remove(oldest_file)
            # print(f"Deleted {oldest_file}")

    def write_data(self, sample_num: str, header: list[str], data: list[str] | list[list[str | float | int]]) -> None:
        """_summary_ writes data to data file

        Args:
            sample_num (str): sample number
            header (list[str]): column names
            data (list[str] | list[list[str  |  float  |  int]]): data to write out
        """
        
        self.logger.debug(f"writing data to file for sample {sample_num} with header {header} and data {data}")
        self.rotating_file_handler()
        self.date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")
        
        file_name = f"{self.path}\\{sample_num}_{self.tool}_{self.date}.csv"
        self.logger.debug(f"writing data to file {file_name}")
        with open(file_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(header)
            if isinstance(data[0], list):
                for row in data:
                    writer.writerow(row)
            else:
                writer.writerow(data)
        self.logger.debug(f"data written to file {file_name}")
#endregion
    



    
if __name__ == "__main__":
    sqltest = sql_client("config.json")
    sqltest.load_config()
    sqltest.connect()
    sqltest.check_tables()
    test_vals = [
        ["fpp_sample_id", "test_sample"],
        ["fpp_pos", "test_pos"],
        ["fpp_time", "test_time"],
        ["fpp_description", "test_description"],
        ["fpp_resistance", "test_resistance"]
        ]
    sqltest.write("fourpp", test_vals)