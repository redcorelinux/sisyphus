#!/usr/bin/python3

import colorama
import signal
import sqlite3
import subprocess
import sisyphus.checkenv
import sisyphus.getfs
import sisyphus.querydb
import sisyphus.syncall
from colorama import Fore, Back, Style

colorama.init()


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
        f"\nSearching {Fore.WHITE}{Style.BRIGHT}{filter}{Style.RESET_ALL} packages...\n")
    pkglist = srch_db(filter, tosql(cat), tosql(pn), tosql(desc))

    if len(pkglist) == 0:
        print(
            f"{Fore.RED}{Style.BRIGHT}No matching packages have been identified!{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{Style.BRIGHT}Use the '{'--ebuild'}' option to search source packages{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{Style.BRIGHT}Use '{'sisyphus search --help'}' for assistance{Style.RESET_ALL}")
    else:
        if single:
            print(f"{Fore.GREEN}{'Package category/name':<45} {'Installed version':<20} {'Latest available version':<30} {'Description'}{Style.RESET_ALL}")
        for pkg in pkglist:
            if not single:
                print(
                    f"{Fore.GREEN}{Style.BRIGHT}*{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} {pkg['cat']}/{pkg['pn']}{Style.RESET_ALL}")
                print(
                    f"{Fore.GREEN}\tInstalled version: {Style.RESET_ALL}{pkg['iv']}")
                if pkg['av'] != 'alien':
                    print(
                        f"{Fore.GREEN}\tLatest available version: {Style.RESET_ALL}{pkg['av']}")
                else:
                    print(
                        f"{Fore.GREEN}\tAlien package: {Style.RESET_ALL}Use 'sisyphus search --ebuild {pkg['pn']}' for available version!")
                print(
                    f"{Fore.GREEN}\tDescription: {Style.RESET_ALL}{pkg['desc']}\n")
            else:
                cpn = f"{pkg['cat']}/{pkg['pn']}"
                print(
                    f"{Fore.WHITE}{Style.BRIGHT}{cpn:45}{Style.RESET_ALL} {str(pkg['iv']):<20} {str(pkg['av']):<30} {str(pkg['desc'])}")
        print(f"\n{len(pkglist)} matching packages have been identified.")


def start(filter, cat, pn, desc, single):
    if sisyphus.checkenv.root():
        print(f"{Fore.RED}{Style.BRIGHT}Searching as root allows database updates. {Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT}Search results would be accurate.{Style.RESET_ALL}")
        while True:
            user_input = input(
                f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
            if user_input.lower() in ['yes', 'y', '']:
                sisyphus.syncall.start(gfx_ui=False)
                break
            elif user_input.lower() in ['no', 'n']:
                print(f"{Fore.RED}{Style.BRIGHT}Skipping database update; displaying search results.{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT}Search results may not be accurate.{Style.RESET_ALL}")
                break
            else:
                continue
    else:
        print(f"{Fore.RED}{Style.BRIGHT}Searching as user does not allow database updates.{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT}Search results may not be accurate.{Style.RESET_ALL}")

    srch_rslt(filter, cat, pn, desc, single)


def estart(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
