#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv
import sisyphus.getnews
import urllib.request


def connectivity():
    is_online = int()

    try:
        urllib.request.urlopen("http://www.google.com", timeout=5)
        is_online = int(1)
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
