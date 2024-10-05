#!/usr/bin/python3

import os
import sisyphus.getclr
import sisyphus.getfs

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
            print(f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} is already marked as {sisyphus.getclr.green}read{sisyphus.getclr.reset}.")
        else:
            r_news_index.append(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} marked as {sisyphus.getclr.green}read{sisyphus.getclr.reset}.")
    else:
        print(
            f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} doesn't exist.")


def mark_unread(article_nr):
    n_news = ld_n_news()

    if 1 <= article_nr <= len(n_news):
        article_index = article_nr - 1
        r_news_index = ld_r_news()

        if article_index not in r_news_index:
            print(f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} is already marked as {sisyphus.getclr.green}unread{sisyphus.getclr.reset}.")
        else:
            r_news_index.remove(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} marked as {sisyphus.getclr.green}unread{sisyphus.getclr.reset}.")
    else:
        print(
            f"\nArticle {sisyphus.getclr.green}{article_nr}{sisyphus.getclr.reset} doesn't exist.")


def list_all_news():
    n_news = ld_n_news()
    r_news_index = ld_r_news()

    for index, news in enumerate(n_news):
        status = "Read" if index in r_news_index else "Unread"
        print(
            f"\nArticle {sisyphus.getclr.green}{index + 1}{sisyphus.getclr.reset} ({status}):\n{news}")


def check_n_news():
    n_news = ld_n_news()
    r_news_index = ld_r_news()

    unread_count = len(n_news) - len(r_news_index)

    if unread_count > 0:
        print(
            f"\nThere are {sisyphus.getclr.bright_red}{unread_count}{sisyphus.getclr.reset} unread news article(s).")
    else:
        print(
            f"\nThere are {sisyphus.getclr.green}{unread_count}{sisyphus.getclr.reset} unread news article(s).")


def start(check=False, list=False, read=False, unread=False, article_nr=None):
    if check:
        check_n_news()

    if list:
        list_all_news()

    if read:
        if article_nr is not None:
            mark_read(article_nr)
        else:
            print("\nError: No article number provided to mark as read.")

    if unread:
        if article_nr is not None:
            mark_unread(article_nr)
        else:
            print("\nError: No article number provided to mark as unread.")
