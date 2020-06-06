#!/usr/bin/python3

mirrorCfg = '/etc/sisyphus/mirrors.conf'

def getList():
    mirrorList = []

    with open(mirrorCfg) as mirrorFile:
        for line in mirrorFile.readlines():
            if 'PORTAGE_BINHOST=' in line:
                url = line.split("=")[1].replace('"', '').rstrip()
                mirror = {'isActive': True, 'Url': url}
                if line.startswith('#'):
                    mirror['isActive'] = False
                mirrorList.append(mirror)
        mirrorFile.close()

    return mirrorList

def printList():
    mirrorList = getList()

    for i, line in enumerate(mirrorList):
        if line['isActive']:
            print(i + 1, '*', line['Url'])
        else:
            print(i + 1, ' ', line['Url'])

def writeList(mirrorList):
    with open(mirrorCfg, 'w+') as mirrorFile:
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("# Support for multiple mirrors is somewhat incomplete #\n")
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("#       Please avoid using the Main Repository        #\n")
        mirrorFile.write("#    http://mirrors.redcorelinux.org/redcorelinux     #\n")
        mirrorFile.write("#  as the bandwidth is limited, use mirrors instead   #\n")
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("#    Uncomment only one mirror from the list bellow   #\n")
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("\n")
        for line in mirrorList:
            mirror = 'PORTAGE_BINHOST=' + '"' + line['Url'] + '"'
            if not line['isActive']:
                mirror = '# ' + mirror
            mirrorFile.write(mirror + "\n")
            mirrorFile.write("\n")

def setActive(mirror):
    mirror = int(mirror[0])
    mirrorList = getList()
    if mirror not in range(1, len(mirrorList) + 1):
        print("\n" + "Mirror index is wrong, please check with sisyphus --mirror --list" + "\n")
    else:
        for i in range(0, len(mirrorList)):
            indx = i + 1
            if indx == mirror:
                mirrorList[i]['isActive'] = True
            else:
                mirrorList[i]['isActive'] = False
        writeList(mirrorList)
