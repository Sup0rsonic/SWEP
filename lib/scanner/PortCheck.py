import threading
import socket


def info():
    info = {
        'name': 'port',
        'path': 'PortCheck',
        'fullname': 'SWEP PORT SCANNER',
        'description': 'A simple port scanner',
        'parameters': {
            'Url': 'Target URL.',
            'Address': 'Target IP.',
            'Lrange': 'Target start port. Default: 1',
            'Rrange': 'Target end port. Default: 65535',
            'Thread': 'Threads. Default: 10',
            'Timeout': 'Connection timeout. Default: 1'
        },
        'author': 'BERACHERS security',
        'date': '2019-01-28'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Address = None
        self.Thread = 10
        self.Timeout = 1
        self.TaskList = []
        self.PortList = []
        self.Lrange = 1
        self.Rrange = 65535
        pass


    def Scan(self):
        try:
            if not self.GetAddress():
                print '[!] Failed to get address, quitting.'
                return
            self.Thread = int(self.Thread)
            self.Timeout = int(self.Timeout)
            self.Lrange = int(self.Lrange)
            self.Rrange = int(self.Rrange)
            checker = threading.Thread(target=self.ThreadChecker)
            checker.setDaemon(True)
            self.Status = True
            checker.start()
            while True:
                if len(self.TaskList) < self.Thread:
                    thread = threading.Thread(target=self.FetchData, args=[self.Lrange])
                    thread.start()
                    self.TaskList.append(thread)
                    self.Lrange += 1
                    if self.Lrange == self.Rrange:
                        print '[*] Scan completed, synchronizing threads.'
                        for item in self.TaskList:
                            item.join()
                        self.Status = False
                        break
            print '[*] Fetch completed, %i port(s) open.' %(len(self.PortList))
            if len(self.PortList):
                print '[*] Incoming port information.'
                for item in self.PortList:
                    print ' |    Port: %i' %(item[0])
                    print ' |      |   Data: %s' %(item[1])
                print '[*] Data output completed.'
        except KeyboardInterrupt:
            print '[*] User stop.'
        except Exception, e:
            print '[!] Failed to fetch target data: %s' %(str(e))
        self.Status = False
        return self.PortList



    def FetchData(self, port):
        try:
            print '[*] Scanning port %i.' %(int(port))
            sess = socket.socket(2,1)
            sess.settimeout(int(self.Timeout))
            sess.connect((self.Address, port))
            try:
                data = sess.recv(1024)
            except socket.timeout:
                data = ''
        except socket.timeout:
            return
        except Exception:
            return
        self.PortList.append([port, data])
        return


    def GetAddress(self):
        if self.Address:
            return
        try:
            self.Address = socket.gethostbyname(self.Url)
        except Exception, e:
            print '[!] Failed to get target address: %s' %(str(e))
            return 0
        return 1


    def ThreadChecker(self):
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


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
    scanner.Url = ''
    scanner.Thread = 200
    scanner.Lrange = 0
    scanner.Rrange = 65535
    scanner.Scan()

