#!/usr/bin/python3

import colorama
import os
import sisyphus.getfs
from colorama import Fore, Back, Style

colorama.init()

NEWS_DIR = "news"

N_NEWS_FILE = os.path.join(sisyphus.getfs.p_cfg_dir,
                           os.path.join(NEWS_DIR, "n_news.txt"))
R_NEWS_FILE = os.path.join(sisyphus.getfs.s_cfg_dir,
                           os.path.join(NEWS_DIR, "r_news.txt"))
DELIMITER = "---"


def ld_n_news():
    with open(N_NEWS_FILE, "r") as file:
        content = file.read()
        articles = content.split(DELIMITER)
        return [article.strip() for article in articles if article.strip()]


def ld_r_news():
    try:
        with open(R_NEWS_FILE, "r") as file:
            return [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        return []


def save_r_news(r_news):
    with open(R_NEWS_FILE, "w") as file:
        for index in r_news:
            file.write(f"{index}\n")


def mark_read(article_nr):
    n_news = ld_n_news()

    if 1 <= article_nr <= len(n_news):
        article_index = article_nr - 1
        r_news_index = ld_r_news()

        if article_index in r_news_index:
            print(
                f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} is already marked as {Fore.GREEN}{Style.BRIGHT}read{Style.RESET_ALL}.")
        else:
            r_news_index.append(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} marked as {Fore.GREEN}{Style.BRIGHT}read{Style.RESET_ALL}.")
    else:
        print(
            f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} doesn't exist.")


def mark_unread(article_nr):
    n_news = ld_n_news()

    if 1 <= article_nr <= len(n_news):
        article_index = article_nr - 1
        r_news_index = ld_r_news()

        if article_index not in r_news_index:
            print(
                f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} is already marked as {Fore.RED}{Style.BRIGHT}unread{Style.RESET_ALL}.")
        else:
            r_news_index.remove(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} marked as {Fore.RED}{Style.BRIGHT}unread{Style.RESET_ALL}.")
    else:
        print(
            f"\nArticle {Fore.WHITE}{Style.BRIGHT}{article_nr}{Style.RESET_ALL} doesn't exist.")


def list_all_news():
    n_news = ld_n_news()
    r_news_index = ld_r_news()

    for index, news in enumerate(n_news):
        status = f"{Fore.GREEN}{Style.BRIGHT}Read{Style.RESET_ALL}" if index in r_news_index else f"{Fore.RED}{Style.BRIGHT}Unread{Style.RESET_ALL}"
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}Article {index + 1}{Style.RESET_ALL} ({status}):\n\n{news}")


def start(list=False, read=False, unread=False, article_nr=None):
    if list:
        list_all_news()

    if read:
        if article_nr is not None:
            mark_read(article_nr)

    if unread:
        if article_nr is not None:
            mark_unread(article_nr)
