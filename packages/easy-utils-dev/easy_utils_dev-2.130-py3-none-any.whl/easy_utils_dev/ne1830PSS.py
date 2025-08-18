# This script is used to collect data from Nokia 1830PSS WDM
# update on 15-12-2022 : 10:53

import traceback
import paramiko , csv 
from time import sleep
from datetime import datetime
from easy_utils_dev.debugger import DEBUGGER
from easy_utils_dev.encryptor import initCryptor
from easy_utils_dev.utils import pingAddress , lget , getTimestamp
from easy_utils_dev import exceptions


class PSS1830 :
    def __init__(self , sim=False , debug_name='Auto1830PSS' , auto_enable_tcp_forward=False,file_name=None,debug_home_path=None ) -> None:
        self.port = None
        self.logger = DEBUGGER(debug_name,file_name=file_name, homePath=debug_home_path)
        self.connected = False
        self.channel = None
        self.nodeName = None
        self.prompt = None
        self.encryptor = initCryptor(True)
        self.TIMEOUT = 15
        self.isjumpserver = False
        self.jumpserver = {}
        self.sim = sim
        self.nodePrompt=None
        self.prevJhostMemLocation=None
        self.jump_channel=None
        self.sshHostname=None
        self.jumpServerInSameInstance  = False
        self.requireAknow=None
        self.gmre = False
        self.isGmreLogin=False
        self.gmrePrompt=None
        self.connectionMethod=None
        self.jump_transport=None
        self.lastPrompt=None
        self.full_buffer=''
        self.pssRelease = None
        self.maxConnectAttempt=3
        self.connect_to_standby_ec=False
        self.currentConnectAttempt=0
        self.auto_enable_tcp_forward=auto_enable_tcp_forward
        self.tcpForwardStatus=None
        self.resetRequired = False
        self.screenBuffer = ""
        self.main_controller_client : paramiko.SSHClient = None
        self.standby_controller_client : paramiko.SSHClient = None
        self.create_jumphost = self.nfmtJumpServer
        if self.auto_enable_tcp_forward :
            self.logger.info(f'***WARNING*** : Auto enable tcp forwarding is enabled. This will allow tcp fowarding in target machine then restarting sshd service agent.')
        
    def createClient(self) :
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client
    

    def set_debug_level( self , level ) :
        self.logger.set_level(level)
        if level == 'debug' :
            self._change_paramiko_debug

    def nfmtJumpServer(self, ip , usr , pw , port=22  ) :
        self.logger.info(f"""ssh to jump-host -> address={ip}""")
        # print(f"this function will be deperecated soon. use create_jumphost() instead.")
        try :
            self.jumpServerInSameInstance = True
            self.jumpserver  = self.createClient()
            self.logger.info(f'connecting to jump-host with {usr}@{ip} port=[{self.port}] ..')
            self.jumpserver.connect(ip , port , usr , pw )
            self.isjumpserver = True
            self.nfmtip = ip 
            self.nfmtsshuser = usr
            self.nfmtsshpw = pw
            self.logger.debug(f"""check if tcpfowarding is allowed or not .. """)
            isEnabled , result  = self.checkIfTcpForwardingEnabled()
            self.logger.debug(f"""check if tcpfowarding is allowed or not. Result : {result}""")
            if not isEnabled :
                self.logger.debug(f"""check if tcpfowarding is allowed or not. result is disallowed. fixing .. """)
                self.fixTcpSSH()
                self.jumpserver.close()
                self.logger.debug(f"""re-establish the connection after modifying the sshd file and restarting the sshd service ..""")
                self.jumpserver  = self.createClient()
                self.jumpserver.connect(ip  , port , usr , pw , banner_timeout=200 , timeout=200, auth_timeout=200)
            self.logger.info(f"""connecting to jump-host [{ip}] - connected""")
            self.connected = True
            self.jumpserver.nfmtip = ip
            self.jumpserver.address = ip
            self.jumpserver.username = usr
            self.jumpserver.password = pw
            return self.jumpserver
        except Exception as error:
            self.logger.debug(f"""connecting to jump-host [{ip}] - failed \n\terror={error} \n\ttraceback={traceback.format_exc()}""") 
            self.logger.error(f"""connecting to jump-host [{ip}] - failed [more details in debug] [force exit with status code -1] error={error}""") 
            raise exceptions.JumpServerConnectionFailure(f"connection failure at address : {ip}")

    def _change_paramiko_debug(self) :
        import logging
        # Set up Paramiko logging
        logging.basicConfig(level=logging.DEBUG)  # This affects all loggers
        logger = logging.getLogger("paramiko")
        logger.setLevel(logging.DEBUG)

    def getTcpForwardStatus(self) :
        status , result = self.checkIfTcpForwardingEnabled()
        self.tcpForwardStatus= status
        return self.tcpForwardStatus

    def fixTcpSSH(self) :
        self.tcpForwardStatus = 'disabled'
        if not self.auto_enable_tcp_forward :
            return
        self.logger.info(f"""Enabling TCP forwarding on target machine ..""")
        status , result = self.checkIfTcpForwardingEnabled()
        self.logger.debug(f"""Current AllowTcpForwarding result = {result}""") 
        cli1 = f"sed -i 's/#AllowTcpForwarding yes/AllowTcpForwarding yes/g' /etc/ssh/sshd_config"
        cli2 = "sed -i 's/#AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config"
        cli3 = "sed -i 's/AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config "
        self.logger.debug(f'executing {cli1}')
        self.logger.debug(f'executing {cli2}')
        self.logger.debug(f'executing {cli3}')
        self.jumpserver.exec_command(f"{cli1} ; {cli2} ; {cli3} ; service sshd restart")
        self.logger.debug('executing fixtcpforward commands are done. service ssh restart also done.')
        self.logger.debug('checking again the status of tcp forward status after executing fix commands.')
        status , result = self.checkIfTcpForwardingEnabled()
        self.logger.debug(f"""Tcp Forward Fix process completed. AllowTcpForwarding result  = {result}""") 

    def rollbackTcp(self) :
        self.logger.info(f"""fixing tcp disable tcpforwarding .. """)
        stdin, stdout, stderr = self.jumpserver.exec_command("cat /etc/ssh/sshd_config | grep -i AllowTcpForwarding")
        result = stdout.read()
        self.logger.debug(f"""Current AllowTcpForwarding result = {result}""") 
        cli1 = f"sed -i 's/AllowTcpForwarding yes/#AllowTcpForwarding no/g' /etc/ssh/sshd_config"
        cli2 = "sed -i 's/#AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config"
        cli3 = "sed -i 's/AllowTcpForwarding yes/AllowTcpForwarding no/g' /etc/ssh/sshd_config "
        self.logger.debug(f'executing {cli1}')
        self.logger.debug(f'executing {cli2}')
        self.logger.debug(f'executing {cli3}')
        self.jumpserver.exec_command(f"{cli1} ; {cli2} ; {cli3} ; service sshd restart")
        self.logger.debug('executing rollback fixtcpforward commands are done. service ssh restart also done.')
        self.logger.debug('checking again the status of tcp forward status after executing rollback commands.')
        status , result = self.checkIfTcpForwardingEnabled()
        self.logger.debug(f"""Tcp Forward rollback process completed. AllowTcpForwarding result  = {result}""") 

    def checkIfTcpForwardingEnabled(self) :
        """check if port forwarding is enabled in linux machine
        returns True : if it is enabled. as boolean
        returns False : if it is not enabled. as boolean
        returns None : if it cannot be determined. as None
        returns the result as string 
        """
        cli = f'''sshd -T | grep -i  allowtcpforwarding'''
        self.logger.debug(f'executing {cli} to check the tcp forwarding if enabled or not ...')
        ssh = self.jumpserver
        result = self.ssh_execute( ssh , cli )
        self.logger.debug(f'result in checkIfTcpForwardingEnabled is {result}')
        if 'no' in result.lower() :
            self.logger.warning("Tcp Forwarding is disabled on the remote jump server host.")
            self.logger.debug(f'allowtcpforwarding is no, returning False ')
            return False, result
        elif 'yes' in result.lower() :
            self.logger.debug(f'allowtcpforwarding is yes, returning True ')
            return True , result
        else :
            self.logger.error(f'allowtcpforwarding is not returning yes or no. maybe configuration is not correct.')
            return None , result

    def enter_login_prompt(self) :
        self.logger.debug("enter_login_prompt Started ..")
        isUsernameOk = False
        isPasswordOk = False
        for i in range(10) :
            sleep(.5)
            new_data = self.channel.recv(4096).decode('utf-8')
            self.logger.debug(f"Enter Login Prompt is waiting the UserName input buffer: {new_data}")
            if 'No Active ECs'.lower() in str(new_data).lower()  :
                raise exceptions.NoActiveEC(f"No Active ECs found in {self.neip}")
            if ("Username:") in str(new_data) : 
                self.logger.debug(f"tool will enter {self.cliUser} to username field.")
                self.channel.sendall(self.cliUser + '\n')
                isUsernameOk = True
                break
        if not isUsernameOk :
            raise exceptions.CliAuthenticationFailure(f"Username {self.cliUser} is not found in the login prompt.")
        for i in range(10) :
            sleep(.5)
            if self.resetRequired and self.tmpPassword:
                cliPw = self.tmpPassword
            else:
                cliPw = self.cliPw
            new_data = self.channel.recv(4096).decode('utf-8')
            self.logger.debug(f"Enter Login Prompt is waiting the Password input: {new_data}")
            if ("password:") in str(new_data).lower() : 
                self.channel.sendall(cliPw + '\n')
                isPasswordOk = True
                break
            if ("authentication failed") in str(new_data).lower() : 
                raise exceptions.CliAuthenticationFailure(str(new_data))
        if not isPasswordOk :
            raise exceptions.CliAuthenticationFailure(f"Password {self.cliPw} is not found in the login prompt.")
        if self.resetRequired:
            self.newUserPwdReset()
            sleep(1)
        return True

    def determine_prompt(self) :
        for i in range(30) :
            sleep(.5)
            if self.resetRequired :
                new_data = self.full_buffer
            else :
                new_data = self.channel.recv(4096).decode('utf-8')
            self.logger.debug(f"Determine prompt full buffer is '{new_data}'")
            if 'authentication failed' in str(new_data).lower() :
                self.logger.error(f"Authentication failed {self.neip}")
                raise exceptions.CliAuthenticationFailure('Password authentication failed')
            if ("acknowledge") in str(new_data).lower() : 
                self.channel.sendall('yes' + '\n')
                sleep(.5)
                continue
            if "#" in new_data :
                new_data = new_data.split('\n')
                self.prompt = new_data[-1]
                self.nodePrompt = self.prompt
                self.logger.debug('prompt detected => '+self.prompt)
                self.nodeName = self.prompt.replace('#' , '')
                if self.auto_disable_paging :
                    self.disable_paging()
                return True

    def get_main_controller_client(self) :
        return self.main_controller_client
    
    def get_standby_controller_client(self) :
        return self.standby_controller_client

    def ssh_execute(self , ssh=None , command='' ,  merge_output=False , hide_output=False , supress_error=True ) :
        self.logger.debug(f"executing {command}")
        if not ssh :
            ssh = self.client
        try :
            stdin_ , stdout_ , stderr_ = ssh.exec_command(command)
            r = stdout_.read().decode()
            e = stderr_.read().decode()
            if r.endswith('\n') :
                r = r[ : -1]
            if hide_output : 
                self.logger.debug(f""" 
                =========================
                +command = '{command}'
                -stdout = {r}
                -stderr = {e}
                =========================
                """)
            else :
                self.logger.debug(f""" 
                =========================
                +command = '{command}'
                -stdout = {r}
                -stderr = {e}
                =========================
                """)
            if not supress_error :
                if e :
                    raise exceptions.SSHShellError(e)
            if merge_output :
                return str(r) + str(e)
            return r 
        except Exception as error :
            self.logger.error(f'failure in command {command} with error {error}')
            self.logger.debug(f'execution failure \n\tcommand={command} \n\terror={error} \n\rtraceback={traceback.format_exc()}')
            if not supress_error :
                raise exceptions.SSHShellError(error)
            return str(error)
 
    def deleteUser(self , affectedUsername) :
        self.logger.info(f'Deleting username {affectedUsername}')
        userProfile = self.getUser(affectedUsername)
        self.logger.info(f'user brief is {userProfile}')
        if not userProfile.get('username') :
            self.logger.info(f"Warnning : {affectedUsername} DID NOT found in NE Users list. Skip Deletion")
            return ''
        group = userProfile['group']
        if group != 'administrator' :
            self.logger.error(f"User {affectedUsername} is not admin user. it is {group}")
            raise exceptions.InsufficientPermissions(f"User {affectedUsername} is not admin user. it is {group}")
        cli = f'config admin user delete {affectedUsername}'
        result = self.cli_execute(cli)
        self.logger.debug(f'user deleted with buffer resutn {result}')
        return result

    def changePassword(self,username,newPassword) :
        # self.logger.set_level('debug')
        self.logger.info(f'Changing password ...')
        userProfile = self.getUser(username)
        self.logger.info(f'user brief are {userProfile}')
        group = userProfile['group']
        if group != 'administrator' :
            self.logger.error(f"User {username} is not admin user. it is {group}")
            raise exceptions.InsufficientPermissions(f"User {username} is not admin user. it is {group}")
        cli = f'config admin users edit {username} passwd force'
        self.cli_execute(cli , expect='password')
        sleep(.5)
        if self.cliUser != username :
            self.cli_execute("Nokia@20981" , expect='password' , ifPassword=True )
            sleep(.5)
            self.cli_execute("Nokia@20981" , expect='password' , ifPassword=True )
            pss = PSS1830(self.sim)
            if self.logger.currentDebugLevel == 'debug' :
                pss.set_debug_level('debug')
            pss.connect(self.mode , neip=self.neip , user=username , pw=newPassword , rootpw=self.rootPw , jumpserver=self.jumpserver , resetRequired=True,tmpPassword="Nokia@20981")
            pss.disconnect()
        else :
            self.cli_execute(self.cliPw , expect='password' , ifPassword=True )
            sleep(.5)
            self.cli_execute(newPassword , expect='password' , ifPassword=True )
            sleep(.5)
            result = self.cli_execute(newPassword , expect='password' , ifPassword=True )
            return result  

    def newUserPwdReset(self):
        self.logger.debug(f'Changing Password for the Newely Created User')
        for i in range(30) :
            self.logger.debug(f"Try {i}/30 to change the password on login ..")
            sleep(1)
            new_data = self.channel.recv(4096).decode('utf-8')
            self.logger.debug(f"buffer in newUserPwdReset : {new_data}")
            if "Change Password Now" in new_data :
                new_data = new_data.split('\n')
                self.logger.debug(f'Prompt for Password Change is: {new_data}')
                self.logger.debug(f"Tool will enter new password for try 1 ")
                self.cli_execute(self.cliPw, ifPassword=True,wait=False)
                sleep(1)
                self.logger.debug(f"Tool will enter new password for try 2")
                self.cli_execute(self.cliPw, ifPassword=True,wait=False)
                sleep(1)
                break
        d= self.buffer()
        self.logger.debug(f'changing password should be done, buffer is {d}')
        if 'Error:' in d:
            errorStr = ''
            for line in d.splitlines() :
                if 'Error' in line :
                    errorStr = line
                    break
            self.logger.error(f"Password Change Failed due to Error: {errorStr}")
            raise exceptions.PssPasswordChangeError(f"Password Change Failed due to Error: {errorStr}")
        return d

    def loginToGmre(self) :
        self.logger.debug(f"login to gmre started ...")
        self.cli_execute('tools gmre_cli' , wait=True , error="telnet: gmremgmt: Name or service not known" , errorMessage=f"No GMRE Activated on {self.neip}" , expect='username')
        self.logger.debug('tool will enter gmre username ..')
        pw = self.encryptor.dec_base64('Z21yZQ==')
        self.cli_execute( pw , wait=True , expect='password')
        self.logger.debug('tool will enter gmre password ..')
        response = self.cli_execute( pw , expect='#' , return_untouched_buffer=True).splitlines()
        self.logger.debug(f'gmre first login response is {response}')
        response = [ line for line in response if line != '']
        self.logger.debug(f'gmre response after clearing empty cells {response}')
        self.gmrePrompt = None
        nodeName = self.prompt.lower().replace('#' , '') .replace(' ' , '').replace('\n', '')
        self.logger.debug(f"checking if {nodeName} in the returned buffer or not ...")
        for item in response :
            item = str(item).replace(' ' , '')
            self.logger.debug(f"checking if '{nodeName}' and '#' in item='{item.lower()}' ...")
            if str(item).find('#')  != -1 :
                self.logger.debug(f"gmre.prompt detected in {item}")
                self.gmrePrompt = item.split('[')[0]
                break
        if not self.gmrePrompt :
            self.logger.error(f"couldn't catch the gmre.prompt. check debug logs.")
            raise exceptions.GmreFailure(f"couldn't catch the gmre.prompt. check debug logs.")
        self.lastPrompt = self.prompt
        self.prompt = self.gmrePrompt
        self.logger.debug(f'gmrePrompt={self.gmrePrompt}')
        self.gmre=True
        self.isGmreLogin= True
        self.logger.debug(f'stop the gmre notifications ..')
        self.cli_execute( command='set notification off' , wait=False)
        sleep(1)
        self.clear_buffer(1,force=True,timeout=5)
        self.logger.debug(f"login to gmre completed.")

    def getGmreInformation(self) :
        self.logger.info(f'getting gmre node details')
        result = self.cli_execute('show node').splitlines()
        data= {}
        for line in result :
            if ': ' in line :
                key = line.split(': ')[0].replace(' ' , '')
                value = line.replace(key , '').replace(': ' , '').replace('\n' , '').lstrip()
                data[key] = value
                self.logger.debug(f'adding {key}={value}')
        return data

    def checkPinngableFromParamiko(self,neip,ssh) :
        pingCommand = f'''ping {neip} -c 3 | grep -i '100%' '''
        self.logger.debug(f'checkPinngableFromParamiko: checking node reachability using {pingCommand}')
        stdin, stdout, stderr = ssh.exec_command(pingCommand)
        result = stdout.read().decode("utf-8").replace("\n", "")
        self.logger.debug(f'checkPinngableFromParamiko: checking node reachability using {pingCommand} result={result}')
        if '100%' in result :
            self.logger.debug(f"checkPinngableFromParamiko: Network Element {neip} is NOT reachable.")
            return False
        else :
            self.logger.debug(f"checkPinngableFromParamiko: Network Element {neip} is reachable.")
            return True

    def activateGmreRelease(self , release ) :
        self.logger.info(f'Warning:- activateGmreRelease {release}')
        if  release.count('.') < 2 :
            self.logger.error(f'Wrong GMRE release. GMRE release must be like so XX.YY.ZZ or XX.YY.Z')
            raise exceptions.GmreFailure('Wrong GMRE release format.')
        cli = f"config node activenetworkversion {release}"
        self.logger.debug(f'activating gmre release using {cli}')
        result = self.cli_execute(cli)
        self.logger.debug(f'activating gmre release using {cli} result={result}')
        if 'unsuccessfully configured' in result.lower() :
            raise exceptions.GmreFailure(f'Network Element {self.neip} activation failed. due to {result}')
        if not 'successfully configured' in result.lower() :
            raise exceptions.GmreFailure(f'Network Element {self.neip} activation failed. due to {result}')


    def verify_node_reachability(self , neip ) :
        self.logger.debug(f"verify_node_reachability from jhost={self.isjumpserver}")
        if  self.isjumpserver == False :
            if not pingAddress(neip) :
                self.logger.error(f"Network Element {neip} is not reachable. PingResult=False")
                raise exceptions.NetworkElementNotReachable(f'Network Element Address : {neip}')
            else :
                self.logger.debug(f"Network Element {neip} not reachable. PingResult=True")
        elif self.isjumpserver :
            if not self.checkPinngableFromParamiko(neip , self.jumpserver) :
                raise exceptions.NetworkElementNotReachable(f'Network Element Address : {neip}')
            
    def close_ssh(self, ssh=None) :
        if not ssh :
            ssh = self.client
        try :
            ssh.close()
        except Exception as error:
            self.logger.error(f"[ignore] - ssh closure error : {error}")
            pass
        try :
            if self.jump_channel :
                self.jump_channel.close()
        except Exception as error:
            self.logger.error(f"[ignore] - jump_channel closure error : {error}")
            pass

    def createJhostInstance(self , neip , port) :
        if self.isjumpserver :
            self.logger.debug(f'creating new transport for jhost ...')
            if (self.prevJhostMemLocation != self.jumpserver) and self.prevJhostMemLocation :
                self.logger.debug(f'new jhost detected with memory-location: {self.prevJhostMemLocation}')
            jump_transport= self.jump_transport = self.jumpserver.get_transport()
            src_addr = ( self.nfmtip , 22 )
            dest_addr = ( neip , port )
            jump_channel = self.jump_channel = jump_transport.open_channel("direct-tcpip", dest_addr, src_addr, timeout=30)
            self.prevJhostMemLocation=self.jumpserver
            self.logger.debug(f'creating new transport for jhost completed')
            return jump_channel
        return None

    def switch_to_standby_ec(self) :
        if self.connect_to_standby_ec : 
            self.logger.info(f"connecting to standby EC {self.neip} ...")
            if not self.sim :
                response = self.ssh_execute(ssh=self.client , command=f"ifconfig ilan | awk '/inet / {{print $2}}'")
                if not response :
                    raise exceptions.InvalidRemoteEcIp(f"couldn't connect to remote EC")
            if self.sim :
                response = "100.0.81.1"
            if response :
                current_ec_ip = response.replace('\n' , '')
                switcher = {
                    '100.0.81.1' : '100.0.81.18',
                    '100.0.81.18' : '100.0.81.1',
                }
                remote_ec_ip = switcher.get(current_ec_ip)
                if not remote_ec_ip :
                    self.logger.error(f"couldn't find the standby EC IP for {current_ec_ip}")
                    raise exceptions.InvalidRemoteEcIp(f"couldn't find the standby EC IP for {current_ec_ip}")
                jump_transport = self.client.get_transport()
                dest_addr = ( remote_ec_ip , 5122 )
                local_addr = ( current_ec_ip , 5122 )  # dummy source addre ss
                channel = jump_transport.open_channel('direct-tcpip', dest_addr, local_addr)
                client = self.createClient()
                client.connect( self.neip , 5122 , "root" , self.rootPw , sock=channel )
                self.client = client
                self.logger.debug(f"switching to standby EC {remote_ec_ip} completed")
                return client

    def port_switcher( self , mode ) :
        if mode == 'direct_cli' or self.sim:
            port = 22
        else:
            port = 5122
            if mode in ('cli', 'ssh'):
                port = 5122
        return port

    def _connect(self , mode='cli' , neip=None , rootpw='QUx1MTIj') :
        self.client = self.createClient()
        port = self.port_switcher(mode)
        try :
            jhostserver = self.createJhostInstance(neip , port)
            self.verify_node_reachability(neip)
            ok = False
            self.logger.debug(f"connecting to {neip} with mode={mode} and port={port}")
            if mode == 'direct_cli' :
                self.client.connect(neip , port , "cli" , '' , sock=jhostserver)
                ok = True
            elif mode == 'cli' or mode == 'ssh' :
                self.client.connect( neip , port , "root" , rootpw ,  sock=jhostserver )
                ok = True
            self.logger.debug(f"client={self.client} ok={ok} port={port} mode={mode}")
            # lets switchj to standby ec if needed
            if ok and self.connect_to_standby_ec:
                self.main_controller_client = self.client
                self.standby_controller_client = self.switch_to_standby_ec()
        except Exception as error :
            self.logger.debug(f'error during connecting to {self.neip} \n\t error={error} \n\t traceback={traceback.format_exc()}')
            if 'Authentication failed' in str(error) :
                return self.client , "AUTH_FAIL" , False
            self.logger.debug(f'Error connecting to {self.neip} as mode={mode} while jumpserver is disabled. Error={error}')
            self.logger.debug(traceback.format_exc() , source=self.neip)
            self.connected=False
            self.close_ssh(self.client)
            return self.client , error, False
        
        self.logger.debug(f"building the initial connection to {neip} success. return now")
        # return client , error , isConnected
        return self.client , '' , True

    def connect(self ,
            mode='cli' , 
            neip=None , 
            user=None , 
            pw=None , 
            rootpw=None,
            jumpserver = None , 
            resetRequired = False, 
            tmpPassword = None , 
            maxReconnectAttemp=3,
            auto_disable_paging=True, 
            return_channel=False ,
            connect_to_standby_ec=False,
        ) :
        if not user :
            user = 'admin'
        if not pw :
            pw = 'YWRtaW4='
        if not rootpw :
            rootpw = 'QUx1MTIj'
        if mode not in ['cli' , 'ssh' , 'direct_cli'] :
            raise exceptions.NotValid1830PssConnectionMode(f'mode {mode} is not a valid input')
        if pw == 'YWRtaW4=' :
            self.logger.debug(f"pw specified is obfuscated. Switch to plain text ...")
            pw = self.encryptor.dec_base64(pw)
            self.logger.debug(f"pw specified is obfuscated. Switch to plain text result {pw}")
        if rootpw == 'QUx1MTIj' :
            self.logger.debug(f"rootpw specified is obfuscated. Switch to plain text ...")
            rootpw = self.encryptor.dec_base64(rootpw)
            self.logger.debug(f"pw specified is obfuscated. Switch to plain text result {rootpw}")
        self.logger.debug(f'Opening SSH  connection to NE {neip} mode={mode}, resetRequired={resetRequired}')
        self.cliUser = user
        self.mode = mode
        self.cliPw = pw
        self.neip= neip
        self.rootPw = rootpw
        self.resetRequired = resetRequired
        self.tmpPassword = tmpPassword
        self.auto_disable_paging = auto_disable_paging
        self.connect_to_standby_ec = connect_to_standby_ec
        self.logger.debug(f"""
            --------------------------------------------------------
            mode={mode}
            neip={neip}
            user={user}
            pw={pw}
            rootpw={rootpw}
            resetRequired={resetRequired}
            tmpPassword={tmpPassword}
            auto_disable_paging={auto_disable_paging}
            connect_to_standby_ec={connect_to_standby_ec}
            return_channel={return_channel}
            sim={self.sim}
            --------------------------------------------------------
        """)
        if connect_to_standby_ec and mode != 'ssh' :
            self.logger.error(f"connect_to_standby_ec is only supported for ssh mode. since PSS CLI only valid on Active Controller")
            raise exceptions.StandbyEcConnectionModeNotSupported('connect_to_standby_ec is only supported for cli/ssh mode.')
        # another method is to inject the jumpserver inside the connect itself.
        if jumpserver != None  and self.jumpServerInSameInstance == False :
            self.isjumpserver = True
            self.jumpserver = jumpserver
            self.nfmtip = jumpserver.nfmtip 
            self.connected = True
        # self.verify_node_reachability(neip)
        self.maxConnectAttempt = maxAttemps = maxReconnectAttemp
        self.currentConnectAttempt=0
        for i in range(maxAttemps) :
            self.currentConnectAttempt += 1
            self.logger.info(f"try {self.currentConnectAttempt}/{maxAttemps} to connect to {neip} ...")
            self.client , error , status = self._connect(mode  , neip , rootpw)
            if error == "AUTH_FAIL" :
                raise exceptions.CliAuthenticationFailure(f"Authentication failure at {self.neip}")
            if self.currentConnectAttempt == self.maxConnectAttempt :
                self.logger.error(f'failed to cconnect to {self.neip}')
                raise exceptions.NetworkElementConnectionFailure(f'failed at {self.neip}')
            self.logger.debug(f"\n\tneip={neip}\n\tself.client={self.client} \n\terror='{error}' \n\tconnectionSuccess={status}")
            if status : 
                self.logger.info(f"connected to {neip} successfully")
                break
            sleep(5)
        self.connected=True
        self.logger.debug(f'''\n
        --------------------------------------------------------
                 Network Element - connected - {neip}
        ---------------------------------------------------------
        \n''')
        if mode == 'ssh' : 
            self.logger.debug(f"ssh mode detected. returning self.client object with no switch_to_cli_shell()")
            self.connected = True
            return self.client
        self.channel = self.switch_to_cli_shell()
        self.logger.debug(f'set timeout in rcv channel to {self.TIMEOUT}')
        self.channel.settimeout(self.TIMEOUT)
        self.start_cli_login_process()
        if return_channel :
            return self.client , self.channel
        return self.client
    
    def start_cli_login_process(self) :
        self.channel = self.switch_to_cli_shell()
        self.logger.debug(f'set timeout in rcv channel to {self.TIMEOUT}')
        self.channel.settimeout(self.TIMEOUT)
        if self.mode == 'cli' :
            self.logger.debug(f'mode cli detected. "su - cli" command will be executed to enter NE cli.')
            cmd = 'su - cli\n'
            self.channel.sendall(cmd)
            sleep(.1)
            self.logger.debug(f'switching user to cli mode completed.')
        self.logger.debug(f'Starting/Processing login window handler to enter username, password and aknowledge message if appears ...')
        self.enter_login_prompt()
        self.logger.debug(f'Starting/Processing to auto detect the NE prompt NE_NAME+# ...')
        self.determine_prompt()
        self.connected = True
        self.logger.debug(f'Processing handler to enter username, password completed. returning self.client object ')
        self.client.channel = self.channel
    
    def switch_to_cli_shell(self) :
        return self.client.invoke_shell()

    def get_neversion(self,supress_error=False,cache=True) :
        """
        retreive the NE version depending on connection mode
        if connection mode has ssh , this means cat /pureNeApp/EC/swVerInfoAscii will be executed
        if connection is direct, this means show version will be executed.
        to save time if cache is enabled. the last version will be returned.
        """
        self.logger.debug(f'Getting NE version..')

        if not self.client :
            self.logger.error('no client is available. are you sure client is connected?')
            if supress_error:
                return False , 0.0
            raise exceptions.PSSError(f'no active connection to {self.neip}')
        if self.pssRelease and cache :
            return True , self.get_version()
        if self.mode == 'cli' or self.mode == 'ssh ':
            cli = "cat /pureNeApp/EC/swVerInfoAscii"
            self.logger.debug(f'executing from get_neversion: {cli} for mode= {self.mode}')
            result = self.ssh_execute( self.client , cli ).replace('\n' , '')
        elif self.mode == 'direct_cli' :
            cli = 'show version'
            self.logger.debug(f'executing from get_neversion: {cli} for mode= {self.mode}')
            result = self.cli_execute(cli)
        if self.mode != 'ssh' :
            if not '1830pss' in result.lower() :
                if supress_error :
                    return False , 0.0
                self.logger.error(f'PSS release response is not valid or too short.')
                raise exceptions.PSSError(f'PSS release response is not valid or pss release value too short.')
        if self.mode != 'ssh' :
            self.logger.debug(f'received release response in get_neversion {result}')
            self.logger.debug(f'received release response in get_neversion length = {len(result)}')
            self.logger.debug(f'partitioning release response as - in result .. ')
            self.pssRelease = float(result.partition('-')[2].partition('-')[0])
            self.logger.debug(f'paritioned release response as float is {self.pssRelease}')
            self.logger.info(f'Network Element release is {self.pssRelease}')
        return True , self.pssRelease

    def disconnect(self) :
        self.logger.debug(f'Disconnecting from PSS ...')
        try :
            self.close_cliconnection()
        except :
            pass
        try :
            self.client.close()
        except :
            pass
        
        try :
            self.close_ssh()
        except :
            pass
        try :
            self.logger.close()
            del self.logger
        except :
            pass


    def disable_paging(self) :
        cli = f'paging status disable'
        self.cli_execute(cli)
        self.logger.debug('paging disabled.')

    def channels_report(self, exportCsv=False) :
        self.logger.info('Generating Channels Report .. ')
        channels = self.get_xcs()
        header = ['NE', 'shelf', 'slot', 'port' , 'powerRx' , "powerTx" , "channel" , "prefec"  ,"postFec" , "shape" , "phase" , "trackMode"]
        csvFpath = f"channels_report_{self.host}_{getTimestamp()}.csv"
        if exportCsv :        
            csvFile = open(csvFpath, 'w', encoding='UTF8' , newline='')
            csvFile = csv.writer(csvFile)
            csvFile.writerow(header)
        for channel in channels :
            otPort = None
            if not "LINE" in channel['aEnd'].upper() : otPort = channel['aEnd']
            if not "LINE" in channel['zEnd'].upper() : otPort = channel['zEnd']
            file = self.cli_execute(f"show interface {otPort} detail").splitlines()
            for line in file :
                breakIt = False 
                try :
                    nodeName = self.prompt.replace("#" , "")
                    if "Shelf:" in line :
                        details = line.split(": ")
                        shelf = details[1].replace(' Slot' , "")
                        slot = details[2].replace(' Port' , "")
                        port = details[3].split(' -')[0]
                    if "Received Power" in line :
                        powerRx = line.split(':')[1].split(" ")[1]
                    if "Transmitted Power" in line :
                        powerTx = line.split(':')[1].split(" ")[1]
                    if "Channel Tx   " in line :
                        channel = line.split(':')[1].split(" ")[1].replace('\n' , '')
                    if "pre" in line.lower() and 'fec' in line.lower() :
                        prefec = line.split(':')[1].split(" ")[1].replace('\n' , '')
                    if "post" in line.lower() and 'fec' in line.lower() :
                        postFec = line.split(':')[1].split(" ")[1].replace('\n' , '')
                    if "Txshape" in line :
                        shape = line.split(':')[1].split(" ")[1].replace('\n' , '')
                    if "Phase encoding Mode" in line :
                        phase = line.split(':')[1].split(" ")[1].replace('\n' , '')
                    if "TrackPolar" in line or "Track Polar" in line :
                        trackMode = line.split(':')[1].split(" ")[1].replace('\n' , '')
                        breakIt = True
                    if breakIt and  exportCsv :
                        output = f"{nodeName} => [ {shelf} / {slot} / {port}  ] {channel} => TX : {powerTx} ,  RX : {powerRx} prefec => {prefec}  "
                        data = [nodeName , shelf , slot , port , powerRx , powerTx , channel , prefec  ,postFec , shape , phase , trackMode]
                        csvFile.writerow(data)
                        self.logger.debug(output)
                except Exception as error:
                    self.logger.error(f'error [MAY SKIP/IGNORE] : {error}')
                    continue
        self.logger.info('Generating Channels Report Terminated. ')
            

    def cli_execute(self , command , wait=True ,ifPassword=False,expect=None,errorMessage=None,error=None,calc_execution_period=True, return_untouched_buffer=False) :
        '''
        cli_execute method is executing pss cli commands inside pss machines.\n
        command : example, show software upgrade status
        wait : default is True. if wait is False then cli_execute will not wait for command completion and will return immediately.
        ifPassword : hide the password logs.
        expect : expect keyword to return the result. the default expect is ne prompt
        errorMessage : the raised error message when error is found
        error :  expect errorkeyword to raise failure when found. the default error is Error keyword
        calc_execution_period :  flag to calculate how long the command took to execute and return result
        return_untouched_buffer :  return the buffer when expect keyword found without any beautification or manipulation.
        '''
        if not self.mode in ['cli' , 'direct_cli'] :
            raise exceptions.NotValid1830PssConnectionMode(f'This command require CLI connection.')
        if calc_execution_period :
            start = getTimestamp()
        if self.gmre and not self.isGmreLogin :
            self.logger.error(f"GMRE not logged in. No command will be executed gmre={self.gmre} isGmreLogin={self.isGmreLogin}")
            return ''
        if not self.connected :
            self.logger.warning(f"No action is allowed to execute. Connection is not established.")
            return
        self.logger.debug(f"Executing cli command '{command}'")
        self.channel.sendall(command + '\n')
        if not ifPassword :
            self.logger.debug('executing :'+command)
        if wait :
            result = self.wait_result(command=command , expect=expect, expectError=error,errorMessage=errorMessage,return_untouched_buffer=return_untouched_buffer)
            if calc_execution_period :
                execution = round(getTimestamp() - start , 1)
                self.logger.info(f'command="{command}" | completed in {execution}secs')
            return result
        
    def buffer(self,size=8096) :
        '''
        start channel.recv to return the buffer and fill it in a full buffer. then return the buffer. default size is 8096 bytes.\n
        @params\n
        size : size of the buffer in bytes.
        '''
        try :
            data= self.channel.recv(size).decode('utf-8')
            self.full_buffer += data
            return data
        except :
            return ''
    
    def config_backup_db_server(self , ip , user, password , protocol , path , backupname="BACKUP") :
        self.cli_execute(f'config database server ip {ip}')
        self.cli_execute(f'config database server protocol {protocol}')
        self.cli_execute(f'config database path {path}{backupname}')
        self.cli_execute(f'config database server userid {user}' , wait=False)
        sleep(.5)
        self.cli_execute(password, ifPassword=True)
  
    def config_swserver(self , ip , user, password , protocol , path ) :
        self.cli_execute(f'config software server ip {ip}')
        self.cli_execute(f'config software server protocol {protocol}')
        self.cli_execute(f'config software server root {path}')
        self.cli_execute(f'config software server userid {user}' , wait=False)
        sleep(.5)
        self.cli_execute(password , ifPassword=True)
  
    def backToCliRoot(self) :
        '''
        backToCliRoot = backMainMenu, same functionality with different function name for more meaningful function name.
        '''
        self.cli_execute('mm')
    
    def backMainMenu( self ) :
        self.backToCliRoot()

    def wait_result(self , command,expect,expectError=None,errorMessage=None,autoError = True,return_untouched_buffer=False,expects=[]) :
        data = ''
        start = False
        return_result = False
        catchedExpectedFromExepcts=None
        i=0
        self.logger.debug(f"""Waiting Results Params [Begin] :
                command={command}
                expect={expect}
                expects={expects}
                self.prompt={self.prompt}
                expectError={expectError}
                errorMessage={errorMessage}
                autoError={autoError}
                return_untouched_buffer={return_untouched_buffer}
            """)
        while True:
            sleep(.5)
            i+=1
            try :
                new_data = self.channel.recv(20000).decode('utf-8')
            except :
                new_data = None
            self.logger.debug(f"""Rcv full buffer: '{new_data}'""")
            if new_data :
                data += new_data   
                self.full_buffer += new_data   
                self.logger.debug(f"checking if any of the next statements are in the data ..\n\r -expect={str(expect)} or -prompt={self.prompt} in the data ...")
                if expect :
                    find1 = data.lower().find(expect.lower())
                else :
                    find1= -1
                if len(expects) != 0  :
                    for elem in expects :
                        find3 = data.lower().find(elem.lower())
                        if find3 != -1 :
                            self.logger.debug(f'expects are provided. found statement will be used as expect. catchedExpectedFromExepcts={elem}')
                            catchedExpectedFromExepcts=elem
                            break
                else :
                    find3=-1
                find2 = data.lower().find(self.prompt.lower())
                self.logger.debug(f"find statement find1: {find1} find2:{find2}")
                if( find1 != -1 ) or (find2 != -1) or (find3 != -1):   
                    self.logger.debug(f"Expected found. find1={find1} find2={find2} find3={find3}")
                    if return_untouched_buffer :
                        self.logger.debug(f"return_untouched_buffer is enabled. return the full buffer. => *{data}*")
                        return data
                    data2 = data.splitlines()   
                    return_data = ''
                    for line in data2 :
                        self.logger.debug(f'wait result will check the content of line "{line}"')
                        if expectError != None and str(expectError).lower() in line.lower(): 
                            self.logger.debug(f"expectError found in buffer. expectError={expectError} line={line}")
                            self.logger.debug(f"""wait_result failure details : 
                                command={command}
                                expect={expect}
                                errorMessage={errorMessage}
                                autoError={autoError}
                                line={line}
                            """)
                            if errorMessage :
                                raise exceptions.PssNodeException(errorMessage)
                            else :
                                raise exceptions.PssNodeException(f"{expectError}")
                        if autoError and 'error' in line.lower() or 'Login incorrect!' in line.lower():
                            self.logger.debug(f"""wait_result failure details : 
                                        command={command}
                                        expect={expect}
                                        errorMessage={errorMessage}
                                        autoError={autoError}
                                        line={line}<
                                        """)
                            raise exceptions.PssNodeException(f"{line}")
                        if command in line : 
                            self.logger.debug(f'wait result found command in {line}. skip this line and flag start to true')
                            start = True
                            continue
                        if start and not self.prompt in line and line != '' and command not in line :
                            self.logger.debug(f'wait_result: start flag is True and no expect in line')
                            return_data += line +'\n'
                        if expect :
                            if expect.lower() in line.lower() :
                                self.logger.debug(f"expect found in line [ignore start flag status ]")
                                return_result = True
                        if catchedExpectedFromExepcts  :
                            if catchedExpectedFromExepcts.lower() in line.lower() :
                                self.logger.debug(f"expect from expects expect={catchedExpectedFromExepcts} found in line [ignore start flag status ]")
                                return_result = True
                        elif self.prompt in line and start :
                            self.logger.debug(f"self.prompt found in line and start is set to True")
                            return_result = True
                        if return_result :
                            self.logger.debug(f'wait_result found "{self.prompt}" or "{expect}" in this line "{line}"')
                            self.logger.debug(f"""WAIT RESULT : return_data = "{return_data}" | END""")
                            self.logger.debug(f"""WAIT RESULT : command = "{command}" | END """)
                            return return_data
            else: 
                self.logger.debug(f'wait_result didnt find "{expect}" or {self.prompt} in the new data.')
                i += 1
                if i >= 10 :
                    self.logger.error(f"""Timout in WAIT_RESULT : {command}""")
                    raise exceptions.PSSError(f'wait result in buffer timedout in node {self.neip}')

    
    def get_allcards(self) : 
        self.logger.info("Getting all cards inventory .. ")
        cards = self.cli_execute('show slot *')
        self.logger.debug(f"Getting all cards inventory .. return {cards} ")
        cards = cards.splitlines()
        cards_return = {"all" : {} , "equipped" : {} , "unequipped" : {} }
        for key , line in enumerate(cards) : 
            try :
                if 'Slot' in line or 'Present Type' in line  or'see slot' in line or "Oper" in line or "------------" in line: 
                    continue
                _card_line = [x for x in line.split(' ') if x != '' ]
                if 'Empty' == _card_line[1] : continue
                self.logger.debug(f"get_allcards : line split .. return {_card_line} ")
                slotting = _card_line[0]
                cardType = _card_line[1]
                cards_return['all'][slotting] = {'card' : cardType , 'slot' : slotting , 'status' : _card_line[-1]}
                if "UEQ" in line :
                    cards_return['unequipped'][slotting] = {'card' : cardType , 'slot' : slotting ,  'status' : _card_line[-1] }
                else :
                    cards_return['equipped'][slotting] = {'card' : cardType , 'slot' : slotting ,  'status' : _card_line[-1] }
            except :
                continue
        self.logger.debug(f"get_allcards : final return {cards_return}")
        return cards_return  
            

    def get_xcs(self) :
        xcs = self.cli_execute('show xc *')
        xcs = xcs.splitlines()
        xcsList = []
        for _ , line in enumerate(xcs) : 
            if "A-End" in line or 'OCH Trail' in line or "Admin Oper" in line or "entries" in line or " "*20 in line or "------------" in line : 
                continue
            details = line.split('  ')
            details = [ i for i in details if i != "" ]
            if len(details) == 0 : 
                continue
            try :
                aEnd = details[0]
                zEnd = details[1]
                channel = details[2]
                connectionId = details[3]
                label = details[4]
                width = details[5]
                type = details[6]
                adminState = details[7]
                oper = details[8]
                dir = details[9]
            except :
                continue
            tmp = {'aEnd' : aEnd , 'zEnd' : zEnd , 'channel' : channel , "id" : connectionId ,
                   "label" : label , 'width' : width , "type" : type , "admin" : adminState , 
                   "operation" : oper , 'dir' : dir
                   }
            xcsList.append(tmp)
        return xcsList        
         
    def showShelf(self , shelfId=1) :
        self.logger.debug(f'show shelf for shelfId={shelfId}')
        cli= f'show shelf {shelfId}'
        result = self.cli_execute(command=cli).splitlines()
        for line in result :
            if 'Present Type' in line :
                shelfId=1
                shelfType = line.split(': ')[-1].split(' ')[0]
                return {
                    'shelfId' : shelfId,
                    'type' : shelfType
                }
        return {}    
        
    def get_all_oscs(self, return_raw=False) -> list :
        ports = self.cli_execute('show cn osc *')
        result = []
        for line in ports.splitlines() :
            if 'OSC' in line :
                data = line.split(' ')
                data = [ x for x in data if x != '']
                if return_raw :
                    result.append(data)
                    break
                shelfSlot = data[0]
                shelf = shelfSlot.split('/')[0]
                slot = shelfSlot.split('/')[1]
                cardType = data[1]
                address = None
                upState = None
                operState = None
                for key , item in enumerate(data) :
                    if address is None :
                        if item.count(".") == 3 :
                            address = item
                            del data[key]
                            break
                for key , item in enumerate(data) :
                    if upState is None :
                        if item.lower() == 'up' or item.lower() == 'down' :
                            upState = item
                            del data[key]
                            break
                for key , item in enumerate(data) :
                    if operState is None :
                        if item.lower() == 'up' or item.lower() == 'down' :
                            operState = item
                            del data[key]
                            break

                result.append({
                    'shelfSlot' : shelfSlot,
                    'shelf' : shelf,
                    'slot' : slot,
                    'type' : cardType ,
                    'adminState' :upState,
                    'operState' : operState,
                    'nextHopAddress' : address,
                })
        return result


    def get_cards(self) :
        cards = self.cli_execute('show card inven *')
        raw_return = cards
        cards = cards.splitlines()
        cardsJson  = []
        for line in cards :
            try :
                if line == '' or "Location  Card" in line or "--"*10 in line : continue 
                card = line.split(' ')
                cardsList = [ i for i in card if i != "" ]
                shelfSlot = cardsList[0]
                shelf = shelfSlot.split('/')[0]
                slot = shelfSlot.split('/')[1]
                family = cardsList[1]
                cardType = cardsList[2]
                pn = cardsList[3]
                sn = cardsList[4]
                cardsJson.append({
                    "shelfSlot" : shelfSlot , 
                    'shelf' : shelf , 
                    'slot' : slot ,
                    'family' : family , 
                    "cardType" : cardType , 
                    "pn" : pn  , 
                    'sn'  : sn
                })
            except :
                continue
        return cardsJson , raw_return

    def get_userlabel(self) :
        return self.cli_execute('show general userlabel')
    
    def enable_openagent(self) :
        self.cli_execute('config general openagent enabled')

    def disable_openagent(self) :
        self.cli_execute('config general openagent disable')

    def openagent_status(self) :
        result = self.cli_execute('show general openagent').splitlines()
        self.logger.debug(f'openagent status response from cli_execute: {result}')
        for line in result :
            self.logger.debug(f'Checking openAgent line by line: line={line}')
            if ":" in line :
                status = line.split(':')[1]
                self.logger.debug(f'open agent detected status is {status}')
                if "enabled" in status.lower() :
                    status  = True
                    break
                elif 'disabled' in status.lower() :
                    status =  False
                    break
                else :
                    status =  'Unknown'
                    break
        self.logger.info(f'Open Agent Status = {status}')
        return status
        
    def get_odukxc(self) : 
        odukxs = self.cli_execute('show odukxc brief')
        odukxs = odukxs.splitlines()
        odukxsList = []
        for key , line in enumerate(odukxs) : 
            try :
                if "------------" in line : continue
                if "A-End" in line or 'XcRate' in line or 'State' in line: continue
                details = line.split('  ')
                details = [ i for i in details if i != "" ]
                if len(details) == 0 : continue
                aEnd = details[0]
                zEnd = details[1]
                id = details[2]
                rate = details[3]
                dir = details[4]
                prot = details[5]
                name = details[6]
                odukxsList.append({
                    'aEnd' : aEnd , "zEnd" : zEnd  , "id" : id , "rate" : rate , "dir" : dir , "protection" : prot , 
                    "name" : name
                })
            except :
                continue
        return odukxsList
        
    def get_version(self) :
        return self.pssRelease
        
    def close_cliconnection(self) :
        self.logger.debug(f'self.close.cli started ...')
        self.quit_gmre()
        sleep(.5)
        self.cli_execute('mm' , wait=False)
        sleep(.5)
        self.cli_execute('logout' , wait=False)
        self.connected = False
        self.logger.debug(f'self.close.cli completed')

    
    def quit_gmre(self) :
        self.logger.debug(f'quiting from gmre if necessary ...')
        if self.gmre and self.isGmreLogin :
            self.cli_execute('quit' , wait=False)
        self.prompt=self.nodePrompt
        self.gmre = False
        self.isGmreLogin = False
        self.logger.debug(f'quiting from gmre if necessary completed')

    def get_mastershelf(self) :
        masterShelf = self.get_shelfs()
        masterShelf = lget( masterShelf , 0  , default={})
        masterShelf = masterShelf.get('type' , '')
        return masterShelf

    def get_mastershelf_type(self) :
        ms = self.showShelf(1)
        return ms.get('type')

    def clear_buffer(self,tries=3,force=False,timeout=2) :
        try :
            prevTimeout = self.channel.gettimeout()
            self.channel.settimeout(timeout)
            if force :
                self.channel.recv(20000)
            else :
                for i in range(tries) :
                    if self.channel.recv_ready():
                        self.channel.recv(1024)
                        break
                    sleep(1)
        except : 
            pass
        self.channel.settimeout(prevTimeout)


    def get_nefirmware(self) :
        self.logger.info('Getting NE firmware .. ')        
        cli = f"show firmware ne"
        result = self.cli_execute(cli)
        data = []
        result = result.splitlines()
        for line in result :
            try :
                if 'sh/sl' in line or '----------' in line or line == ''  or "NE" in line : 
                    continue
                s = line.split(' ')
                s = [ x for x in s if x != '' ]
                shelfslot = s[0]
                shelf = shelfslot.split('/')[0]
                slot = shelfslot.split('/')[1]
                card = s[1]
                try : 
                    profile= s[2]
                except IndexError :
                    profile= 'N/A'
                data.append({'shelf' : shelf , 'slot' : slot ,  'shelf/slot' : shelfslot , 'card' : card , 'profile' : profile  })
            except :
                continue
        self.logger.info('Getting NE firmware .. completed') 
        return data

    def get_ec_type(self) :
        self.logger.debug('retreiving EC type from all installed cards ...')
        cards = self.get_allcards().get('all')
        for key , value in cards.items() :
            self.logger.debug(f'Searching for EC in {key} detail=> {value}')
            if 'EC' in value.get('card' , '').upper() :
                self.logger.debug(f'''EC card detected in {key} card={value.get('card')}''')
                return value.get('card')
            


    def get_availableFW(self) :
        self.logger.info('Getting available firmware .. ')        
        cli = f"show firmware available"
        result = self.cli_execute(cli)
        self.logger.info(f'get_availableFW : command = {cli}')    
        self.logger.debug(f'{self.nodeName} - {cli} - {result}')
        result = result.splitlines()
        data = {}
        start = False
        current_fw = 'Not Found'
        for line in result :
            try :
                if 'All available firmware profiles' in line :
                    self.logger.debug(f'All Available firmware profiles line detected. splitting line to search for cards. and flag start to True.')
                    card = line.split('for')[1].replace(' ', '').replace('\n' , '')
                    start = True
                    profiles = []
                elif start == True :
                    if line != '' :
                        fw = line.replace(' ', '').replace('\n' , '').replace('*' , '')
                        profiles.append(fw)
                        data[card] = {'profiles' : profiles , 'currentfw' :  current_fw}
                    if "*" in line : 
                        current_fw = line.replace(' ', '').replace('\n' , '').replace('*' , '')
                        data[card] = {'profiles' : profiles , 'currentfw' :  current_fw}
            except : 
                pass
        self.logger.debug(f'Getting available firmware completed. {data}') 
        return data

    def getUsers(self) :
        result = self.cli_execute(f'show admin user *')
        sleep(1)
        a = result.splitlines()
        users=[]
        for line in a :
            if '----' in line or "LinuxTools" in line : continue
            line = line.split(' ')
            line = [x for x in line if x != '']
            if len(line) >= 3 :
                try :
                    users.append({
                    'username' : line[0],
                    'group' : line[1],
                    'status' : line[2],
                    'linuxtools' : line[3],
                })
                except :
                    pass
        return users

    def getUser(self,username) :
        self.logger.debug(f"Looking for user {username}")
        users = self.getUsers()
        self.logger.debug(f"Full users array = {users}")
        for user in users :
            f = username == user['username']
            self.logger.debug(f"is username={username} equal ne_username={user.get('username')} ? {f}")
            if username == user['username'] :
                return user
        return {}


    def enable_cli_user(self , user, exception_on_failure=True ):
        """
        Enable PSS login user status from disabled to enabled.
        user : cli user : string
        exception_on_failure : bool, default True. Raise exception if user not found.

        return True if user is enabled
        return False if error raised during the process.
        """
        self.logger.debug(f"enable pss cli user {user}")
        cli = f'config admin users edit {user} status enabled'
        result = self.cli_execute(cli)
        if 'unknown username' in result or len(result) > 0 :
            if exception_on_failure :
                raise exceptions.PSSError(f'Username {user} is not found. PSS response is {result}')
            return False
        return True

    def updateUserPrivileges(self,affectedUsername,newRole) :
        self.logger.info(f"Updating user privileges with {newRole} for {affectedUsername}")
        possibleRoles = ['administrator' , 'observer' , 'provisioner' , 'crypto']
        if not newRole.lower() in possibleRoles :
            self.logger.error(f"Role  '{newRole}'@{affectedUsername} is not a valid role. Possible roles are: {possibleRoles}")
            return False
        cli = f'config admin users edit {affectedUsername} group {newRole}'
        self.cli_execute(cli)
        return True

    def updateMinMaxLoginAttempts(self , maxAttempts=3 ) :
        '''
        change the minimum and max failed login attempts to PSS elements.
        maxAttempts range ( 0 , 15 )
        '''
        ...
        maxAttempts = int(maxAttempts)
        if maxAttempts < 0 or maxAttempts > 15 :
            raise exceptions.PSSError("Invalid maxAttempts Value 0-15")
        command = f"config admin session maxfailedlogins {maxAttempts}"
        self.cli_execute(command)
        return True

    def updateRootPasswordCliMethod(self , password ) :
        '''
        in this function we can update the root password to whatever.\n
        Changing password will be using CLI method. \n
        root will be mentioned by maint1 user
        '''
        if len(password) < 8 :
            raise exceptions.PSSError(f"Password too short. Minimum 8 characters.")
        self.cli_execute(command="config admin system maint1 passwd" , expect="new password")
        self.cli_execute(command=password , expect="Verify password")
        result = self.cli_execute(command=password)
        if not 'changed' in result.lower() :
            raise exceptions.PSSError(f"Failed to update root password")
        return True

    def changeRootPasswordSshMethod(self , password ) :
        '''
        in this function we can update the root password to whatever.\n
        Changing password will be using linux ssh method. \n
        '''
        self.ssh_execute(ssh=self.client , command= f'''echo "root:{password}" | sudo chpasswd''')
        return True

    def disable_cli_user(self , user, exception_on_failure=True ):
        """
        Disable PSS login user status from enabled to disabled.
        user : cli user : string
        exception_on_failure : bool, default True. Raise exception if user not found.
        return True if user is disabled
        return False if error raised during the process.
        """
        self.logger.debug(f"enable pss cli user {user}")
        cli = f'config admin users edit {user} status disabled'
        result = self.cli_execute(cli)
        if 'unknown username' in result or len(result) > 0 :
            if exception_on_failure :
                raise exceptions.PSSError(f'Username {user} is not found. PSS response is {result}')
            return False
        return True

    def get_shelfs(self) :
        self.logger.debug('Getting shelfs .. ')
        shelfsList = []
        # self.clear_buffer()
        cli = f"show shelf *"
        shelfs = self.cli_execute(cli).splitlines()
        start=False
        for line in shelfs :
            if "Description" in line or "Present" in line or '---------' in line : 
                start=True
                continue
            if start :
                self.logger.debug(f'get_shelfs : line before split {line}')
                line= line.split(' ')
                self.logger.debug(f'get_shelfs : line after split {line}')
                line = [line for line in line if line != '']
                self.logger.debug(f'get_shelfs : after removing white-spaces {line}')
                shelfId = lget(line , 0 )
                shelfType =  lget(line , 1  )
                shelfsList.append({
                    'shelfId' : shelfId,
                    'type' : shelfType
                })
        return shelfsList


