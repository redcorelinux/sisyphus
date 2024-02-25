#!/usr/bin/python3

import animation
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.getenv
import sisyphus.purgeenv
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
            print("\n\nNo internet connection; Aborting!\n")
            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            sys.exit(app.exec_())  # kill GUI window
        else:
            print(sisyphus.getclr.bright_red +
                  "\n\nNo internet connection; Aborting!\n" + sisyphus.getclr.reset)
            sys.exit()
    else:
        if is_sane == 1:
            sync_evrth()
        else:
            if gfx_ui:
                if "packages-next" in bhst_addr:
                    print("\n\nActive branch:" + " " + "'" +
                          actv_brch + "'" + " " + "(stable)")
                    print("\n\nActive binhost:" + " " + "'" +
                          bhst_addr + "'" + " " + "(testing)")
                else:
                    print("\n\nActive branch:" + " " + "'" +
                          actv_brch + "'" + " " + "(testing)")
                    print("\n\nActive binhost:" + " " + "'" +
                          bhst_addr + "'" + " " + "(stable)")

                print("\n\nInvalid configuration!")
                print("\nUse 'sisyphus branch --help' for help\n")
                for i in range(9, 0, -1):
                    print(f"Killing application in : {i} seconds!")
                    time.sleep(1)

                sys.exit(app.exec_())  # kill GUI window
            else:
                if "packages-next" in bhst_addr:
                    print(sisyphus.getclr.green + "\n\nActive branch:" + " " +
                          sisyphus.getclr.reset + "'" + actv_brch + "'" + " " + "(stable)")
                    print(sisyphus.getclr.green + "\nActive binhost:" + " " +
                          sisyphus.getclr.reset + "'" + bhst_addr + "'" + " " + "(testing)")
                else:
                    print(sisyphus.getclr.green + "\n\nActive branch:" + " " +
                          sisyphus.getclr.reset + "'" + actv_brch + "'" + " " + "(testing)")
                    print(sisyphus.getclr.green + "\nActive binhost:" + " " +
                          sisyphus.getclr.reset + "'" + bhst_addr + "'" + " " + "(stable)")

                print(sisyphus.getclr.bright_red +
                      "\n\nInvalid configuration!" + sisyphus.getclr.reset)
                print(sisyphus.getclr.bright_yellow + "\nUse" + sisyphus.getclr.reset + " " + "'" +
                      "sisyphus branch --help" + "'" + " " + sisyphus.getclr.bright_yellow + "for help" + sisyphus.getclr.reset)
                time.sleep(1)
                sys.exit()
