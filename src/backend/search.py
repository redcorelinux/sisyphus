#!/usr/bin/python3

import sqlite3
import subprocess
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.getfs
import sisyphus.update


def searchDB(filter, cat='', pn='', desc=''):
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
        'upgradable': f'''SELECT
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

    with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(SELECTS[filter])
        rows = cursor.fetchall()

    return rows


def tosql(string):
    return '%%' if string == '' else string.replace('*', '%').replace('?', '_')


def showSearch(filter, cat, pn, desc, single):
    print("Searching" + sisyphus.getcolor.bright_yellow + " " +
          f"{filter}" + " " + sisyphus.getcolor.reset + "packages ..." + "\n")
    pkglist = searchDB(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print(sisyphus.getcolor.bright_red +
              "No binary package found!\n" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow + "Use the" + sisyphus.getcolor.reset + " " + "'" + "--ebuild" +
              "'" + " " + sisyphus.getcolor.bright_yellow + "option to search source packages" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow +
              "Use" + sisyphus.getcolor.reset + " " + "'" + "sisyphus search --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)
    else:
        if single:
            print(sisyphus.getcolor.green +
                  f"{'Package category/name':45} {'Installed version':20} {'Latest available version':30} {'Description'}" + sisyphus.getcolor.reset)
        for pkg in pkglist:
            if not single:
                print(sisyphus.getcolor.bright_green + "*" + " " + sisyphus.getcolor.reset +
                      sisyphus.getcolor.bright_white + f"{pkg['cat']}/{pkg['pn']}" + sisyphus.getcolor.reset)
                print(sisyphus.getcolor.green + "\tInstalled version:" +
                      " " + sisyphus.getcolor.reset + f"{pkg['iv']}")
                if pkg['av'] != 'alien':
                    print(sisyphus.getcolor.green + "\tLatest available version:" +
                          " " + sisyphus.getcolor.reset + f"{pkg['av']}")
                else:
                    print(sisyphus.getcolor.green + "\tAlien package:" + " " + sisyphus.getcolor.reset +
                          "Use `sisyphus search --ebuild" + " " + f"{pkg['pn']}`" + " " + "for available version!")
                print(sisyphus.getcolor.green + "\tDescription:" + " " +
                      sisyphus.getcolor.reset + f"{pkg['desc']}" + "\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(sisyphus.getcolor.bright_white + f"{cpn:45}" + " " + sisyphus.getcolor.reset +
                      f"{str(pkg['iv']):20}" + " " + f"{str(pkg['av']):30}" + " " + f"{str(pkg['desc'])}")
        print("\nFound" + " " + sisyphus.getcolor.bright_yellow +
              f"{len(pkglist)}" + " " + sisyphus.getcolor.reset + "matching package(s) ...")


def start(filter, cat, pn, desc, single):
    if sisyphus.checkenv.root():
        sisyphus.update.start()
    else:
        print(sisyphus.getcolor.bright_red + "\nYou don't have root permissions, cannot update the database!\n" +
              sisyphus.getcolor.reset + sisyphus.getcolor.bright_yellow + "\nSearch results may be inaccurate" + sisyphus.getcolor.reset)

    showSearch(filter, cat, pn, desc, single)


def estart(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
