#!/usr/bin/python3

import animation
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getcolor
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
            print(sisyphus.getcolor.bright_red +
                  "\n\nNo internet connection; Aborting!\n" + sisyphus.getcolor.reset)
            sys.exit()
    else:
        if is_sane == 1:
            sync_evrth()
        else:
            if "packages-next" in bhst_addr:
                print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + actv_brch + "'" + " " + "(stable)" +
                      " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + bhst_addr + "'" + " " + "(testing)")
            else:
                print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + actv_brch + "'" + " " + "(testing)" +
                      " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + bhst_addr + "'" + " " + "(stable)")

            if gfx_ui:
                print("\n\nInvalid configuration!")
                print("Use 'sisyphus branch --help' for help\n")
                for i in range(9, 0, -1):
                    print(f"Killing application in : {i} seconds!")
                    time.sleep(1)

                sys.exit(app.exec_())  # kill GUI window
            else:
                print(sisyphus.getcolor.bright_red + "\n\nInvalid configuration!" + sisyphus.getcolor.reset + sisyphus.getcolor.bright_yellow + "\nUse" +
                      sisyphus.getcolor.reset + " " + "'" + "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)
                sys.exit()
