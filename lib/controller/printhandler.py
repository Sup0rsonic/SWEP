import sys
import os


class PrintController():
    def __init__(self):
        self.LastTextLen = 0
        self.LastText = ''
        pass


    def Print(self, content):
        sys.__stdout__.write('\b' * (len(self.LastText)+1))
        sys.__stdout__.write(content)
        self.LastText = content
        self.LastTextLen = len(content)
        sys.stdout.flush()
        return


    def PrintInline(self, content):
        sys.__stdout__.write('%s\n' %(content))
        return


    def PrintLine(self, content):
        sys.__stdout__.write(content)
        return


    def RawInput(self, prompt):
        self.PrintInline(prompt)
        InputText = sys.stdin.read()
        return InputText


    def Mute(self):
        sys.stdout = open(os.devnull)
        return


    def Resume(self):
        sys.out = sys.__stdout__
        return
