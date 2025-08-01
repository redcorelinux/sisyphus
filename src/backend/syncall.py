#!/usr/bin/python3

import animation
import colorama
import os
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getenv
import sisyphus.syncdb
import sisyphus.syncenv
from colorama import Fore, Back, Style

colorama.init()


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def sync_evrth():
    sisyphus.syncenv.g_repo()
    sisyphus.syncenv.r_repo()
    sisyphus.syncenv.p_cfg_repo()
    sisyphus.syncdb.rmt_tbl()


@animation.wait('fetching updates')
def start(gfx_ui=False):
    actv_brch = sisyphus.getenv.sys_brch()
    bhst_addr = sisyphus.getenv.bhst_addr()
    is_sane = sisyphus.checkenv.sanity()
    is_online = sisyphus.checkenv.connectivity()
    unread_count = sisyphus.checkenv.news()

    if is_online != 1:
        if gfx_ui:
            print("\nNo internet connection detected. Aborting!\n")
            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}\nNo internet connection detected; Aborting!\n{Style.RESET_ALL}")
            sys.exit()
    else:
        if is_sane == 1:
            sync_evrth()
            if gfx_ui:
                print(
                    f"\n\nThere are {unread_count} unread Redcore Linux Project news article(s).")
            else:
                if unread_count > 0:
                    print(
                        f"\n\nThere are {Fore.RED}{Style.BRIGHT}{unread_count}{Style.RESET_ALL} unread {Fore.WHITE}{Style.BRIGHT}Redcore Linux Project{Style.RESET_ALL} news article(s).")
                else:
                    print(
                        f"\n\nThere are {Fore.GREEN}{unread_count}{Style.RESET_ALL} unread {Fore.WHITE}{Style.BRIGHT}Redcore Linux Project{Style.RESET_ALL} news article(s).")
        else:
            if gfx_ui:
                if "packages-next" in bhst_addr:
                    print(f"\n\nThe active branch is '{actv_brch}' (stable)")
                    print(f"\n\nThe active binhost is '{bhst_addr}' (testing)")
                else:
                    print(f"\n\nThe active branch is '{actv_brch}' (testing)")
                    print(f"\n\nThe active binhost is '{bhst_addr}' (stable)")

                print("\nInvalid configuration!")
                print(
                    "\nUse the Sisyphus CLI command: 'sisyphus branch --help' for assistance; Aborting.\n")

                for i in range(9, 0, -1):
                    print(f"Killing application in : {i} seconds!")
                    time.sleep(1)

                os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
            else:
                if "packages-next" in bhst_addr:
                    print(
                        f"{Fore.GREEN}\n\nThe active branch is '{actv_brch}' (stable){Style.RESET_ALL}")
                    print(
                        f"{Fore.GREEN}The active binhost is '{bhst_addr}' (testing){Style.RESET_ALL}")
                else:
                    print(
                        f"{Fore.GREEN}\n\nThe active branch is '{actv_brch}' (testing){Style.RESET_ALL}")
                    print(
                        f"{Fore.GREEN}The active binhost is '{bhst_addr}' (stable){Style.RESET_ALL}")

                print(
                    f"{Fore.RED}{Style.BRIGHT}\nInvalid configuration!{Style.RESET_ALL}")
                print(
                    f"{FORE.WHITE}{Style.BRIGHT}\nUse 'sisyphus branch --help' for assistance; Aborting.{Style.RESET_ALL}\n")
                sys.exit()
