import lib.intruder


class Controller():
    def __init__(self):
        self.Switch = {'adminpage': False, 'sqli': False, 'ftp': False, 'logic': False, 'ssh': False, 'spider': False, 'xss': False, 'cmsexp': False, 'cmsidf': False, 'hashcheck': False}
        self.Args = {'url': None, 'Thread': None, 'FTPUserDict': None, 'FTPPasswordDict': None, 'SSHUserDict': None, 'SSHPassDict': None}
        self.ProcessList = []
        pass


    def Start(self, switch, args): # Start intrude
        if not self.Args['url']:
            print '[!] URL not specified.'
        if not self.Args['Thread']:
            print '[!] Thread not specified, Using 10 by default.'
            self.Args['Thread'] = 3
        else:
            self.Args['Thread'] = int(str(self.Args['Thread']))
        if self.Switch['cmsidf']:
            pass
        if self.Switch['spider']:
            pass
        if self.Switch['adminpage']:
            pass
        if self.Switch['xss']:
            pass
        if self.Switch['sqli']:
            pass
        if self.Switch['hashcheck']:
            pass
        if self.Switch['logic']:
            pass
        if self.Switch['cmsexp']:
            pass
        if self.Switch['ssh']:
            pass
        if self.Switch['ftp']:
            pass


    def Status(self): # Get status from modules.
        pass


    def GetThread(self):
        pass
