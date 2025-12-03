#!/usr/bin/python3

import os
import re
import sisyphus.getfs

makeopts_file_path = os.path.join(
    sisyphus.getfs.s_cfg_dir, 'sisyphus.make-opts.conf')


def get_ncpus():
    return os.cpu_count() or 1


def smt_active():
    try:
        with open("/sys/devices/system/cpu/smt/active") as f:
            return f.read().strip() == "1"
    except FileNotFoundError:
        return False


def makeopts_line(jobs):
    return f'MAKEOPTS="-j{jobs}"\n'


def adjust_makeopts():
    n_cpus = get_ncpus()
    new_jobs = n_cpus // 2 if smt_active() else n_cpus

    with open(makeopts_file, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'(MAKEOPTS="-j)(\d+)(")'

    def repl(match):
        return f'{match.group(1)}{new_jobs}{match.group(3)}'

    if re.search(pattern, content):
        updated = re.sub(pattern, repl, content)
    else:
        updated = content
        if not content.endswith("\n"):
            updated += "\n"
        updated += makeopts_line(new_jobs)

    if updated != content:
        with open(makeopts_file, "w", encoding="utf-8") as f:
            f.write(updated)
    else:
        pass  # MAKEOPTS already optimised


def start():
    adjust_makeopts()
