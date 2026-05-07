#!/usr/bin/python3

import os
import sys
import sisyphus.getfs
import sisyphus.getenv


def getList():
    mirrorList = []
    files = [(sisyphus.getfs.binhostcfg, 'BINHOST (DEPRECATED)'),
             (sisyphus.getfs.binreposcfg, 'BINREPOS (CURRENT)')]

    for path, ftype in files:
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            for line in f:
                url = None
                if ftype == 'BINHOST (DEPRECATED)' and 'PORTAGE_BINHOST=' in line:
                    url = line.split("=", 1)[1].replace(
                        '"', '').replace("'", "").strip()
                elif ftype == 'BINREPOS (CURRENT)' and 'sync-uri =' in line:
                    url = line.split("=", 1)[1].strip()

                if url:
                    branch = "testing" if "packages-next" in url else "stable"
                    mirrorList.append({
                        'isActive': not line.strip().startswith('#'),
                        'Url': url,
                        'Type': ftype,
                        'Branch': branch
                    })
    return mirrorList


def printList():
    mirrorList = getList()
    for i, m in enumerate(mirrorList):
        status = "[*]" if m['isActive'] else "[ ]"
        print(
            f"{i+1:2} {status} {m['Type']:20} | {m['Branch'].upper():7} | {m['Url']}")


def writeList(file_path, target_url, activate, is_legacy):
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        clean = line.strip()

        # --- BINHOST (DEPRECATED) logic ---
        if is_legacy:
            if 'PORTAGE_BINHOST=' in line and target_url in line:
                if activate:
                    new_lines.append(line.lstrip('# ').strip() + "\n")
                else:
                    new_lines.append(("# " + line.lstrip())
                                     if not clean.startswith('#') else line)
            else:
                new_lines.append(line)
            continue

        # --- BINREPOS (CURRENT) logic ---
        if 'sync-uri =' in line and target_url in line:
            cursor = len(new_lines) - 1
            while cursor >= 0:
                prev = new_lines[cursor].strip()
                if 'sync-uri =' in prev:
                    break
                if prev.startswith('[') or (prev.startswith('#') and '[' in prev):
                    if activate:
                        new_lines[cursor] = prev.lstrip('# ').strip() + "\n"
                    else:
                        if not prev.startswith('#'):
                            new_lines[cursor] = "# " + prev + "\n"
                    break
                cursor -= 1

            if activate:
                new_lines.append(line.lstrip('# ').strip() + "\n")
            else:
                new_lines.append(("# " + line.lstrip())
                                 if not clean.startswith('#') else line)

        elif 'location =' in line:
            last_line = new_lines[-1] if new_lines else ""
            if target_url in last_line:
                if activate:
                    new_lines.append(line.lstrip('# ').strip() + "\n")
                else:
                    new_lines.append(("# " + line.lstrip())
                                     if not clean.startswith('#') else line)
            else:
                if not activate:
                    new_lines.append(("# " + line.lstrip())
                                     if not clean.startswith('#') else line)
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)


def setActive(index):
    mirrors = getList()
    if not (1 <= index <= len(mirrors)):
        print(f"\nError: Index {index} is out of range.\n")
        return

    selection = mirrors[index - 1]
    sys_branch = "testing" if sisyphus.getenv.system_branch() == "next" else "stable"

    for m in mirrors:
        is_legacy = (m['Type'] == 'BINHOST (DEPRECATED)')
        cfg_path = sisyphus.getfs.binhostcfg if is_legacy else sisyphus.getfs.binreposcfg
        writeList(cfg_path, m['Url'], False, is_legacy)

    base_host = selection['Url'].replace(
        'packages-next/', '').replace('packages/', '')

    target_mirror = None
    for m in mirrors:
        if m['Type'] == selection['Type'] and m['Branch'] == sys_branch:
            if base_host in m['Url']:
                target_mirror = m
                break

    if target_mirror:
        is_legacy = (target_mirror['Type'] == 'BINHOST (DEPRECATED)')
        cfg_path = sisyphus.getfs.binhostcfg if is_legacy else sisyphus.getfs.binreposcfg
        writeList(cfg_path, target_mirror['Url'], True, is_legacy)
