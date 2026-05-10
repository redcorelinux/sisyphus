#!/usr/bin/python3

import colorama
import signal
import sqlite3
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getfs
import sisyphus.querydb
from colorama import Fore, Style

colorama.init()


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def tosql(value):
    if isinstance(value, list):
        return [tosql(v) for v in value]
    if value == '':
        return '%%'
    return str(value).replace('*', '%').replace('?', '_')


def srch_db(filter, cat='', pn='', desc=''):
    results = []

    with sqlite3.connect(sisyphus.getfs.local_db) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        if isinstance(pn, list):
            for name in pn:
                query = sisyphus.querydb.start(
                    filter, tosql(cat), tosql(name), tosql(desc))
                cursor.execute(query)
                results.extend(cursor.fetchall())
        else:
            query = sisyphus.querydb.start(
                filter, tosql(cat), tosql(pn), tosql(desc))
            cursor.execute(query)
            results = cursor.fetchall()

    return results


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
    if filter == 'ebuild':
        pkgnames = [pn] if isinstance(pn, str) else pn
        print(
            f"\nSearching {Fore.WHITE}{Style.BRIGHT}source{Style.RESET_ALL} packages...\n")
        subprocess.call(['emerge', '--search', '--getbinpkg'] + pkgnames)
        return

    if sisyphus.checkenv.root():
        msg = f"Tip: Run {Fore.CYAN}'sisyphus update'{Style.RESET_ALL} first to ensure search results are accurate."
    else:
        msg = f"Note: Search results may be inaccurate. Run {Fore.CYAN}'sisyphus update'{Style.RESET_ALL} as root first to refresh the database."

    print(f"\n{msg}\n")
    srch_rslt(filter, cat, pn, desc, single)
