import threading
import queue
import ftplib
import json
import socket
import time


def info():
    info = {
        'name': 'ftp',
        'path': 'FTPPasswordScanner',
        'fullname': 'SWEP FTP PASSWORD SCANNER',
        'description': 'FTP weak password scanner',
        'parameters':{
            'Url': 'Target URL',
            'Port': 'Target port, Default: 22',
            'UsernameFile': '(OPTIONAL) Username file',
            'PasswordFile': '(OPTIONAL) Password file',
            'UserPassFile': '(OPTIONAL) Username and password file',
            'Threads': 'Threads. Default: 10',
            'Timeout': 'Timeout. Default: 3'
        },
        'author': 'BREACHER security',
        'date': '2019-01-12'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.addr = None
        self.port = 22
        self.UsernameFile = None
        self.PasswordFile = None
        self.UserpassFile = None
        self.Threads = 10
        self._Counter = 0
        self.Timeout = 3
        self.Time = 0
        self.Status = False
        self.UserPassList = []
        self.TaskList = []
        self.Status = True
        self.Queue =queue.Queue()
        self.Name = 'FTP Password'


    def GetFTPPassword(self):
        UserpassList = self.LoadPasswordDictionary()
        self.addr = socket.gethostbyname(self.Url)
        self.port = int(self.port)
        self.Threads = int(self.Threads)
        self.Timeout = int(self.Timeout)
        self.Status = True
        timer = threading.Thread(target=self.Timer)
        timer.setDaemon(True)
        checker = threading.Thread(target=self.ThreadChecker)
        checker.setDaemon(True)
        statchecker = threading.Thread(target=self.StatChecker)
        statchecker.setDaemon(True)
        statchecker.start()
        checker.start()
        timer.start()
        try:
            while True:
                if not self.Status:
                    break
                if len(self.TaskList) < self.Threads:
                    thread = threading.Thread(target=self.CheckPassword, args=[self.Queue.get()])
                    thread.start()
                    self.TaskList.append(thread)
                    time.sleep(0.3)
                if not self.Status:
                    break
        except KeyboardInterrupt:
            print '[*] Keyboard interrupt: Quitting.'
            return
        except Exception, e:
            print '[!] Failed attaining FTP password: %s' %(str(e))
        return self.UserPassList


    def LoadPasswordDictionary(self):
        if not self.PasswordFile:
            if not self.UsernameFile:
                mode = 1
            else:
                print '[!] Please specify username file.'
                return
        else:
            mode = 0
        if mode:
            UserPassJson = json.load(open('FTPPassword.json', 'r'))
            PasswordList = UserPassJson['password']
            UsernameList = UserPassJson['user']
        else:
            UsernameList = open(self.UsernameFile, 'r').read().split('\n')
            PasswordList = open(self.PasswordFile, 'r').read().split('\n')
        UsernameList = self.RemoveDuplicate(UsernameList)
        PasswordList = self.RemoveDuplicate(PasswordList)
        for username in UsernameList:
            for password in PasswordList:
                self.Queue.put('%s:%s') %(username, password)
        print '[+] Dictionary load completed, Total %s user-pass pairs.' %(str(self.Queue.qsize()))


    def CheckPassword(self, credential):
        username , password = credential.split(':')
        sess = ftplib.FTP(host=self.addr, user=username, passwd=password)
        try:
            sess.connect(self.addr, self.port, timeout=int(self.Timeout))
            print '[+] Connect success: %s' %(str(credential))
        except ftplib.error_perm:
            pass
        except Exception, e:
            print '[!] Error trying to login: %s' %(str(e))
        self.UserPassList.append(credential)
        return


    def RemoveDuplicate(self, dict):
        NewList = []
        for item in dict:
            if item not in NewList:
                NewList.append(item)
        return NewList


    def Scan(self):
        FTPPasswordList = self.GetFTPPassword()
        return FTPPasswordList


    def Timer(self):
        while self.Status:
            time.sleep(1)
            self.Time += 1


    def StatChecker(self):
        while self.Status:
            time.sleep(5)
            print '[*] %s thread running, %s item left, cost %s seconds' %(str(len(self.TaskList)), str(self.Queue.qsize()), self.Time)



    def ThreadChecker(self):
        while True:
            time.sleep(1)
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
            if not self.Queue.qsize() and len(self.TaskList) == 0:
                self.Status = False
                break



    def info(self):
        InformationList = info()
        args = InformationList['parameters']
        print '[*] Incoming scanner information:'
        print '[*] Scanner name: %s' %(InformationList['name'])
        print ' |   %s' %(InformationList['fullname'])
        print ' |   Description: %s' %(InformationList['description'])
        print ' |   Author: %s' %(InformationList['author'])
        print ' |   Date: %s' %(InformationList['date'])
        print ' |   Arguments: Total %i' %(len(args))
        print ' |    |  NAME        DESCRIPTION'
        print ' |    |  ----        `-----------'
        for item in args.keys():
            print ' |    |  %s%s' %(item.ljust(12), args[item])
        print ' |'
        print '[*] Scanner information end.'


def test():
    scanner = Scanner()
    scanner.info()

