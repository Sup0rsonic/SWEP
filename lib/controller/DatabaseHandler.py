import lib.db.db
import FunctionLib
import pickle
import base64


class DatabaseHandler():
    def __init__(self):
        self.Database = lib.db.db.DBHandler()
        self.Cursor = lib.db.db.DBHandler


    def Connnect(self):
        try:
            self.Database.Connect()
        except Exception, e:
            print '[!] Failed to connect to database: %s' %(str(e))
            return
        return 1


    def SearchHost(self, *keywd):
        try:
            if keywd:
                hosts = self.Database.Query('SELECT * FROM hosts WHERE addr LIKE "%' + keywd[0] + '%";')
            else:
                hosts = self.Database.Query('SELECT * FROM hosts;')
            if len(hosts):
                print '[+] Fetched %s record(s).' %(len(hosts))
                print 'ID       ADDRESS'
                print '--       -------'
                for item in hosts:
                    print str(item[0]).ljust(9) + item[1]
            else:
                print '[*] No hosts found.'
        except Exception, e:
            print '[!] Failed to search host from db: %s' %(str(e))
        return


    def InsertHost(self, host): # Host: (www.baidu.com, [BUF])
        if not host:
            print '[!] Host not found.'
            return
        try:
            self.Database.Execute('INSERT INTO hosts VALUES(NULL, "%s", "%s");' %(host[0], str(host[1])))
            print '[+] Inserted 1 host.'
        except Exception, e:
            print '[!] Failed to insert host: %s' %(str(e))
        return


    def DeleteHost(self, id):
        if not id:
            print '[!] Host not found.'
            return
        try:
            self.Database.Execute('DELETE FROM hosts WHERE id=%s LIMIT 0,1' %(str(id)))
            print '[*] Host delete success.'
        except Exception, e:
            print '[!] Failed to delete host: %s' %(str(e))
            return
        return



    def LoadHost(self, id):
        try:
            HostInfo = self.Database.Query('SELECT * FROM hosts WHERE id=%s LIMIT 0,1' %(str(id)))
        except Exception, e:
            HostInfo = None
            print '[!] Failed to load host from db: %s' %(str(e))
        return HostInfo


    def UpdateHost(self, id, session):
        try:
            SerializedSession = self.Serialize(session)
            self.Database.Query('SELECT * FROM hosts WHERE id=%s' %(str(id)))
            if not self.Database.Session.fetchall():
                if raw_input('[*] Host not found. Do you want to insert it? (Y/N)').upper() != 'Y':
                    return
                self.InsertHost((session.url, SerializedSession))
                print '[+] Site update completed'
                return
            self.Database.Query('UPDATE hosts SET session="%s" WHERE id=%s' %(str(SerializedSession), id))
            print '[+] Site update completed.'
        except Exception, e:
            print '[!] Update failed: %s' %(str(e))
        return



    def Serialize(self, object):
        if not object:
            return
        try:
            Serialized = pickle.dumps(object, protocol=2)
        except Exception, e:
            print '[!] Failed to serialize target: %s' %(str(e))
            return
        Serialized = base64.b64encode(str(Serialized))
        return Serialized


    def Unseralize(self, object):
        if not object:
            return
        try:
            RawStr = base64.b64decode(str(object))
            UnserializedObject = pickle.loads(RawStr)
        except Exception, e:
            print '[!] Failed to unserialize target: %s' %(str(e))
            return
        return UnserializedObject


