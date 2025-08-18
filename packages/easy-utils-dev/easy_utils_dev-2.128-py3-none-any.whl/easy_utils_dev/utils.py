import datetime , string , subprocess , psutil ,secrets , os ,ping3 , time , sys , argparse , ctypes , math , threading , random , jwt , socket


def getRandomKey(n=10, numbers=True) :
    """
    Generate a random key of specified length.
    
    Args:
        n (int): Length of the random key to generate. Default is 10.
        numbers (bool): If True, generates only numbers. If False, generates only lowercase letters.
    
    Returns:
        str: A random string of specified length containing either numbers or lowercase letters.
    """
    if numbers :
        return ''.join(secrets.choice(string.digits)
            for i in range(n))
    else :
        return ''.join(secrets.choice(string.ascii_lowercase )
            for i in range(n))


def now() :
    """
    Get current datetime object.
    
    Returns:
        datetime: Current date and time.
    """
    return datetime.datetime.now()

def date_time_now() :
    """
    Get current date and time as a string with microseconds removed.
    
    Returns:
        str: Current date and time in string format (YYYY-MM-DD HH:MM:SS).
    """
    return  str( now().replace(microsecond=0))


def timenow() : 
    """
    Get current date and time in a specific string format.
    
    Returns:
        str: Current date and time in format "DD/MM/YYYY HH:MM:SS".
    """
    return  str(now().strftime("%d/%m/%Y %H:%M:%S"))
    

def timenowForLabels() : 
    """
    Get current date and time formatted for use in file labels.
    
    Returns:
        str: Current date and time in format "DD-MM-YYYY_HH-MM-SS".
    """
    return now().strftime("%d-%m-%Y_%H-%M-%S")

def fixTupleForSql(list):
    """
    Convert a list to a format suitable for SQL queries.
    
    Args:
        list: List of values to be converted.
    
    Returns:
        tuple or str: If list has more than one element, returns a tuple.
                     If list has one element, returns a string in parentheses.
    """
    if len(list) <= 1 :
        execlude = str(list).replace('[' , '(' ).replace(']' , ')')
    else :
        execlude = tuple(list)
        
    return execlude

def getDateTimeAfterFewSeconds(seconds=10):
    """
    Get date and time after adding specified seconds to current time.
    
    Args:
        seconds (int): Number of seconds to add to current time. Default is 10.
    
    Returns:
        str: Future date and time in format "YYYY-MM-DD HH:MM".
    """
    current_time = datetime.datetime.now()
    new_time = current_time + datetime.timedelta(seconds=seconds)
    return new_time.strftime('%Y-%m-%d %H:%M')


def isOsPortFree(port : str):
    """
    Check if a specific port is available on the operating system.
    
    Args:
        port (str): Port number to check.
    
    Returns:
        bool: True if port is free, False if port is in use.
    """
    for conn in psutil.net_connections():
        if str(conn.laddr.port) == port :
            return False
    return True

def getRandomKeysAndStr(n=5, upper=False):
    """
    Generate a random string of specified length.
    
    Args:
        n (int): Length of the random string to generate. Default is 5.
        upper (bool): If True, returns string in uppercase. Default is False.
    
    Returns:
        str: Random string containing letters and digits.
    """
    s = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    if upper :
        return s.upper()
    return s

def generateToken(iter=5,split=False) :
    """
    Generate a random token consisting of multiple parts.
    
    Args:
        iter (int): Number of parts in the token. Default is 5.
        split (bool): If True, parts are joined with hyphens. Default is False.
    
    Returns:
        str: Random token with specified number of parts.
    """
    if not split :
        return ''.join( [ getRandomKeysAndStr(n=5) for x in range( iter )] )
    return '-'.join( [ getRandomKeysAndStr(n=5) for x in range( iter )] )


def pingAddress( address ) : 
    """
    Check if a network address is reachable.
    
    Args:
        address (str): IP address or hostname to ping.
    
    Returns:
        bool: True if address is reachable, False otherwise.
    """
    try :
        trustedAddresses = ['127.0.0.1' , 'localhost']
        if address in trustedAddresses :
            return True
        response  = ping3.ping(f'{address}')
        if not response :
            return False
        else :
            return True
    except Exception : 
        return False

