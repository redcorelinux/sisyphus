#!/usr/bin/python3

import sisyphus
import sqlite3

def searchDB(filter, cat = '', pn = '', desc = ''):
    NOVIRT = "AND cat NOT LIKE 'virtual'"
    SELECTS = {
        'all': f'''SELECT
                    i.category AS cat,
                    i.name as pn,
                    i.version as iv,
                    IFNULL(a.version, 'None') AS av,
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
        'local': f'''SELECT
                        i.category AS cat,
                        i.name AS pn,
                        i.version as iv,
                        a.version AS av,
                        d.description AS desc
                        FROM local_packages AS i
                        LEFT JOIN remote_packages AS a
                        ON a.category = i.category
                        AND a.name = i.name
                        AND a.slot = i.slot
        				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                        WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                        AND av IS NULL''',
        'remote': f'''SELECT
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
        'upgrade': f'''SELECT
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

    with sqlite3.connect(sisyphus.filesystem.localDatabase) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(SELECTS[filter])
        rows = cursor.fetchall()

    return rows

def tosql(string):
    return '%%' if string == '' else string.replace('*', '%').replace('?', '_')

def showSearch(filter, cat, pn, desc, single = False):
    print(f"Searching for {filter} packages ...\n")
    pkglist = searchDB(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print("No binary package found!")
    else:
        for pkg in pkglist:
            if not single:
                print(f"*  {pkg['cat']}/{pkg['pn']}")
                print(f"\tInstalled version: {pkg['iv']}")
                print(f"\tLatest available version: {pkg['av']}")
                print(f"\tDescription: {pkg['desc']}\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(f"{cpn:45} i:{str(pkg['iv']):20} a:{str(pkg['av'])}")
        print(f"\nFound {len(pkglist)} binary package(s)")

    print("To search for source packages, use the '--ebuild' option.")
