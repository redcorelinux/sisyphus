#!/usr/bin/python3

import animation
import io
import subprocess

@animation.wait('resolving dependencies')
def package(pkgname):
    areBinaries = []
    areSources = []
    needsConfig = int()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stderr, encoding="utf-8"):
        if "The following keyword changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in portageOutput.rstrip():
            needsConfig = int(1)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "[binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "[ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)

    portageExec.wait()
    return areBinaries,areSources,needsConfig

@animation.wait('resolving dependencies')
def world():
    areBinaries = []
    areSources = []
    needsConfig = int()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stderr, encoding="utf-8"):
        if "The following keyword changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in portageOutput.rstrip():
            needsConfig = int(1)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "[binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "[ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)

    portageExec.wait()
    return areBinaries,areSources,needsConfig
