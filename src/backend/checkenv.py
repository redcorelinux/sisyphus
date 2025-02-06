#!/usr/bin/python3

import os
import re
import subprocess
import sisyphus.getenv
import sisyphus.getfs
import sisyphus.getnews
import urllib.request
from urllib.error import HTTPError


NETWORK_CHECK_URL_FILE = os.path.join(
    sisyphus.getfs.s_cfg_dir, "sisyphus.net_chk_addr.conf")


def is_valid_url(url):
    regex = re.compile(
        r'^(http|https)://'
        r'([a-zA-Z0-9.-]+)'
        r'(\.[a-zA-Z]{2,})'
        r'(:\d+)?'
        r'(/.*)?$'
    )
    return re.match(regex, url) is not None


def connectivity():
    is_online = int()
    default_url = "https://redcorelinux.org"

    try:
        with open(NETWORK_CHECK_URL_FILE, "r") as file:
            url = file.readline().strip()

        if not url:
            url = default_url

        elif not is_valid_url(url):
            url = default_url

    except FileNotFoundError:
        url = default_url

    try:
        urllib.request.urlopen(url, timeout=5)
        is_online = int(1)

    except HTTPError as e:
        if e.code == 429:
            is_online = int(1)  # ignore rate limiting errors
        else:
            is_online = int(1)  # ignore all other http errors

    except urllib.error.URLError:
        is_online = int(0)

    return is_online


def root():
    return True if os.getuid() == 0 else False


def news():
    n_news = sisyphus.getnews.ld_n_news()
    r_news_index = sisyphus.getnews.ld_r_news()

    unread_count = len(n_news) - len(r_news_index)

    return unread_count


def sanity():
    actv_brch = sisyphus.getenv.sys_brch()
    bhst_addr = sisyphus.getenv.bhst_addr()
    is_sane = int()

    if "packages-next" in bhst_addr:
        if actv_brch == "next":
            is_sane = int(1)
        else:
            is_sane = int(0)
    else:
        if actv_brch == "master":
            is_sane = int(1)
        else:
            is_sane = int(0)

    return is_sane
