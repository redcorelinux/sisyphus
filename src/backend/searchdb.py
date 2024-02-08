#!/usr/bin/python3

import signal
import sqlite3
import subprocess
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.getfs
import sisyphus.update


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def srch_db(filter, cat='', pn='', desc=''):
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


def srch_rslt(filter, cat, pn, desc, single):
    print("\nSearching" + sisyphus.getclr.bright_yellow + " " +
          f"{filter}" + " " + sisyphus.getclr.reset + "packages ..." + "\n")
    pkglist = srch_db(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print(sisyphus.getclr.bright_red +
              "No binary package found!\n" + sisyphus.getclr.reset)
        print(sisyphus.getclr.bright_yellow + "Use the" + sisyphus.getclr.reset + " " + "'" + "--ebuild" +
              "'" + " " + sisyphus.getclr.bright_yellow + "option to search source packages" + sisyphus.getclr.reset)
        print(sisyphus.getclr.bright_yellow + "Use" + sisyphus.getclr.reset + " " + "'" +
              "sisyphus search --help" + "'" + " " + sisyphus.getclr.bright_yellow + "for help" + sisyphus.getclr.reset)
    else:
        if single:
            print(sisyphus.getclr.green +
                  f"{'Package category/name':45} {'Installed version':20} {'Latest available version':30} {'Description'}" + sisyphus.getclr.reset)
        for pkg in pkglist:
            if not single:
                print(sisyphus.getclr.bright_green + "*" + " " + sisyphus.getclr.reset +
                      sisyphus.getclr.bright_white + f"{pkg['cat']}/{pkg['pn']}" + sisyphus.getclr.reset)
                print(sisyphus.getclr.green + "\tInstalled version:" +
                      " " + sisyphus.getclr.reset + f"{pkg['iv']}")
                if pkg['av'] != 'alien':
                    print(sisyphus.getclr.green + "\tLatest available version:" +
                          " " + sisyphus.getclr.reset + f"{pkg['av']}")
                else:
                    print(sisyphus.getclr.green + "\tAlien package:" + " " + sisyphus.getclr.reset +
                          "Use `sisyphus search --ebuild" + " " + f"{pkg['pn']}`" + " " + "for available version!")
                print(sisyphus.getclr.green + "\tDescription:" + " " +
                      sisyphus.getclr.reset + f"{pkg['desc']}" + "\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(sisyphus.getclr.bright_white + f"{cpn:45}" + " " + sisyphus.getclr.reset +
                      f"{str(pkg['iv']):20}" + " " + f"{str(pkg['av']):30}" + " " + f"{str(pkg['desc'])}")
        print("\nFound" + " " + sisyphus.getclr.bright_yellow +
              f"{len(pkglist)}" + " " + sisyphus.getclr.reset + "matching package(s) ...")


def start(filter, cat, pn, desc, single):
    if sisyphus.checkenv.root():
        print(sisyphus.getclr.bright_red +
              "\nSearching as root, database can be updated!\n" + sisyphus.getclr.reset)
        print(sisyphus.getclr.bright_yellow +
              "Search results will be accurate\n" + sisyphus.getclr.reset)
        while True:
            user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                               "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
            if user_input.lower() in ['yes', 'y', '']:
                sisyphus.update.start(gfx_ui=False)
                break
            elif user_input.lower() in ['no', 'n']:
                print(sisyphus.getclr.bright_red +
                      "\nSkipping database update, displaying search results!\n" + sisyphus.getclr.reset)
                print(sisyphus.getclr.bright_yellow +
                      "Search results may be inaccurate" + sisyphus.getclr.reset)
                break
            else:
                continue
    else:
        print(sisyphus.getclr.bright_red +
              "\nSearching as user, database cannot be updated!\n" + sisyphus.getclr.reset)
        print(sisyphus.getclr.bright_yellow +
              "Search results may be inaccurate" + sisyphus.getclr.reset)

    srch_rslt(filter, cat, pn, desc, single)


def estart(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
