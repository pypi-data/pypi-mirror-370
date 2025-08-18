
class NetworkElementNotReachable(Exception) :
    def __init__(self ,message='Network Element Is Not Reachable.'):
        super().__init__(message)

class NetworkElementConnectionFailure(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class InvalidRemoteEcIp(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class NotValid1830PssConnectionMode(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)
        
class StandbyEcConnectionModeNotSupported(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)
        
class PssNodeException(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class JumpServerConnectionFailure(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class NoActiveEC(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class CliAuthenticationFailure(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class InsufficientPermissions(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class SSHShellError(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class PssPasswordChangeError(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class GmreFailure(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)

class PSSError(Exception) :
    def __init__(self ,message=''):
        super().__init__(message)