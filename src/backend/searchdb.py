#!/usr/bin/python3

import signal
import sqlite3
import subprocess
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.getfs
import sisyphus.querydb
import sisyphus.syncall


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def srch_db(filter, cat='', pn='', desc=''):
    query = sisyphus.querydb.start(filter, cat, pn, desc)

    with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

    return rows


def tosql(string):
    return '%%' if string == '' else string.replace('*', '%').replace('?', '_')


def srch_rslt(filter, cat, pn, desc, single):
    print(
        f"\nSearching {sisyphus.getclr.bright_yellow}{filter}{sisyphus.getclr.reset} packages...\n")
    pkglist = srch_db(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print(
            f"{sisyphus.getclr.bright_red}No matching packages have been identified!{sisyphus.getclr.reset}")
        print(f"{sisyphus.getclr.bright_yellow}Use the '{'--ebuild'}' option to search source packages{sisyphus.getclr.reset}")
        print(f"{sisyphus.getclr.bright_yellow}Use '{'sisyphus search --help'}' for assistance{sisyphus.getclr.reset}")
    else:
        if single:
            print(f"{sisyphus.getclr.green}{'Package category/name':<45} {'Installed version':<20} {'Latest available version':<30} {'Description'}{sisyphus.getclr.reset}")
        for pkg in pkglist:
            if not single:
                print(
                    f"{sisyphus.getclr.bright_green}*{sisyphus.getclr.reset}{sisyphus.getclr.bright_white} {pkg['cat']}/{pkg['pn']}{sisyphus.getclr.reset}")
                print(
                    f"{sisyphus.getclr.green}\tInstalled version: {sisyphus.getclr.reset}{pkg['iv']}")
                if pkg['av'] != 'alien':
                    print(
                        f"{sisyphus.getclr.green}\tLatest available version: {sisyphus.getclr.reset}{pkg['av']}")
                else:
                    print(
                        f"{sisyphus.getclr.green}\tAlien package: {sisyphus.getclr.reset}Use 'sisyphus search --ebuild {pkg['pn']}' for available version!")
                print(
                    f"{sisyphus.getclr.green}\tDescription: {sisyphus.getclr.reset}{pkg['desc']}\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(
                    f"{sisyphus.getclr.bright_white}{cpn:45}{sisyphus.getclr.reset} {str(pkg['iv']):<20} {str(pkg['av']):<30} {str(pkg['desc'])}")
        print(f"\n{len(pkglist)} matching packages have been identified.")


def start(filter, cat, pn, desc, single):
    if sisyphus.checkenv.root():
        print(f"{sisyphus.getclr.bright_red}Searching as root allows database updates. {sisyphus.getclr.reset}\n{sisyphus.getclr.bright_yellow}Search results will be accurate.{sisyphus.getclr.reset}")
        while True:
            user_input = input(
                f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
            if user_input.lower() in ['yes', 'y', '']:
                sisyphus.syncall.start(gfx_ui=False)
                break
            elif user_input.lower() in ['no', 'n']:
                print(f"{sisyphus.getclr.bright_red}Skipping database update; displaying search results.{sisyphus.getclr.reset}\n{sisyphus.getclr.bright_yellow}Search results may be inaccurate.{sisyphus.getclr.reset}")
                break
            else:
                continue
    else:
        print(f"{sisyphus.getclr.bright_red}Searching as a user does not allow database updates.{sisyphus.getclr.reset}\n{sisyphus.getclr.bright_yellow}Search results may be inaccurate.{sisyphus.getclr.reset}")

    srch_rslt(filter, cat, pn, desc, single)


def estart(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
