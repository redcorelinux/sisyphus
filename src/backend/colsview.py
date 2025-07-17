#!/usr/bin/python3

from colorama import Fore, Style
from shutil import get_terminal_size


def columnize_list(title, items, item_color, label):
    if not items:
        return

    max_item_length = max(len(item) for item in items)
    col_width = max(max_item_length + 4, 20)
    terminal_width = get_terminal_size().columns
    columns = max(1, terminal_width // col_width)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n")

    for i, pkg in enumerate(items, 1):
        print(f"{item_color}{pkg:<{col_width}}{Style.RESET_ALL}", end="")
        if i % columns == 0:
            print()
    if len(items) % columns != 0:
        print()

    print(
        f"\n{Fore.WHITE}{Style.BRIGHT}Total: {len(items)} {label} package(s){Style.RESET_ALL}\n"
    )


def print_packages(bin_list=None, src_list=None, rm_list=None):
    bin_list = bin_list or []
    src_list = src_list or []
    rm_list = rm_list or []

    columnize_list("These are the binary packages that would be merged, in order:",
                    bin_list, Fore.MAGENTA, "binary")
    columnize_list("These are the source packages that would be merged, in order:",
                    src_list, Fore.GREEN, "source")
    columnize_list("These are the selected packages that would be unmerged, in order:",
                    rm_list, Fore.BLUE, "selected")
