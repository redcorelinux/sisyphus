#!/usr/bin/python3

import os
import sys
import colorama
import subprocess
import gnupg
import time
import signal
import sisyphus.getfs
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

colorama.init()

KEY_PATH = os.path.join(
    '/usr',
    'share',
    'openpgp-keys',
    'gentoo-release.asc',
)


def log(message, color=None, gfx_ui=False, error=False):
    target = sys.stderr if error else sys.stdout
    if gfx_ui or not sys.stdout.isatty():
        print(message, file=target, flush=True)
    else:
        color_code = color if color else ""
        print(f"{color_code}{message}{Style.RESET_ALL}",
              file=target, flush=True)


def _verify_single_file(gpg, data_path, sig_path, authorized_fingerprint, gfx_ui):
    display_name = os.path.relpath(data_path, sisyphus.getfs.pkg_cache_dir)

    if not gfx_ui:
        c_ok = f"{Fore.GREEN}OK{Style.RESET_ALL}"
        c_fail = f"{Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL}"
        c_name = f"{Fore.MAGENTA}{display_name}{Style.RESET_ALL}"
    else:
        c_ok, c_fail, c_name = "OK", "FAIL", display_name

    try:
        with open(sig_path, 'rb') as f:
            result = gpg.verify_file(f, data_path)

        is_valid = result.valid and result.pubkey_fingerprint == authorized_fingerprint

        if is_valid:
            log(f"{c_ok}      {c_name}", gfx_ui=gfx_ui)
        else:
            log(f"{c_fail}    {c_name}", gfx_ui=gfx_ui)

        return is_valid, display_name
    except Exception as e:
        log(f"[ERROR] {display_name}: {str(e)}",
            color=Fore.YELLOW, gfx_ui=gfx_ui, error=True)
        return False, display_name


def binpkg_cache(authorized_fingerprint, gfx_ui=False, max_workers=None):
    cache_dir = sisyphus.getfs.pkg_cache_dir
    gpg = gnupg.GPG(gnupghome='/etc/portage/gnupg')
    tasks = []
    missing_sig = False
    failed_files = []

    for root, _, files in os.walk(cache_dir):
        for filename in files:
            if filename.endswith('.asc'):
                continue
            path = os.path.join(root, filename)
            sig_path = path + ".asc"

            if not os.path.exists(sig_path):
                log(f"[MISSING] {path}.asc",
                    color=Fore.YELLOW, gfx_ui=gfx_ui, error=True)
                missing_sig = True
            else:
                tasks.append((path, sig_path))

    if missing_sig:
        log("\n" + "="*60, color=Fore.RED, gfx_ui=gfx_ui)
        log(f"SECURITY ALERT: MISSING SIGNATURES IN '{cache_dir}'",
            color=Fore.RED, gfx_ui=gfx_ui)
        log("="*60, color=Fore.RED, gfx_ui=gfx_ui)
        if gfx_ui:
            for i in range(15, 0, -1):
                print(f"Killing application in: {i} seconds!", flush=True)
                time.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)
            os._exit(1)
        else:
            sys.exit(1)

    if not tasks:
        return

    overall_success = True
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            futures = {executor.submit(
                _verify_single_file, gpg, t[0], t[1], authorized_fingerprint, gfx_ui): t for t in tasks}

            for future in as_completed(futures):
                success, name = future.result()
                if not success:
                    overall_success = False
                    failed_files.append(name)
        except KeyboardInterrupt:
            executor.shutdown(wait=False, cancel_futures=True)
            sys.exit(1)

    if not overall_success:
        log("\n" + "="*60, color=Fore.RED, gfx_ui=gfx_ui)
        log("SECURITY ALERT: SIGNATURE VERIFICATION FAILED",
            color=Fore.RED, gfx_ui=gfx_ui)
        log("="*60, color=Fore.RED, gfx_ui=gfx_ui)
        for f in failed_files:
            log(f" -> {f} (Corrupted file)", gfx_ui=gfx_ui)

        if gfx_ui:
            for i in range(15, 0, -1):
                print(f"Killing application in: {i} seconds!", flush=True)
                time.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)
            os._exit(1)
        else:
            sys.exit(1)


def portage_tree(gfx_ui=False):
    tree = sisyphus.getfs.gentoo_ebuild_dir
    try:
        g_exec = subprocess.Popen(['gemato', 'verify', tree, '-s', '-K', KEY_PATH],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in g_exec.stdout:
            print(line, end='', flush=True)

        g_exec.wait()
        if g_exec.returncode != 0:
            log("\n" + "="*60, color=Fore.RED, gfx_ui=gfx_ui)
            log("SECURITY ALERT: SIGNATURE VERIFICATION FAILED",
                color=Fore.RED, gfx_ui=gfx_ui, error=True)
            log("="*60, color=Fore.RED, gfx_ui=gfx_ui)
            if gfx_ui:
                for i in range(15, 0, -1):
                    print(f"Killing application in: {i} seconds!", flush=True)
                    time.sleep(1)
                os.kill(os.getpid(), signal.SIGTERM)
                os._exit(1)
            else:
                sys.exit(g_exec.returncode)
    except KeyboardInterrupt:
        g_exec.terminate()
        try:
            g_exec.wait(1)
        except subprocess.TimeoutExpired:
            g_exec.kill()
        sys.exit(1)
