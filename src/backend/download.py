#!/usr/bin/python3

import os
import pickle
import shutil
import wget
import sisyphus.getcolor
import sisyphus.getenv
import sisyphus.getfs


def pkg(pkgname):
    binhostURL = sisyphus.getenv.binhostURL()
    areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

    for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
        print(">>> Downloading binary" + "(" + sisyphus.getcolor.bright_yellow + "{}".format(index) + sisyphus.getcolor.reset + " " + "of" + " " + sisyphus.getcolor.bright_yellow +
              str(len(areBinaries)) + sisyphus.getcolor.reset + ")" + " " + sisyphus.getcolor.magenta + binary.replace('.tbz2', ' ') + sisyphus.getcolor.reset)
        wget.download(binhostURL + binary)
        print("")

        if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(
                sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
        else:
            os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir,
                        binary.rstrip().split("/")[0]))
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(
                sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

        if os.path.exists(binary.rstrip().split("/")[1]):
            os.remove(binary.rstrip().split("/")[1])


def world():
    binhostURL = sisyphus.getenv.binhostURL()
    areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
        print(">>> Downloading binary" + "(" + sisyphus.getcolor.bright_yellow + "{}".format(index) + sisyphus.getcolor.reset + " " + "of" + " " + sisyphus.getcolor.bright_yellow +
              str(len(areBinaries)) + sisyphus.getcolor.reset + ")" + " " + sisyphus.getcolor.magenta + binary.replace('.tbz2', ' ') + sisyphus.getcolor.reset)
        wget.download(binhostURL + binary)
        print("")

        if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(
                sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
        else:
            os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir,
                        binary.rstrip().split("/")[0]))
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(
                sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

        if os.path.exists(binary.rstrip().split("/")[1]):
            os.remove(binary.rstrip().split("/")[1])
