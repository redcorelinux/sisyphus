#!/usr/bin/python3

import atexit
import io
import os
import subprocess
import pickle
import sisyphus.getfs
import sisyphus.killemerge


def pkgbinpkgonly():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly',
                              '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList))
    p_exe.wait()


def pkgbinpkg():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--fetchonly',
                              '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList))
    p_exe.wait()


def xpkgbinpkgonly():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly', '--rebuilt-binaries',
                              '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, p_exe)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        print(p_out.rstrip())

    p_exe.wait()


def worldbinpkgonly():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly',
                              '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList))
    p_exe.wait()


def worldbinpkg():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--fetchonly',
                              '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList))
    p_exe.wait()


def xworldbinpkgonly():
    fetchList = []
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    for index, binary in enumerate(['=' + package for package in bin_list]):
        fetchList.append(binary)

    p_exe = subprocess.Popen(['emerge', '--nodeps', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly', '--rebuilt-binaries',
                              '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(fetchList), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, p_exe)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        print(p_out.rstrip())

    p_exe.wait()
