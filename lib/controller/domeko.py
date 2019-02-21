#coding:utf-8

import json
import requests
import argparse
import socket
import re
import threading
import Queue


debug = True
get=False
thread = 1


'''

parser = argparse.ArgumentParser()
parser.add_argument('-url','--url',dest='url',help='Target URL')
parser.add_argument('-s','--subnet',dest='subnet',help='Subnet to scan')
parser.add_argument('-t','--threads',dest='thread',help='Thread count, default == 1')
parser.add_argument('-f','--filename',dest='filename',help='Output filename, Not available in current version(1.0.0dev)')
parser.add_argument('-g','--fetch-page',dest='get',help='Fetch target homepage, Not available in current version(1.0.0dev)')

args = parser.parse_args()

url = args.url
subnet = args.subnet
thread = args.subnet
filename = args.filename
get = args.get

if debug == True:
    url = '123.com'
'''
def conn(url,scanval):
    global hostlist
    ip = socket.gethostbyname(url)
    hostlist = []
    if scanval == 'c':
        addr = re.findall('(.*\.)',ip)
        for i in range(255):
            hostlist.append(addr[0] + str(i))
    elif scanval == 'b':
        addr = re.findall('(.*\.)\.*\.',ip)
        host = addr[0]
        for i in range(0,255):
            baddr = host + str(i) + '.'
            for j in range(0,255):
                hostlist.append(baddr + str(j))
    else:
        hostlist = [ip]
    print hostlist
    return hostlist

def scan(hostname):
    hostlist = []
    print '[*] Fetching information for %s' % hostname
    try:
        raw = requests.get('http://api.webscan.cc/?action=query&ip=' + hostname, timeout=3)
    except requests.Timeout:
        print '[*] Error: Query timeout, address: %s' %(str(hostname))
        return
    resp = raw.text.encode('utf-8')
    if re.findall('null',resp) != [] :
        print '[*] No website found on %s'%hostname
        return
    if raw.status_code != 200:
        print '[*] Error occurred.'
        return
    resp = re.sub(u'\ufeff','',resp.decode('utf-8'))
    try:
        rjson = json.loads(resp)
    except Exception, e:
        print '[!] Failed to decode json: %s' %(str(e))
        return
    print '[+] %i host(s) found on %s' %(len(rjson),hostname)
    for i in rjson:
        print ' |  [+] Site title:%s' %i['title']
        print ' |  [+] Site URL:%s' %i['domain']
    return rjson

def savefile(hosts,filename):
    file = open(str(filename),'w+')
    for i in hosts:
        file.write(i)
    print '[+]File write complete.'

'''
if url == None:
    print '[!]No url specified.'
    exit(1)
if subnet:
    if subnet.lower() == 'b':
        if raw_input('[*]Warning:You are trying to scan a B-class subnet.Sure? (Y/N)').upper() != 'Y':
            exit()
        print '[*]Scanning target B-class subnet.'
        hostlist = conn(url,'b')
    if subnet.lower() == 'c':
        print '[*]Scanning target C-class subnet.'
        hostlist = conn(url,'c')
    else:
        print '[*]No subnet specified,using default.'
    if not thread:
        thread = 1
    hosts = Queue.Queue()
    for i in hostlist:
        hosts.put(i)
    i = 0
    while hosts.empty() != True:
        while i < int(thread):
            scanner = threading.Thread(target=scan,args=(hosts.get()))
            i += 1
            scanner.start()
else:
    print '[*]Subnet not provided. Scanning single site.'
    resp = scan(socket.gethostbyname(url))
    if filename != None:
        output = open(str(filename),'w+')
        output.write('###########################\n#Domeko Host Report\n###########################')
        for i in resp:
            output.write(i['title'])

def interactive(): # todo: Interactive mode
    banner()
    print '[*]Domeko Interactive start.'
    print '[*]Type help to get help.'
    pass

def banner(): # todo: Banner
    pass
'''


