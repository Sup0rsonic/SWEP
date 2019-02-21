import os
import sys
import lib.config
import MainHandler


# Hope this works.
# Hope this works.
# Hope this works.


class intruder():
    def __init__(self):
        self.MainHandler = MainHandler.MainHandler()
        self.Url = None
        self.Protocol = None
        self.Threads = 10
        self.TaskList = []
        pass


    def GetCmd(self):
        try:
            self.MainHandler.ShowMenu()
            while True:
                cmd = raw_input('[>]=[SWEP Intruder]: ')
                self.InterpretCommand(cmd)
        except KeyboardInterrupt:
            print '[*] User exit.'
            return
        except Exception, e:
            print '[!] Error interpreting command: %s' %(str(e))
        return


    def ShowInfo(self):
        pass


    def InterpretCommand(self, CommandDict):
        CommandDict = CommandDict.rstrip(' ').split(' ', 1)
        if len(CommandDict) < 1:
            if CommandDict[0] != 'help':
                self.Help('help')
            else:
                self.Help(CommandDict)
        if CommandDict[0] == 'set':
            self.Set(CommandDict[1])
        elif CommandDict[0] == 'unset':
            self.Unset(CommandDict[1])
        elif CommandDict[0] == 'switch':
            self.Switch(CommandDict[1])
        elif CommandDict[0] == 'help':
            self.Help(CommandDict)
        elif CommandDict[0] == 'scan':
            self.StartScan()
        else:
            self.Help(CommandDict)
        return


    def Set(self, CommandDict):
        CommandDict = CommandDict.split(' ')
        if CommandDict[0] in ['sql', 'xss', 'admin', 'file', 'ftp', 'ssh']:
            if len(CommandDict < 3):
                self.MainHandler.PrintMenu('[!] Invalid parameter count.\n  |    Usage: set [*scanner] [parameter] [value]')
                return
            self.MainHandler.Set(CommandDict[0], CommandDict[1], CommandDict[2])
        else:
            if len(CommandDict) < 2:
                self.MainHandler.PrintMenu('[!] Invalid parameter count.\n  |    Usage: set [parameter] [value]')
                return
            for item in ['sql', 'xss', 'admin', 'file', 'ftp', 'ssh']:
                self.MainHandler.Set(item, CommandDict[0], CommandDict[1])
        return


    def Switch(self, CommandDict):
        CommandDict = CommandDict.split(' ')
        if len(CommandDict) < 2:
            self.MainHandler.PrintMenu('[!] Invalid parameter count.\n  |    Usage: switch [scanner] [on|off]')
            return
        self.MainHandler.Switch(CommandDict[0], CommandDict[1])
        return


    def StartScan(self):
        print '[*] Starting scan.'
        self.MainHandler.Scan()
        return


    def Unset(self, CommandDict):
        CommandDict = CommandDict.split(' ')
        if len(CommandDict) < 1:
            self.MainHandler.PrintMenu('[!] Invalid parameter count.\n  |    Usage: unset [*scanner] [value]')
            return
        elif CommandDict[0] not in ['sql', 'xss', 'admin', 'file', 'ftp', 'ssh']:
            for item in ['sql', 'xss', 'admin', 'file', 'ftp', 'ssh']:
                self.MainHandler.Unset(item, CommandDict[1])
        else:
            if len(CommandDict) > 2:
                self.MainHandler.PrintMenu('[!] Invalid parameter count.\n  |    Usage: unset [scanner] [value]')
            else:
                self.MainHandler.Unset(CommandDict[0], CommandDict[1])
        return


    def Help(self, CommandDict):
        self.MainHandler.ShowMenu()
        if len(CommandDict) == 1:
            print '[*] Help: help [set unset switch scan help]'
        elif CommandDict[1] == 'set':
            print '[*] Help: set [*scanner] [value]'
        elif CommandDict[1] == 'unset':
            print '[*] Help: set [*scanner] [value]'
        elif CommandDict[1] == 'switch':
            print '[*] Help: switch [*scanner] [on|off]'
        elif CommandDict[1] == 'scan':
            print '[*] Help: scan'
        elif CommandDict[1] == 'help':
            print '[*] Help: [set unset switch scan help] [*module] [*value]'
        elif CommandDict[1] == 'eggs':
            prompt = raw_input('[*] Eggs: ')
            if prompt == 'coffee':
                print '[COFFEE] ?'
            elif prompt == 'help':
                print '[*] This is not a help.'
            elif prompt == 'the answer to life the universe and everything':
                print '[*] 42'
            elif prompt == 'something':
                print '[*] Hello! This will become a set of challenge. Join development to fill it up.'
            else:
                print '[*] Please ask me something.'
        else:
            self.Help([])
        return




def test():
    sess = intruder()
    sess.GetCmd()

test()