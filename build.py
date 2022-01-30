#!/usr/bin/python

import os
import sys
import getopt
import merge_bin_esp
import shutil
import htmlmin
import subprocess
from bs4 import BeautifulSoup


def shrinkHtml():

    directory = os.fsencode('src/pages/')

    for f in os.listdir(directory):
        filename = os.fsdecode(f)
        if filename.endswith(".html"):
            file = open(os.path.join(directory, f))
            html = file.read().replace("\n", " ")
            file.close()
            minified = htmlmin.minify(html, remove_empty_space=True)
            print(minified)
            with open(os.path.join(directory, f), "w") as myfile:
                myfile.write(minified)
            continue
        else:
            continue


def updateVersion(version):
    markup = open('src/pages/config.html', 'r')
    soup = BeautifulSoup(markup, 'html.parser')
    versionTag = soup.find("td", {"id": "version"})
    versionTag.string = version
    hashTag = soup.find("td", {"id": "hash"})
    hash = subprocess.check_output(['git','rev-parse','--short','HEAD'])
    hashTag.string = hash.decode("utf-8").strip()
    print(hashTag)
    with open("src/pages/config.html", "w") as file:
        file.write(str(soup))


def cleanAndBuild():
    try:
        shutil.rmtree('release')
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    os.system('platformio run -t clean')
    os.system('platformio run')


def copyAndRenameBinaries(version):
    merge_bin_esp.main(version)
    shutil.copyfile('.pio/build/esp32dev/firmware.bin',
                    'release/esp32nat_extended_v' + version + '.bin')


def buildRelease(version):
    updateVersion(version)
    shrinkHtml()
    cleanAndBuild()
    copyAndRenameBinaries(version)


def main(argv):
    version = ''
    try:
        opts, args = getopt.getopt(argv, "hi:version:", ["version="])
    except getopt.GetoptError:
        print('build.py -v <version>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('build.py -v <version>')
            sys.exit()
        elif opt in ("--version"):
            version = arg
    print('Version is <' + version + ">")
    buildRelease(version)


if __name__ == "__main__":
    main(sys.argv[1:])
