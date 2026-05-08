#!/usr/bin/python3

import os
import sys
import pickle
import requests
import signal
from concurrent.futures import ThreadPoolExecutor
from email.utils import formatdate, parsedate_to_datetime
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
from rich.console import Console

import sisyphus.getfs
import sisyphus.getenv

console = Console()


def sigint_handler(signal, frame):
    console.print("\n[bold red]Interrupted. Exiting...[/bold red]")
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def get_headers(path):
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        return {'If-Modified-Since': formatdate(mtime, usegmt=True)}
    return {}


def dl_index_files(session, pkg_root, base_url):
    index_files = ["Packages", "Packages.gz",
                   "Packages.asc", "Packages.gz.asc"]

    for filename in index_files:
        url = f"{base_url}/{filename}"
        local_path = os.path.join(pkg_root, filename)

        try:
            with session.get(url, headers=get_headers(local_path), timeout=10) as r:
                if r.status_code == 200:
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(r.content)

                    if 'Last-Modified' in r.headers:
                        mtime = parsedate_to_datetime(
                            r.headers['Last-Modified']).timestamp()
                        os.utime(local_path, (mtime, mtime))

                    console.print(
                        f">>> Fetching package index: [magenta]{filename}[/magenta]")
                elif r.status_code == 304:
                    console.print(
                        f">>> Skipping package index: [magenta]{filename}[/magenta]")
        except Exception as e:
            console.print(f"[red]Error fetching index {filename}: {e}[/red]")


def dl_binpkg(session, package_name, current_count, total_count, pkg_root, base_url, progress):
    pkg_name = f"{package_name}.gpkg.tar"
    asc_name = f"{package_name}.gpkg.tar.asc"
    local_pkg_path = os.path.join(pkg_root, pkg_name)
    local_asc_path = os.path.join(pkg_root, asc_name)
    pkg_url = f"{base_url}/{pkg_name}"
    asc_url = f"{base_url}/{asc_name}"

    progress_prefix = (f">>> Fetching ([bold yellow]{current_count}[/bold yellow] "
                       f"of [bold yellow]{total_count}[/bold yellow]) "
                       f"[magenta]{pkg_name}[/magenta]")

    try:
        with session.get(pkg_url, headers=get_headers(local_pkg_path), stream=True, timeout=20) as r:
            if r.status_code == 200:
                os.makedirs(os.path.dirname(local_pkg_path), exist_ok=True)
                total_size = int(r.headers.get('content-length', 0))
                task_id = progress.add_task(progress_prefix, total=total_size)

                with open(local_pkg_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=131072):
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))

                progress.remove_task(task_id)

                if 'Last-Modified' in r.headers:
                    remote_mtime = parsedate_to_datetime(
                        r.headers['Last-Modified']).timestamp()
                    os.utime(local_pkg_path, (remote_mtime, remote_mtime))

                progress.console.print(
                    f"{progress_prefix}: [green]Fetch completed[/green]")

            elif r.status_code == 304:
                progress.console.print(
                    f"{progress_prefix}: [green]Fetch skipped[/green]")
            else:
                progress.console.print(
                    f"{progress_prefix}: [red]Failed (HTTP {r.status_code})[/red]")
                return

        with session.get(asc_url, headers=get_headers(local_asc_path), timeout=10) as r_asc:
            if r_asc.status_code == 200:
                with open(local_asc_path, 'wb') as f_asc:
                    f_asc.write(r_asc.content)

                if 'Last-Modified' in r_asc.headers:
                    asc_mtime = parsedate_to_datetime(
                        r_asc.headers['Last-Modified']).timestamp()
                    os.utime(local_asc_path, (asc_mtime, asc_mtime))

            elif r_asc.status_code == 304:
                pass

    except Exception as e:
        progress.console.print(
            f"{progress_prefix}: [bold red]Error ({e})[/bold red]")


def start(dl_world=False, max_workers=4):
    pkg_root = sisyphus.getfs.pkg_cache_dir
    base_url = sisyphus.getenv.binpkg_addr()

    if not base_url:
        console.print(
            "[bold red]Error: Could not resolve URL address.[/bold red]")
        return

    metadata_dir = sisyphus.getfs.pkg_metadata_dir
    pickle_name = "sisyphus_worlddeps.pickle" if dl_world else "sisyphus_pkgdeps.pickle"
    file_path = os.path.join(metadata_dir, pickle_name)

    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: {file_path} not found.[/bold red]")
        return

    with open(file_path, "rb") as f:
        bin_list = pickle.load(f)[0]

    total_packages = len(bin_list)

    with requests.Session() as session:
        dl_index_files(session, pkg_root, base_url)

        with Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=30),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
            refresh_per_second=10
        ) as progress:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for index, package in enumerate(bin_list, start=1):
                    executor.submit(dl_binpkg, session, package, index, total_packages,
                                    pkg_root, base_url, progress)
