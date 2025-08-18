

import oracledb
from easy_utils_dev.encryptor import initCryptor

class OracleDb :
    def __init__(self) :
        self.encrypt = initCryptor()
        self.connection = None
        self.sessions = []
        self.dbUser= None
        pass

    def validate_user(self , user ) :
        okUsers = ['wdm' , 'otn' , 'snml']
        if user not in okUsers:
            raise ValueError(f'Not valid database user. "{user}"')

    def get_pw(self , legacy=False) :
        if not legacy :
            return self.encrypt.dec_base64('Tm9raWFOZm10KzIwMjErMTIh')
        return self.encrypt.dec_base64('YWx1KzEyMz8=')   


    def connect(self , host , port=4999 , user='wdm' , legacy=False , program="Lynx.Db.Module") :
        self.dbUser=user
        self.validate_user(user)
        connection = oracledb.connect(
            user=user,
            password=self.get_pw(legacy),
            host=host,
            port=port,
            service_name="OTNE",
            program=program
        )
        self.sessions.append(connection)
        self.connection = connection
        return connection , connection.cursor()
    
    def get_results_limited(self , cursor, limit) :
        if limit == 0  :
            return cursor.fetchall()
        else :
            return cursor.fetchmany(limit)


    def execute_dict(self,  query , connection=None , limit=0) :
        if not connection :
            connection = self.connection
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in self.get_results_limited(cursor , limit)]
        cursor.close()
        return data
    
    def close(self , connection=None) :
        if not connection :
            connection = self.connection
        connection.close()

if __name__ == '__main__' :
    wsnoc = OracleDb()
    wsnoc.connect(
        host= '10.0.0.1' ,
        port=4999 ,
        user='wdm',
        legacy=False
    )
    results = wsnoc.execute_dict(f"select * from networkconnection")
    wsnoc.close()