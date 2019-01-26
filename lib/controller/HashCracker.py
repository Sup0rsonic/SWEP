import hashlib
import threading
import queue


def info():
    info = {
        'name': 'hash',
        'path': 'HashCracker',
        'fullname': 'SWEP HASH CRACKER',
        'description': 'Hash cracker. Supports md5 and all sha types.',
        'parameters':{
            'Hash': 'Hash to crack',
            'mode': 'Hash mode',
            'Thread': 'Threads. Default: 10'
        },
        'author': 'BREACHERS security',
        'date': '2019-01-26'
    }
    return info



class Scanner():
    def __init__(self):
        self.TaskList = []
        self.Thread = 10
        self.Queue = queue.Queue()
        self.Hash = None
        self.Status = False
        self.PlainText = ''
        self.mode = 'md5'
        self.FileName = '/home/nimda/swep/WordLists/100000.txt'
        pass


    def CrackHash(self, **hash):
        if not hash:
            if not self.Hash:
                print '[!] Hash not specified.'
                return
        else:
            self.Hash = hash[0]
        fp = open(self.FileName, 'w+')
        for item in fp.read().split('\n'):
            self.Queue.put(item)
        if self.mode == 'md5': # Duplicate but good for efficiency.
            while len(self.TaskList) or self.Queue.qsize():
                    if len(self.TaskList) < self.Thread:
                        threading.Thread(target=self._Md5HashCracker, args=[self.Queue.get()]).start()
                    if self.Status:
                        break
        elif self.mode == 'sha1':
            while len(self.TaskList) or self.Queue.qsize():
                    if len(self.TaskList) < self.Thread:
                        threading.Thread(target=self._Sha1HashCracker, args=[self.Queue.get()]).start()
                    if self.Status:
                        break
        elif self.mode == 'sha224':
            while len(self.TaskList) or self.Queue.qsize():
                if len(self.TaskList) < self.Thread:
                    threading.Thread(target=self._Sha224HashCracker, args=[self.Queue.get()]).start()
                if self.Status:
                    break
        elif self.mode == 'sha256':
            while len(self.TaskList) or self.Queue.qsize():
                if len(self.TaskList) < self.Thread:
                    threading.Thread(target=self._Sha256HashCracker, args=[self.Queue.get()]).start()
                if self.Status:
                    break
        elif self.mode == 'sha384':
            while len(self.TaskList) or self.Queue.qsize():
                if len(self.TaskList) < self.Thread:
                    threading.Thread(target=self._Sha256HashCracker, args=[self.Queue.get()]).start()
                if self.Status:
                    break
        elif self.mode == 'sha512':
            while len(self.TaskList) or self.Queue.qsize():
                if len(self.TaskList) < self.Thread:
                    threading.Thread(target=self._Sha512HashCracker, args=[self.Queue.get()]).start()
                if self.Status:
                    break
        else:
            print '[!] Invalid hash type. Support type: md5, sha1|224|256|384|512.'
            return
        if self.PlainText:
            print '[+] Password found: %s' % (self.PlainText)
            return self.PlainText
        else:
            print '[*] Hash not found.'
        return


    def _Md5HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.md5(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return

    def _Sha1HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.sha1(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return


    def _Sha224HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.sha224(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return


    def _Sha256HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.sha256(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return



    def _Sha384HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.sha384(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return


    def _Sha512HashCracker(self, plaintext):
        print '[*] Checking %s' %(plaintext)
        if hashlib.sha512(plaintext).hexdigest() == hashlib.md5(self.Hash).hexdigest():
            self.Status = True
            self.PlainText = plaintext
        return


    def GetPlaintext(self, mode, digit): # todo: list generation
        list = []
        CharList = ['a', 'b', 'c', 'd', 'e' ,'f', 'g', 'h', 'i' ,'j', 'k', 'l' ,'m', 'n', 'o' ,'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        NumList = [1,2,3,4,5,6,7,8,9,10]
        if mode == 'a-z':
            for i in range(digit):
                for i in CharList:
                    pass


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
    scanner.Hash = '21232f297a57a5a743894a0e4a801fc3'
    scanner.CrackHash()

test()