import requests


class AdminPageIdentifer():
    def __init__(self):
        self.Url = None
        self.AdminPageDict = None
        self.Threads = 10
        self.Timeout = 3
        pass


    def FetchAdminPage(self):
        if not self.Url:
            print '[!] URL not specified.'
            return
        elif not self.AdminPageDict:
            print '[*] Admin page list not specified, using default.'
            self.AdminPageDict = open('')