def getScriptDir(f= __file__):
    """
    Get the directory path of the current script, handling PyInstaller bundled applications.
    
    Args:
        f (str): Path to the current file. Default is __file__.
    
    Returns:
        str: Directory path of the current script.
    """
    if getattr(sys, 'frozen', False): 
        # The script is run from a bundled exe via PyInstaller
        path = sys._MEIPASS 
    else:
        # The script is run as a standard script
        path = os.path.dirname(os.path.abspath(f))
    return path

def getScriptDirInMachine(f= __file__):
    """
    Get the absolute directory path of the current script.
    
    Args:
        f (str): Path to the current file. Default is __file__.
    
    Returns:
        str: Absolute directory path of the current script.
    """
    return os.path.dirname(os.path.abspath(f))



def is_packed():
    """
    Check if the script is running from a PyInstaller bundled executable.
    
    Returns:
        bool: True if running from a PyInstaller bundle, False otherwise.
    """
    # Check if the script is running from an executable produced by PyInstaller
    if getattr(sys, 'frozen', False):
        return True
    # Check if the 'bundle' directory exists
    elif hasattr(sys, '_MEIPASS') and os.path.exists(os.path.join(sys._MEIPASS, 'bundle')):
        return True
    else:
        return False

def get_executable_path(file=__file__) :
    """
    Get the path of the executable or script.
    
    Args:
        file (str): Path to the current file. Default is __file__.
    
    Returns:
        str: Path to the executable or script.
    """
    if is_packed():
        return os.path.dirname(os.path.realpath(sys.argv[0]))
    return os.path.dirname(os.path.realpath(file))

def isArgsEmpty(args) :
    """
    Check if all values in an argparse Namespace are False.
    
    Args:
        args: argparse.Namespace object to check.
    
    Returns:
        bool: True if all values are False, False otherwise.
    """
    if True in args.__dict__.values() :
        return False
    else :
        return True
    
def convert_bytes_to_mb(bytes_size, rounded=True):
    """
    Convert bytes to megabytes.
    
    Args:
        bytes_size (int/float): Size in bytes to convert.
        rounded (bool): If True, rounds the result to nearest integer.
    
    Returns:
        float/int: Size in megabytes.
    """
    if rounded :
        # print(f'''
        # {bytes_size} =>>> {round(float(bytes_size))}
        # ''')
        return round(float(bytes_size / (1024 * 1024)))
    return bytes_size / (1024 * 1024)

def convert_bytes_to_kb(bytes_size, rounded=True):
    """
    Convert bytes to kilobytes.
    
    Args:
        bytes_size (int/float): Size in bytes to convert.
        rounded (bool): If True, rounds the result to nearest integer.
    
    Returns:
        float/int: Size in kilobytes.
    """
    if rounded :
        return round(float(bytes_size / 1024))
    return bytes_size / 1024

def convert_mb_to_bytes(mb_size):
    """
    Convert megabytes to bytes.
    
    Args:
        mb_size (int/float): Size in megabytes to convert.
    
    Returns:
        int/float: Size in bytes.
    """
    return mb_size * 1024 * 1024

def getTimestamp(after_seconds=None, epoch=False) :
    """
    Get current timestamp or timestamp after specified seconds.
    
    Args:
        after_seconds (int): Number of seconds to add to current time.
        epoch (bool): If True, returns timestamp in milliseconds.
    
    Returns:
        int: Unix timestamp in seconds or milliseconds.
    """
    '''
    get timestamp now or after few seconds.
    after_seconds is int.
    '''
    if not after_seconds :
        if epoch :
            return int(time.time()) * 1000
        return int(time.time())
    if epoch :
        return (int(time.time())  + int(after_seconds) ) * 1000  
    return int(time.time()) + int(after_seconds)

