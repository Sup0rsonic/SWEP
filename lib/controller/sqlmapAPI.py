import os
import sys
import json
import requests
import subprocess
import lib.config
import time

# Low-level sqlmapapi port interface for swep.
# Powered by MAGIC, better don't touch.

# Development settings.
# DON'T EDIT except you know what are you doing.
# todo: Edit after development.
dev_mode = True


if dev_mode:
    lib.config.SQLmapHost = 'localhost'
    lib.config.SQLmapPort = 8775
    lib.config.SQLmapFileDir = '/usr/share/sqlmap'


class sqlmapApi():
    def __init__(self):
        self.sqlmapApiHost = lib.config.SQLmapHost
        self.sqlmapApiPort = lib.config.SQLmapPort
        self.sqlmapPath = lib.config.SQLmapFileDir
        self.ParmList = {}
        self.Url = 'http://%s:%s' % (self.sqlmapApiHost, str(self.sqlmapApiPort))
        if not os.path.isdir(self.sqlmapPath):
            print '[!] Failed to load sqlmap dir. Check your config.'
            return
        path = 'python %s/sqlmapapi.py' %(self.sqlmapPath)
        self.API = os.popen('python %s/sqlmapapi.py -s' %(self.sqlmapPath))
        time.sleep(3) # Nasty hack waiting for sqlmapapi initalize
        # self.ProcessList = [] # Json format: {'taskid': 'xxxxxx', 'status': 'xxxxxxx'(true|false|complete) 'resp': {xxxxx(resp)}}
        pass


    def InitalizeServer(self):
        try:
            requests.get(self.Url)
        except requests.ConnectionError:
            self.TryConnect()
        print '[+] sqlmapapi server init complete.'
        return True


    def Get(self, url):
        try:
            resp = requests.get(url)
        except requests.ConnectionError, e:
            if raw_input('[!] Failed to connect to server: %s. Retry?(Y/n)' %(str(e)).upper() != 'N'):
                resp = self.Get(url)
            else:
                resp = None
        except Exception, e:
            print '[!] Error connecting to server: %s' %(str(e))
            return
        return resp


    def Post(self, url ,data):
        try:
            resp = requests.post(url, data, headers={'Content-Type': 'application/json'})
        except requests.ConnectionError, e:
            if raw_input('[!] Failed to connect to server: %s. Retry?(Y/n)' %(str(e)).upper() != 'N'):
                resp = self.Get(url)
            else:
                resp = None
        except Exception ,e:
            print '[!] Error connecting to server: %s' %(str(e))
            return
        return resp


    def TryConnect(self):
        while raw_input('[!] Failed to connect to sqlmapapi server. Retry?(Y/n)').upper() != 'N':
            try:
                self.Get(self.Url)
                return
            except requests.ConnectionError:
                pass
        else:
            print '[!] Failed to connect to sqlmapapi server. Please start manually.'
            return False


    def NewTask(self):
        resp = self.Get('%s/task/new' %(self.Url))
        StatJson = json.loads(resp.text)
        if not StatJson['success']:
            print '[!] Failed starting task.'
            return
        self.Post('%s/option/set' %(self.Url), '{ "dumpAll": true }')
        pid = StatJson['taskid']
        return pid


    def StartScan(self, taskid, url):
        try:
            SessUrl = '%s/scan/%s/start' %(self.Url, str(taskid))
            TaskJson = json.loads(self.Post(SessUrl, '{"url": "%s"}' %(url)).text)
        except Exception, e:
            print '[!] Failed to start scan: %s' %(str(e))
            return
        if TaskJson['success']:
            print '[*] Starting scan for %s, id: %s' %(url, TaskJson['engineid'])
        else:
            print '[!] Failed to start scan %s.' %(url)
        return TaskJson


    def FetchLog(self, id):
        try:
            SessLog = json.loads(self.Get('%s/scan/%s/log' %(self.Url, str(id))).text)
        except Exception, e:
            print '[!] Failed to fetch log for id %d: %s' %(id, str(e))
            return
        return SessLog


    def GetStat(self, id):
        try:
            ProcStat = json.loads(self.Get('%s/scan/%s/status' %(self.Url, str(id))).text)
        except Exception, e:
            print '[!] Failed to fetch status for id %s: %s' %(id, str(e))
            return
        return ProcStat


    def GetData(self, id):
        try:
            SessData = json.loads(self.Get('%s/scan/%s/data' %(self.Url, str(id))).text)
        except Exception, e:
            print '[!] Failed to fetch data from id %s: %s' %(id, str(e))
            return
        return SessData


    def SetOptions(self, id , option, val):
        try:
            if not json.loads(self.Post('%s/option/%s/set' %(self.Url, id), '{"%s": %s}' %(option, val)).text)['success']:
                print '[!] Failed to set %s to %s.' %(option, val)
            else:
                self.ParmList[option] = val
        except Exception, e:
            print '[!] Failed to set %s to %s: %s' %(option, val, str(e))
        return


    def StopTask(self, id):
        try:
            self.Get('%s/scan/%s/stop' %(self.Url, id))
            print '[*] Stopped task %s' %(str(id))
            return True
        except Exception ,e:
            print '[!] Failed to stop task %s' %(str(id))
        return