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
            print(
                f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} is already marked as {sisyphus.getclr.bright_green}read{sisyphus.getclr.reset}.")
        else:
            r_news_index.append(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} marked as {sisyphus.getclr.bright_green}read{sisyphus.getclr.reset}.")
    else:
        print(
            f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} doesn't exist.")


def mark_unread(article_nr):
    n_news = ld_n_news()

    if 1 <= article_nr <= len(n_news):
        article_index = article_nr - 1
        r_news_index = ld_r_news()

        if article_index not in r_news_index:
            print(
                f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} is already marked as {sisyphus.getclr.bright_red}unread{sisyphus.getclr.reset}.")
        else:
            r_news_index.remove(article_index)
            save_r_news(r_news_index)
            print(
                f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} marked as {sisyphus.getclr.bright_red}unread{sisyphus.getclr.reset}.")
    else:
        print(
            f"\nArticle {sisyphus.getclr.bright_white}{article_nr}{sisyphus.getclr.reset} doesn't exist.")


def list_all_news():
    n_news = ld_n_news()
    r_news_index = ld_r_news()

    for index, news in enumerate(n_news):
        status = f"{sisyphus.getclr.bright_green}Read{sisyphus.getclr.reset}" if index in r_news_index else f"{sisyphus.getclr.bright_red}Unread{sisyphus.getclr.reset}"
        print(
            f"\n{sisyphus.getclr.bright_yellow}Article {sisyphus.getclr.bright_white}{index + 1}{sisyphus.getclr.reset} ({status}):\n\n{news}")


def start(list=False, read=False, unread=False, article_nr=None):
    if list:
        list_all_news()

    if read:
        if article_nr is not None:
            mark_read(article_nr)

    if unread:
        if article_nr is not None:
            mark_unread(article_nr)
