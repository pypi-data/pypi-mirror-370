from werkzeug.serving import ThreadedWSGIServer
from easy_utils_dev.utils import getRandomKey , generateToken , getTimestamp
from flask_socketio import SocketIO
from engineio.async_drivers import gevent
from engineio.async_drivers import threading
from flask_cors import CORS
import logging  , os
from flask import Flask
from threading import Thread
from easy_utils_dev.custom_env import cenv
from easy_utils_dev.utils import kill_thread
from multiprocessing import Process
from werkzeug.serving import make_ssl_devcert
from time import sleep
from easy_utils_dev.utils import start_thread , getRandomKeysAndStr , mkdirs

def getClassById( id ) :
    return cenv[id]

def create_ssl(host,output) :
    '''
    host : is the IP/Adress of the server which servers the web-server
    output: the output locaiton to generate the ssl certificate. it should end with filename without extension
    '''
    return make_ssl_devcert( output , host=host)
    


class Abort :
    def __init__(self, requestId=getRandomKeysAndStr(50)) :
        self.requestId = requestId
        self.result= None
        self.thread = None
        self.aborted=False
        self.response = {}
        self.error = False
        self.message = ''
        self.starttimestamp = getTimestamp()
        self.endtimestamp = 0
        self.kill = self.api_abort
        pass


    def abortable_process(self , operation , args=[] , kwargs={}) :
        def thread_run() :
            try :
                self.result =  operation( *args, **kwargs )
                self.error = False
                self.message = ''
                self.endtimestamp = getTimestamp()
            except Exception as error :
                self.error = True
                self.message = str(error)
        thread = self.thread = start_thread( target = thread_run )  
        while thread.is_alive() :
            sleep(.1)
            if self.aborted :
                self.response = {
                    'message' : 'request aborted.' , 
                    'id' : self.requestId ,
                    'status' : 405 , 
                    'result' : None, 
                    'error' : self.error , 
                    'error_message' : '',
                    'starttimestamp' : self.starttimestamp,
                    'endtimestamp' : self.endtimestamp,
                    'aborted' : True,
                    'threadIsAlive' : thread.is_alive()
                    } 
                return self.response
        sleep(.2)
        self.response = {
            'message' : 'request completed.' , 
            'id' : self.requestId , 
            'status' : 200 , 
            'result' : self.result , 
            'error' : self.error , 
            'error_message' : self.message ,
            'starttimestamp' : self.starttimestamp,
            'endtimestamp' : self.endtimestamp,
            'aborted' : False ,
            'threadIsAlive' : thread.is_alive()
        }
        return self.response


    def api_abort(self) :
        self.endtimestamp = getTimestamp()
        kill_thread(self.thread)
        sleep(.5)
        self.aborted=True


class UISERVER :
    def __init__(self ,
                 id=getRandomKey(n=15),
                 secretkey=generateToken(),
                 address='localhost',
                 port=5312 , 
                 https=False , 
                 ssl_crt=None,
                 ssl_key=None,
                 template_folder='templates/' ,
                 static_folder = 'templates/assets'
                   ,**kwargs
                ) -> None:
        self.id = id
        self.static_folder = static_folder
        self.app = app = Flask(self.id , template_folder=template_folder  ,  static_folder=self.static_folder )
        app.config['SECRET_KEY'] = secretkey
        CORS(app,resources={r"/*":{"origins":"*"}})
        self.address= address 
        self.port = port
        self.thread = None
        self.ssl_crt=ssl_crt
        self.ssl_key=ssl_key
        self.enable_test_url=True
        self.abort_requests = {}
        if https :
            self.httpProtocol = 'https'
        else :
            self.httpProtocol = 'http'
        self.socketio = SocketIO(app , cors_allowed_origins="*"  ,async_mode='threading' , engineio_logger=False , always_connect=True ,**kwargs )
        cenv[id] = self
        self.fullAddress = f"{self.httpProtocol}://{self.address}:{self.port}"

    def update_cert(self , crt, ssl ) :
        self.ssl_crt=crt
        self.ssl_key=ssl


    def getAbort(self , id ) :
        result : Abort = self.abort_requests.get(id , Abort)
        return result

    def updateAbort( self , id , abort ) :
        self.abort_requests[id] = abort

    def getInstance(self) :
        return self.getFlask() , self.getSocketio() , self.getWsgi()
    
    def getSocketio( self ):
        return self.socketio
    
    def getFlask( self ):
        return self.app
    
    def getWsgi(self) :
        return self.wsgi_server
    
    def shutdownUi(self) :
        kill_thread(self.thread)
        self.wsgi_server.server_close()
        self.wsgi_server.shutdown()

    def _wait_th(self , t ) :
        t.join()
        
    def thrStartUi(self , suppress_prints=True) :
        if self.enable_test_url :
            if not suppress_prints :
                print(f'TEST URL GET-METHOD /connection/test/internal')
            @self.app.route('/connection/test/internal' , methods=['GET'])
            def test_connection():
                return f"Status=200<br> ID={self.id}<br> one-time-token={getRandomKey(20)}"
        if self.httpProtocol == 'http' :
            con = None
        elif self.httpProtocol == 'https' :
            con=(self.ssl_crt , self.ssl_key)
        self.wsgi_server = wsgi_server = ThreadedWSGIServer(
            host = self.address ,
            ssl_context=con,
            # ssl_context=('ssl.crt', 'ssl.key'),
            port = self.port,
            app = self.app )
        if not suppress_prints :
            print(f"web-socket: {self.fullAddress}")
            print(f"UI URL : {self.fullAddress}")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        wsgi_server.serve_forever()
    
    def startUi(self ,daemon , suppress_prints=True) :
        self.thread = self.flaskprocess = Thread(target=self.thrStartUi , args=[suppress_prints])
        self.flaskprocess.daemon = daemon
        self.flaskprocess.start()
        start_thread(target=self._wait_th , args=[self.thread])
        return self.thread
    
    def stopUi(self) :
        kill_thread(self.thread)
        return True
    
