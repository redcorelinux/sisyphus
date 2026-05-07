#!/usr/bin/python3

import colorama
import os
import sys
import pickle
import requests
import signal

from colorama import Fore, Back, Style
from tqdm import tqdm
from email.utils import formatdate, parsedate_to_datetime

import sisyphus.getfs
import sisyphus.getenv

colorama.init()


def sigint_handler(signal, frame):
    print(Style.RESET_ALL)
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def dl_binpkg(package_name, current_count, total_count, pkg_root, base_url):
    pkg_name = f"{package_name}.gpkg.tar"
    asc_name = f"{package_name}.gpkg.tar.asc"
    local_pkg_path = os.path.join(pkg_root, pkg_name)
    local_asc_path = os.path.join(pkg_root, asc_name)

    pkg_url = f"{base_url}/{pkg_name}"
    asc_url = f"{base_url}/{asc_name}"

    progress_prefix = (f">>> Fetching ({Fore.YELLOW}{Style.BRIGHT}{current_count}{Style.RESET_ALL} "
                       f"of {Fore.YELLOW}{Style.BRIGHT}{total_count}{Style.RESET_ALL}) "
                       f"{Fore.MAGENTA}{pkg_name}{Style.RESET_ALL}")

    headers = {}

    if os.path.exists(local_pkg_path):
        mtime = os.path.getmtime(local_pkg_path)
        headers['If-Modified-Since'] = formatdate(mtime, usegmt=True)

    try:
        with requests.get(pkg_url, headers=headers, stream=True, timeout=20) as r:
            if r.status_code == 304:
                print(
                    f"{progress_prefix}: {Fore.GREEN}Up to date (Skipped){Style.RESET_ALL}")
                return

            if r.status_code == 200:
                os.makedirs(os.path.dirname(local_pkg_path), exist_ok=True)
                total_size = int(r.headers.get('content-length', 0))

                with open(local_pkg_path, 'wb') as f, tqdm(
                    desc=progress_prefix,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                    leave=True,
                    ascii=" >>",
                    bar_format='{desc} {percentage:3.0f}% [ {bar:30} ] {n_fmt}/{total_fmt} {rate_fmt}'
                ) as bar:
                    for chunk in r.iter_content(chunk_size=65536):
                        size = f.write(chunk)
                        bar.update(size)

                if 'Last-Modified' in r.headers:
                    remote_mtime = parsedate_to_datetime(
                        r.headers['Last-Modified']).timestamp()
                    os.utime(local_pkg_path, (remote_mtime, remote_mtime))

                try:
                    asc_res = requests.get(asc_url, timeout=10)
                    if asc_res.status_code == 200:
                        with open(local_asc_path, 'wb') as f_asc:
                            f_asc.write(asc_res.content)
                        if 'Last-Modified' in asc_res.headers:
                            asc_mtime = parsedate_to_datetime(
                                asc_res.headers['Last-Modified']).timestamp()
                            os.utime(local_asc_path, (asc_mtime, asc_mtime))
                except requests.RequestException:
                    pass

            else:
                print(
                    f"{progress_prefix}: {Fore.RED}Failed (HTTP {r.status_code}){Style.RESET_ALL}")

    except Exception as e:
        print(f"{progress_prefix}: {Fore.RED}Error ({e}){Style.RESET_ALL}")


def start(dl_world=False, gfx_ui=False):
    pkg_root = sisyphus.getfs.pkg_cache_dir
    base_url = sisyphus.getenv.binpkg_addr()

    if not base_url:
        print(
            f"{Fore.RED}Error: Could not resolve BINHOST/BINREPOS address.{Style.RESET_ALL}")
        return

    metadata_dir = sisyphus.getfs.pkg_metadata_dir
    pickle_name = "sisyphus_worlddeps.pickle" if dl_world else "sisyphus_pkgdeps.pickle"
    file_path = os.path.join(metadata_dir, pickle_name)

    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: {file_path} not found.{Style.RESET_ALL}")
        return

    with open(file_path, "rb") as f:
        bin_list = pickle.load(f)[0]

    total_packages = len(bin_list)

    for index, package in enumerate(bin_list, start=1):
        dl_binpkg(package, index, total_packages, pkg_root, base_url)
