import os
print 'SWEP Duplication remove tool'
filename = raw_input('Filename> ')
print '[*] Stating removing duplication.'
file = open(filename, 'r+')
rawlist = file.read().split('\n')
newlist = []
for item in rawlist:
    if item not in newlist:
        newlist.append(item)
shorted = len(rawlist)-len(newlist)
print '[+] Remove completed. Total %s line(s), removed %s items.' %(str(len(newlist)), str(shorted))
os.remove(filename)
newfile = open(filename, 'w+')
for item in newlist:
    newfile.write(item)
    newfile.write('\n')
newfile.close()
