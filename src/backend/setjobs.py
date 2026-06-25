#!/usr/bin/python3

import os
import sisyphus.getfs

makeopts_file_path = os.path.join(
    sisyphus.getfs.sisyphus_cfg_dir, 'sisyphus.make-opts.conf')


def get_ncpus():
    return os.cpu_count() or 1


def smt_active():
    try:
        with open("/sys/devices/system/cpu/smt/active") as f:
            return f.read().strip() == "1"
    except FileNotFoundError:
        return False


def adjust_makeopts():
    n_cpus = get_ncpus()
    phys_cores = n_cpus // 2 if smt_active() else n_cpus

    src_jobs = phys_cores
    src_load = phys_cores

    bin_jobs = 4 if phys_cores > 4 else phys_cores
    bin_load = phys_cores

    comments = []
    if os.path.exists(makeopts_file_path):
        with open(makeopts_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("#"):
                    comments.append(line)

    new_content = "".join(comments)
    if new_content and not new_content.endswith("\n"):
        new_content += "\n"

    new_content += "\n"
    new_content += f'MAKEOPTS="-j{src_jobs} -l{src_load}"\n'
    new_content += f'EMERGE_DEFAULT_OPTS="${{EMERGE_DEFAULT_OPTS}} --jobs={bin_jobs} --load-average={bin_load}"\n'

    with open(makeopts_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def start():
    adjust_makeopts()
