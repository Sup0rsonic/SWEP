import sys
import os
import ModuleHandler
import PrintHandler


class  Controller():
    def __init__(self):
        self.ModuleHandler = ModuleHandler.ModuleHandler()
        self.PrintHandler = PrintHandler.PrintController()
        self.Path = os.path.abspath(__file__)
        

    def Set(self, arglist):
        if len(arglist) == 1:
            print '[*] Invalid usage. Usage: set arg val'
            return
        self.ModuleHandler.ArgumentList[arglist[0]] = arglist[1]
        return 1


    def unset(self, arglist):
        self.ModuleHandler.ArgumentList[arglist[0]] = None
        return


    def switch(self, name, mode):
        if mode == 'on':
            self.ModuleHandler.OptionDict[name] = True
        elif mode == 'off':
            self.ModuleHandler.OptionDict[name] = False
        else:
            print '[*] Invalid usage. Usage: switch module on/off'
            return 0
        return 1


    def pause(self):
        pass


    def ShowInfo(self):
        pass


    def ShowOptions(self):
        self.PrintHandler.PrintLine('--SWEP Intruder----------')
        self.PrintHandler.PrintLine('')
        self.PrintHandler.PrintLine('')
        self.PrintHandler.PrintLine('ID    NAME       STATUS')
        self.PrintHandler.PrintLine('==    ====       ======')
        counter = 0
        for item in self.ModuleHandler.OptionDict.keys():
            counter += 1
            self.PrintHandler.PrintLine('%s%s%s' %(str(counter).ljust(6, ' '), item.ljust(11, ' '), 'ON' if self.ModuleHandler.OptionDict[item] else 'OFF'))
        pass