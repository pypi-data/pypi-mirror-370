import sqlite3 , os  ,time
from .debugger import DEBUGGER
from .utils import getRandomKey
from .custom_env import custom_env , setupEnvironment 
from .utils import fixTupleForSql

env = custom_env()

def getLoggerFromMemory( id ) :
    '''
    When Logger/Debugger is called or initialized it automatically is stored in memory with certain id.
    you can call this event from memory by passing that id to this function which will return the event if found.
    if not.. it will return None
    '''
    ev = env.get('simple_sqlite' , {} )
    return ev.get( id , None )


class initDB :
    def __init__(self, db=None , logger=None,enable_log=True,id=getRandomKey(n=5),loggerName=None,WAL_JOURNAL=False) :
        self.db_file = db
        self.disableLog = False
        self.logger = logger
        self.enable_log = enable_log
        self.lastCur = None
        self.lastCon=None
        self.id = id
        self.WAL_JOURNAL = WAL_JOURNAL
        self.applyDatabaseParams=True
        if not loggerName :
            self.loggerName = 'simple-sqlite'
        else :
            self.loggerName = loggerName
        setupEnvironment(self.loggerName)
        env[self.loggerName][id] = self
        if not logger : 
            self.logger = DEBUGGER(name=self.loggerName)
        if not enable_log and self.logger:
            self.logger.disable_print()

    def config_database_path(self,path) :
        self.logger.debug(f'Database path set to {path}')
        self.db_file = path
        
    def fixTupleForSql(self , list:list ):
        if len(list) <= 1 :
            results = str(list).replace('[' , '(' ).replace(']' , ')')
        else :
            results = tuple(list)
        return results

    def db_connect(self,  WAL=False , timeout: int=30):
        self.logger.debug(f'connecting to {self.db_file}')
        self.con = sqlite3.connect(self.db_file , check_same_thread=False,timeout= timeout)
        self.cur = self.con.cursor()
        if WAL or self.WAL_JOURNAL :
            self.con.execute("PRAGMA journal_mode=WAL;")
            self.con.commit()
        return  self.cur , self.con 

    def execute_dict(self,cli:str) :
        self.logger.debug(f"execute_dict: {cli}")
        cur , conn = self.db_connect()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        c = conn.cursor()
        h = c.execute(cli).fetchall()
        if not 'select' in cli.lower() :
            conn.commit()
        conn.close()
        return h
    
    def vacuum(self) :
        try :
            cur , conn = self.db_connect()
            cur.execute('VACUUM')
            conn.commit()
            conn.close()
        except :
            pass


    def createTable(self , tableName ,data=[] , autoId=True) :
        self.logger.debug(f'Creating table : {data}')
        try :
            cur,con = self.db_connect()
            cli = f"""CREATE TABLE IF NOT EXISTS {tableName} ( \n"""
            if autoId : 
                data.insert(0,{
                    'column' : 'id' ,
                    'params' : 'INTEGER PRIMARY KEY AUTOINCREMENT'
                })
            for elem in data :
                if "column" in elem:
                    cli += f""" {elem['column']} {elem['params']} ,\n"""
                elif "constraint" in elem:
                    cli += f""" {elem['constraint']} {elem['params']} ,\n"""
        except Exception as error : 
            self.logger.debug(f"create table faced error {error}")
            try :
                con.close()
            except :
                pass
            raise
                
        cli = cli.rstrip(', \n') + ' \n)'
        cur.execute(cli)
        con.commit()
        con.close()

    def execute(self,cli) :
        self.logger.debug(f'Executing : {cli}')
        cur,con = self.db_connect()
        h = cur.execute(cli).fetchall()
        if not 'select' in cli.lower() :
            con.commit()
        con.close()
        return h

    def insert_to_table(self,table_name , table_headers , table_values , autocommit= True) :
        cur , con = self.db_connect()
        self.logger.debug(f'Inserting data into {table_name}'.format(table_name=table_name))
        table_headers = fixTupleForSql(table_headers)
        table_values = fixTupleForSql(table_values)
        cli = f"INSERT INTO {table_name} {table_headers} VALUES{table_values}"
        self.logger.debug('INFO DB EXECUTION: '+cli)
        for i in range(10) :
            try :
                cur.execute(cli)
                if autocommit == True :
                    con.commit()
                con.close()
                break
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e).lower():
                    time.sleep(1)  # backoff
                else:
                    con.close()
                    raise
        try :
            con.close()
        except :
            pass
        return cur.lastrowid
    
    def insert_to_table_from_dict(self , table_name , dict : dict , autocommit= True , fix_escape_char=False ) :
        '''
        Inserting row to table using dict template\n
        fix_escape_char : will replace all single quotes with two single quotes -> ' => ''.
        --------------------------------------------------------------------------
        example :
        dict_template : {
            id : 1 ,
            name : Ahmed,
            Age : 30
        }
        '''
        headers = list(dict.keys())
        values = list(dict.values())
        if fix_escape_char :
            values = [str(x).replace("'" , "''") for x in values ]
        self.logger.debug(f'headers= {headers}')
        self.logger.debug(f'values= {values}')
        return self.insert_to_table(table_name , headers , values , autocommit= autocommit)
            
        

    def insert_to_table_bulk(self, tableName, values=[], autoCommit=True , return_cursor=False):
        '''
        Aim : insert many rows using single transaction. instead of inserting 1by1 (multiple transactions).
        This is way faster than insert_to_table function if you are going to insert many rows.
        values_template : [
            {
                id : 1 ,
                name : ahmed
            },
            {
                id : 2 ,
                name : mohamed
            }
        ]
        '''
        cur, con = self.db_connect()
        self.logger.debug(f'Inserting data into {tableName}')
        headers = ', '.join(values[0].keys())
        placeholders = ', '.join(['?'] * len(values[0]))
        cli = f"INSERT INTO {tableName} ({headers}) VALUES ({placeholders})"
        self.logger.debug(f'Constructed SQL: {cli}')
        rows = [tuple(v.values()) for v in values]
        try:
            cur.executemany(cli, rows)
            if autoCommit:
                con.commit()
            rowEnd = cur.rowcount
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting data: {e}")
            con.close()
            raise
        finally:
            if not return_cursor :
                con.close()
        if return_cursor :
            return con , cur
        return list(range(rowEnd)), cur.lastrowid

    def dump_database(self,outputPath , export_rows=True ,fileName=None,skip_create=False) :
        cur , conn = self.db_connect()           
        if not fileName :
            fileName = os.path.basename(outputPath)
        outputPath= os.path.dirname(outputPath)
        fullPath = os.path.join(outputPath, fileName)
        if not os.path.exists(outputPath) :
            os.makedirs(outputPath)
        if os.path.exists(fullPath) :
            os.remove(fullPath)
        with open(fullPath, 'a+') as f:
            inside_create = False
            for line in conn.iterdump():
                # Check if we're inside a CREATE TABLE or CREATE VIEW statement
                if skip_create:
                    # Start of CREATE TABLE or CREATE VIEW statement
                    if line.lower().startswith('create table') or line.lower().startswith('create view'):
                        inside_create = True
                    
                    # If we're inside a CREATE statement, skip the line
                    if inside_create:
                        # We continue skipping lines until we encounter the closing parenthesis of the CREATE statement
                        f.write('')  # Optionally, you can write an empty line for debugging purposes
                        if line.strip().endswith(');'):
                            inside_create = False
                        continue

                if not export_rows :
                    if line.lower().startswith('insert into') :
                        continue
                f.write(line + '\n')
        return fullPath
        
    def reset(self , exclude: list=[]) :
        '''
        This function will reset all the database tables. to skip some tables, add their names to exclude array.
        '''
        cli = f"SELECT name FROM sqlite_master where type == 'table'"
        results= self.execute_dict(cli)
        exclude = [str(x).lower() for x in exclude]
        cur , conn = self.db_connect()
        for elem in results :
            tableName = elem['name']
            if tableName.lower() in exclude :
                continue
            self.logger.info(f'Resetting table : {tableName}')
            cli = f'DELETE FROM {tableName}'
            cur.execute(cli)
        cli = f'DELETE FROM sqlite_sequence'
        cur.execute(cli)
        cli = f'VACUUM'
        conn.commit()
        cur.execute(cli)
        conn.commit()
        conn.close()

    def execute_script(self, scriptPath) :
        if not os.path.exists(scriptPath) :
            raise Exception(f'SQL script not found: {scriptPath}')
        cur , conn = self.db_connect()
        with open(scriptPath, 'r') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
        conn.close()
        

    def exists( self , query , return_bool=True ) :
        '''
        select name from nodes where node = 'ahmed'
        '''
        query = f"SELECT exists ( {query} ) as return_code "
        result = self.execute_dict(query)[0]['return_code']
        if return_bool :
            if result == 0 :
                return False
            return True
        else :
            return result


    def add_column_to_table(self, table_name, column_name, column_type, default_value=None):
        """
        Adds a new column to an existing SQLite table.

        Args:
            db_path (str): Path to the SQLite database file.
            table_name (str): Name of the table to modify.
            column_name (str): Name of the new column to add.
            column_type (str): SQLite data type (e.g., 'TEXT', 'INTEGER').
            default_value (any, optional): Optional default value for the new column.

        Raises:
            sqlite3.OperationalError: If the column already exists or SQL is invalid.
        """
        cursor , conn = self.db_connect()

        # Construct the SQL statement
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            # Properly format the default value depending on its type
            if isinstance(default_value, str):
                default_value = f"'{default_value}'"
            sql += f" DEFAULT {default_value}"
        try:
            cursor.execute(sql)
            conn.commit()
            self.logger.debug(f"Column '{column_name}' added to '{table_name}'.")
        except sqlite3.OperationalError as e:
            self.logger.error(f"SQLite error: {e}")
        finally:
            conn.close()

    def column_exists(self , table_name, column_name):
        """
        Checks if a column exists in a given SQLite table.

        Args:
            db_path (str): Path to the SQLite database.
            table_name (str): Name of the table to inspect.
            column_name (str): Column to check for.

        Returns:
            bool: True if the column exists, False otherwise.
        """
        try:
            cursor , conn = self.db_connect()
            # Execute PRAGMA to get the table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            # Fetch column names from the result
            columns = [row[1] for row in cursor.fetchall()]  # row[1] is the column name
            conn.close()
            # Return True if the column is found in the list, else False
            return column_name in columns
        except sqlite3.Error as e:
            self.logger.error(f"SQLite error: {e}")
            return False

if __name__ == '__main__' :
    # # # # example
    # db = initDB()
    # db.config_database_path('database.db')
    # results = db.execute_dict(f"select * from users where name='7amada'")
    # db.reset(exclude=['users'])
    # dumpedSql = db.dump_database('./here/' , export_rows=True , fileName='7amada.sql' , skip_create=True)
    pass