if __name__ == '__main__' : 
    pass

        
# pss = PSS1830(auto_enable_tcp_forward=True)
# pss.port = 322
# pss.set_debug_level('debug')
# jumpserver = pss.nfmtJumpServer('127.0.0.1' , 'root' , 'Nokia@2023')
# pss = PSS1830()
# pss.set_debug_level('debug')
# x= pss.connect('cli' , neip="10.10.40.167" , jumpserver=jumpserver )
# # x = pss.get_allcards()
# # x = pss.get_ec_type()
# s = pss.enable_cli_user('admin')
# print(s)

# s = pss.get_nefirmware()
# print(s)
# pss.get_mastershelf()
# pss.disable_openagent()
# pss.enable_openagent()
# pss.openagent_status()
# pss.get_version()
# pss.get_xcs()
# pss.channels_report()

# pss.cli_execute('show xc *')
# s = pss.close_cliconnection()
# s = pss.cli_execute('show otu *')
# print(s)
# pss.cli_execute('show shelf *' , False)
# pss.cli_execute('show version')
# pss.cli_execute('show soft up st')
# pss.cli_execute('show card inven * ')
# pss.config_database('10.10.10.1' , 'alcatel' , 'alu1233' , 'ftp' , '/' , 'BACKUP')
# pss.config_swserver('10.10.10.2' , 'alcatel' , 'alu1233' , 'ftp' , '/')
