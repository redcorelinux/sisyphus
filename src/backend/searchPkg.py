#!/usr/bin/python3

import sqlite3
import sisyphus.checkEnvironment
import sisyphus.getFilesystem
import sisyphus.updateAll

def searchDB(filter, cat = '', pn = '', desc = ''):
    NOVIRT = "AND cat NOT LIKE 'virtual'"
    SELECTS = {
        'all': f'''SELECT
                    i.category AS cat,
                    i.name as pn,
                    i.version as iv,
                    IFNULL(a.version, 'alien') AS av,
                    d.description AS desc
                    FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
    				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    UNION
                    SELECT
                    a.category AS cat,
                    a.name as pn,
                    IFNULL(i.version, 'None') AS iv,
                    a.version as av,
                    d.description AS desc
                    FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
    				LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}''',
        'installed': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.version AS iv,
                    a.version as av,
                    d.description AS desc
                    FROM local_packages AS i
                    LEFT JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
    				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}''',
        'alien': f'''SELECT
                        i.category AS cat,
                        i.name AS pn,
                        i.version as iv,
                        IFNULL(a.version, 'alien') AS av,
                        d.description AS desc
                        FROM local_packages AS i
                        LEFT JOIN remote_packages AS a
                        ON a.category = i.category
                        AND a.name = i.name
                        AND a.slot = i.slot
        				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                        WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                        AND av IS 'alien' ''',
        'available': f'''SELECT
                    a.category AS cat,
                    a.name AS pn,
                    i.version as iv,
                    a.version AS av,
                    d.description AS desc
                    FROM remote_packages AS a
                    LEFT JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
    				LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    AND iv IS NULL''',
        'upgradeable': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.version as iv,
                    a.version AS av,
                    d.description AS desc
                    FROM local_packages AS i
                    INNER JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
    				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    AND iv <> av'''
    }

    with sqlite3.connect(sisyphus.getFilesystem.localDatabase) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(SELECTS[filter])
        rows = cursor.fetchall()

    return rows

def tosql(string):
    return '%%' if string == '' else string.replace('*', '%').replace('?', '_')

def showSearch(filter, cat, pn, desc, single):
    print(f"Searching {filter} packages ... \n")
    pkglist = searchDB(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print("No package found!\nUse the '--ebuild' option to search for source packages!")
    else:
        if single:
            print(f"{'Package':45} {'Installed':20} Available")
        for pkg in pkglist:
            if not single:
                print(f"*  {pkg['cat']}/{pkg['pn']}")
                print(f"\tInstalled version: {pkg['iv']}")
                if pkg['av'] != 'alien':
                    print(f"\tLatest available version: {pkg['av']}")
                else:
                    print(f"\tAlien package: Use `sisyphus search --ebuild {pkg['pn']}` for available version!")
                print(f"\tDescription: {pkg['desc']}\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(f"{cpn:45} {str(pkg['iv']):20} {str(pkg['av'])}")
        print(f"\nFound {len(pkglist)} matching package(s) ...")

def cliExec(filter, cat, pn, desc, single):
    if sisyphus.checkEnvironment.root():
        sisyphus.updateAll.cliExec()
    else:
        print("\nYou are not root, cannot fetch updates.\nSearch result may be inaccurate!\n")

    showSearch(filter, cat, pn, desc, single)
