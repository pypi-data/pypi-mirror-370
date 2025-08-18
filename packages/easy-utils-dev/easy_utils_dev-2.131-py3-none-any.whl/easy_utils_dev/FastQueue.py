from easy_utils_dev.utils import getRandomKey
import concurrent.futures
from threading import Thread
import traceback

class FastQueue : 
    def __init__(self,request_max_count=30,) -> None:
        self.queue = []
        self.request_max_count = request_max_count
        pass
    
    def removeFromQueue(self , id) :
        data = self.queue
        for elem in data :
            if elem['requestId'] == id :
                data.remove(elem)
                self.queue= data
                break
        return data

    def execute_task(self , task ):
        task_id = task['requestId']
        function = task['action']
        actionArgs = task['actionArgs']
        onComplete = task['onComplete']
        onFailure = task['onFailure']
        onFailureArgs : dict = task['onFailureArgs']
        onCompleteArgs : dict = task['onCompleteArgs']
        onSuccess = task['onSuccess']
        onSuccessArgs : dict = task['onSuccessArgs']
        supressError = task['supressError']
        isSuccess= False
        result = None
        try:
            task['running'] = True
            result = function(**actionArgs)
            task['result'] = result
            task['completed'] = True
            task['running'] = False
            task['error'] = None
            task['traceback'] = None
            isSuccess = True
            if onSuccess : 
                for key , value in task.items() :
                    onSuccessArgs.update({ key  : value })
                onSuccessArgs.update({'_task' : task })
                onSuccessArgs.update({'result' :  result })
                onSuccessArgs.update({'isSuccess' :  True })
                onSuccess(**onSuccessArgs)
        except Exception as e:
            task['error'] = e
            task['traceback']= traceback
            if onFailure : 
                onFailureArgs.update({'_task'  :  task })
                for key , value in task.items() :
                    onFailureArgs.update({ key  : value })
                onFailureArgs.update({'traceback'  : traceback })
                onFailureArgs.update({'error' : e })
                onFailureArgs.update({'isSuccess' : False })
                onFailure(**onFailureArgs)
            if not supressError :
                print(traceback.format_exc())
            task['completed'] = True
            task['result'] = None
            task['running'] = False
        onCompleteArgs.update({'_task'  : task })
        onCompleteArgs.update({'isSuccess' : isSuccess })
        for key , value in task.items() :
            onCompleteArgs.update({ key  : value })
        if onComplete : 
            onComplete(**onCompleteArgs)
        self.removeFromQueue(task_id)
        if 'exception' in task and not supressError :
            raise task['exception']
        return result

    def getCurrentQueueLength(self) :
        return len(self.queue)
    
    def getQueue(self) :
        return self.queue

    def addToQueue( 
            self, 
            action , 
            onComplete=None , 
            onSuccess=None , 
            onFailure=None,
            onCompleteArgs={},
            actionArgs={},
            onFailureArgs={},
            onSuccessArgs={},
            supressError=False,
        ) :
        id = getRandomKey(n=5)
        self.queue.append(
            {
                'action' : action , 
                'requestId' : id ,
                'onComplete' : onComplete,
                'onFailure' : onFailure,
                'completed' : False,
                'forceTerminate' : False,
                'result' : None,
                'onCompleteArgs' :onCompleteArgs ,
                'actionArgs': actionArgs ,
                'onFailureArgs':onFailureArgs ,
                'onSuccessArgs':onSuccessArgs,
                'onSuccess':onSuccess,
                'supressError' : supressError
            }
        )
        return id
    
    def clearQueue(self):
        self.queue = []
        self.numberOfRequests = 0

    def getAllQueueResults(self) :
        x = [item['result'] for item in self.queue]
        return x
    
    def runQueue( self, await_results=True , maxRequests=None ) :
        '''
        this function will run all the requests inside the queue.
        await_results. 
            if True. the results will be returned as array for each request.
            if false: the thread object will be returned. results can be retreived by calling getAllQueueResults
        maxRequests : maximum number of requests to be executed at a time. default is self.request_max_count.
        '''
        if not maxRequests :
            maxRequests= self.request_max_count
        else :
            maxRequests= int(maxRequests)
        def main() : 
            with concurrent.futures.ThreadPoolExecutor(max_workers=maxRequests) as executor:
                futures = [executor.submit(self.execute_task, task) for task in self.queue]
                concurrent.futures.wait(futures)
                self.final_results =  [future.result() for future in futures]
                return self.final_results
            
        if await_results : 
            return main()
        else :
            self.t= Thread(target=main)
            self.t.daemon = True
            self.t.start()
            return self.t
        
    def waitQueueResults(self) :
        if self.t :
            self.t.join()

    def getLastResults(self) :
        return self.final_results