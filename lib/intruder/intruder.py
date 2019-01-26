import os
import sys
import lib.intruder
import getpass


class Intruder():
    def __init__(self):
        self.Phase = None
        self.Username = getpass.getuser()
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.Args = {'url': None, 'Thread': None, 'FTPUserDict': None, 'FTPPasswordDict': None, 'SSHUserDict': None,'SSHPassDict': None}
        self.SwitchStatus = {'adminpage': False, 'sqli': False, 'ftp': False, 'logic': False, 'ssh': False, 'spider': False, 'xss': False, 'cmsexp': False, 'cmsidf': False, 'hashcheck': False}
        self.Controller = lib.intruder.controller.Controller()
        pass


    def GetCmd(self):
        while True:
            cmd = raw_input('[SWEP intruder %s: %s]~$ ' %(self.Username, os.getcwd()))
            if cmd == 'exit':
                return
            self.InterpretCmd(cmd)


    def InterpretCmd(self, cmd):
        CommandDict = str(cmd).split(' ')
        if CommandDict[0] == 'set': # Set a variable. Example: set url test.com
            pass
        elif CommandDict[0] == 'unset': # Unset a variable.
            pass
        elif CommandDict[0] == 'start': # Start intrude.
            pass
        elif CommandDict[0] == 'show': # Show status
            pass
        elif CommandDict[0] == 'switch': # Switch function on/off
            pass
        elif CommandDict[0] == 'help': # Help
            pass
        elif CommandDict[0] == 'clear':
            pass
        elif CommandDict[0] == 'cd':
            pass
        else:
            pass


    def Set(self, arg, value):
        self.Args[arg] = value
        print '[*] %s => %s' %(arg, value)
        return


    def Unset(self, arg):
        self.Args[arg] = None
        print '[*] Unset %s.'


    def Start(self):
        self.Controller.Start(self.SwitchStatus, self.Args)
        return


    def ShowStatus(self):
        pass


    def PrintStatus(self):
        pass
