from .utils import getRandomKeysAndStr , getTimestamp , start_thread , kill_thread , getRandomKey
from time import sleep


class AbortableTask :
    def __init__(self, task , args=[] , kwargs={}, timeout=None  , pid=None) :
        if not pid :
            self.pid = getRandomKey(5)
        else :
            self.pid = pid
        self.result= None
        self.thread = None
        self.aborted=False
        self.response = {}
        self.error = False
        self.message = ''
        self.starttimestamp = getTimestamp()
        self.endtimestamp = 0
        self.operation = task
        self.args = args
        self.kwargs = kwargs
        self.timeout = timeout


    def start(self) :
        if self.timeout :
            terminationts = getTimestamp(after_seconds=self.timeout)
        def thread_run() :
            try :
                self.result =  self.operation( *self.args, **self.kwargs )
                self.error = False
                self.message = ''
                self.endtimestamp = getTimestamp()
            except Exception as error :
                self.error = True
                self.message = str(error)
        thread = self.thread = start_thread( target = thread_run )  
        while thread.is_alive() :
            if self.timeout :
                if terminationts < getTimestamp() :
                    self.kill()
            if self.aborted :
                self.response = {
                    'message' : 'request aborted.' , 
                    'pid' : self.pid ,
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
        sleep(.2)
        self.response = {
            'message' : 'request completed.' , 
            'pid' : self.pid , 
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


    def kill(self) :
        self.endtimestamp = getTimestamp()
        kill_thread(self.thread)
        sleep(.5)
        self.aborted=True


def test(i) :
    print('test function started ...')
    sleep(10)
    print(f'{i} test function terminated.')


if __name__ == '__main__' :
    
    # start the function but abort it after sometime with return result
    process = AbortableTask(task=test , args=[10] , timeout=2)
    result = process.start()
    print(result)
    pass