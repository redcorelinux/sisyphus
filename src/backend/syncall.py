#!/usr/bin/python3

import animation
import os
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.getenv
import sisyphus.syncdb
import sisyphus.syncenv


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

    if is_online != 1:
        if gfx_ui:
            print("\nNo internet connection detected. Aborting!\n")
            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
        else:
            print(
                f"{sisyphus.getclr.bright_red}\nNo internet connection detected; Aborting!\n{sisyphus.getclr.reset}")
            sys.exit()
    else:
        if is_sane == 1:
            sync_evrth()
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
                        f"{sisyphus.getclr.green}\n\nThe active branch is '{actv_brch}' (stable){sisyphus.getclr.reset}")
                    print(
                        f"{sisyphus.getclr.green}The active binhost is '{bhst_addr}' (testing){sisyphus.getclr.reset}")
                else:
                    print(
                        f"{sisyphus.getclr.green}\n\nThe active branch is '{actv_brch}' (testing){sisyphus.getclr.reset}")
                    print(
                        f"{sisyphus.getclr.green}The active binhost is '{bhst_addr}' (stable){sisyphus.getclr.reset}")

                print(
                    f"{sisyphus.getclr.bright_red}\nInvalid configuration!{sisyphus.getclr.reset}")
                print(
                    f"{sisyphus.getclr.bright_yellow}\nUse{sisyphus.getclr.reset} 'sisyphus branch --help' for assistance; Aborting.\n")
                sys.exit()