def kill_thread(thread):
    """
    Forcefully terminate a running thread.
    
    Args:
        thread (threading.Thread): Thread object to terminate.
    
    Note:
        Use with caution as this can lead to resource leaks and inconsistent state.
    """
    """
    thread: a threading.Thread object
    """
    thread_id = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        
def start_thread(target, args=(), kwargs=None, daemon=True,auto_start=True):
    """
    Start a new thread with specified target function and arguments.
    
    Args:
        target (callable): Function to run in the new thread.
        args (tuple): Positional arguments for the target function.
        kwargs (dict): Keyword arguments for the target function.
        daemon (bool): If True, thread will be a daemon thread.
    
    Returns:
        threading.Thread: Started thread object.
    """
    if kwargs is None:
        kwargs = {}
    th = threading.Thread(target=target, args=args, kwargs=kwargs)
    th.daemon = daemon
    if auto_start :
        th.start()
    return th


def pagination(data , iter=25 , base_url=None) :
    """
    Create pagination for a list of data.
    
    Args:
        data (list): List of items to paginate.
        iter (int): Number of items per page. Default is 25.
        base_url (str): Base URL for pagination links.
    
    Returns:
        tuple: (base_url, paginated_data, total_pages)
    """
    total_pages = math.ceil(len(data) / iter)
    paginated_data = {}
    token=generateToken()
    if not base_url :
        base_url=f'/pagination/{token}'
    for page_number in range(1, total_pages + 1):
        start_index = (page_number - 1) * iter
        end_index = min(start_index + iter, len(data))
        paginated_data[page_number] = {
            'url' : f"{base_url}/{page_number}" ,
            'data' : data[start_index:end_index] ,
            'page' : page_number
        }
    return base_url , paginated_data , len(paginated_data)

def lget(list , index , default=None) :
    """
    Safely get an item from a list by index, similar to dict.get().
    
    Args:
        list: List to get item from.
        index: Index of item to get.
        default: Default value to return if index is out of range.
    
    Returns:
        Item at specified index or default value if index is out of range.
    """
    '''
    this is same as what we have in dict.get , get the index of exists, else will return a default value.'''
    try :
        return list[index]
    except :
        return default

def mkdirs(path) :
    """
    Create directory and all necessary parent directories.
    
    Args:
        path (str): Path of directory to create.
    """
    if not os.path.exists(path) :
        os.makedirs(path)

def releasify(release : float ) -> tuple :
    """
    Convert a release number into major and minor version numbers.
    
    Args:
        release (float): Release number (e.g., 1.2).
    
    Returns:
        tuple: (major_version, minor_version)
    """
    return (int(release), int(str(release).split(".")[1]))

def convertTimestampToDate(timestamp, return_date_time_object=False) :
    """
    Convert Unix timestamp to readable date and time.
    
    Args:
        timestamp (int): Unix timestamp to convert.
        return_date_time_object (bool): If True, returns datetime object instead of string.
    
    Returns:
        str or datetime: Formatted date and time.
    """
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    if return_date_time_object :
        return dt_object
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

def generateJwtToken() :
    """
    Generate a JWT token with timestamp and random value.
    
    Returns:
        str: Generated JWT token.
    """
    return jwt.encode({'timestamp' : getTimestamp() , 'r' : getRandomKey() }, getRandomKey(), algorithm="HS256")

def getMachineUuid() :
    """
    Get the machine's unique identifier (UUID).
    
    Returns:
        str: Machine UUID or empty string if not available.
    """
    if 'win' in sys.platform :
        cli = fr'reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductID'
        return str(subprocess.getoutput(cli).splitlines()[2].split(' ')[-1].replace('\n',''))
    elif 'linux' in str(sys.platform) :
        return str(subprocess.getoutput('cat /sys/class/dmi/id/product_uuid').replace('\n' , ''))
    else :
        return ''

def getMachineAddresses() :
    """
    Get all IP addresses associated with the machine.
    
    Returns:
        list: List of IP addresses.
    """
    ip_addresses = socket.gethostbyname_ex(socket.gethostname())[2]
    return ip_addresses

if __name__ == "__main__":
    pass
