import sqlite3
import lib.config
import sys

class DBHandler():
    def __init__(self):
        self.Prefix = lib.config.DatabasePrefix
        self.Connection = None
        self.Session = None
        self.Connect()
        self._Initalize()
        pass


    def Connect(self):
        try:
            conn = sqlite3.connect(lib.config.DatabaseFile)
        except Exception, e:
            raise SystemError('Failed to connect to database: %s' %(str(e)))
        self.Connection = conn
        try:
            sess = conn.cursor()
        except Exception, e:
            raise SystemError('Failed to connect to load cursor: %s' %(str(e)))
        self.Session = sess
        return sess


    def _CheckDatabase(self):
        try:
            self.Session.execute('SELECT * FROM hosts LIMIT 0,1')
            self.Session.execute('SELECT * FROM sessions LIMIT 0,1')
            self.Session.execute('SELECT * FROM exploit LIMIT 0,1')
            self.Session.execute('SELECT * FROM modules LIMIT 0,1')
            self.Session.execute('SELECT * FROM wshell LIMIT 0,1')
            return 1
        except sqlite3.OperationalError, e:
            print '[*] Database not exist.'
            return 0


    def _Initalize(self):
        if self._CheckDatabase():
            pass
        else:
            print '[*] Database not found.'
            try:
                self.Session.execute('CREATE TABLE IF NOT EXISTS hosts (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, addr TEXT, buffer TEXT)') # Hosts
                self.Session.execute('CREATE TABLE IF NOT EXISTS modules (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, path TEXT, description TEXT)')
                self.Session.execute('CREATE TABLE IF NOT EXISTS exploit (name TEXT PRIMARY KEY UNIQUE, description TEXT)')
                self.Session.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, date TEXT, info TEXT, buffer TEXT)') # Sessions for re-use. Hosts not included.
                self.Session.execute('CREATE TABLE IF NOT EXISTS wshell (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, url TEXT, password TEXT, obfs TEXT, info TEXT)')
                self.Connection.commit()
            except Exception ,e:
                print '[!] Error generating database: %s.' %(str(e))
                return None
            print '[+] Database generate complete.'
            return 1


    def Query(self,query):
        try:
            self.Session.execute(query)
            resp = self.Session.fetchall()
        except Exception, e:
            print '[!] Error execute query %s: %s' %(str(query),str(e))
            resp = None
        return resp


    def Fetch(self,array):
        pass


    def Exit(self):
        try:
            self.Connection.commit()
            self.Connection.close()
            return 1
        except Exception, e:
            print '[!] Failed to close database connection: %s' %(str(e))
        return 0


    def Execute(self, query):
        try:
            self.Session.execute(query)
            self.Connection.commit()
        except Exception, e:
            print '[!] Failed to execute query %s: %s' %(str(query), str(e))
            return 0
        return 1


    def Init(self):
        self._Initalize()
        return

