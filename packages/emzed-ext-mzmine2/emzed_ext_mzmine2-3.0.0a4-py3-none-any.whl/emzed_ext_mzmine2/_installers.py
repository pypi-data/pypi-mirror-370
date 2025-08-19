#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import functools
import io
import os
import shutil
import sys
import zipfile

import requests
from emzed.config import folders

from ._utils import default_install_target, download, unpack

JDK_ROOT = (
    "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11"
)

URLS = {
    "linux": f"{JDK_ROOT}/OpenJDK21U-jre_x64_linux_hotspot_21.0.5_11.tar.gz",
    "darwin": f"{JDK_ROOT}/OpenJDK21U-jre_aarch64_mac_hotspot_21.0.5_11.tar.gz",
    "win32": f"{JDK_ROOT}/OpenJDK21U-jre_x64_windows_hotspot_21.0.5_11.zip",
}

SUPPORTED_PLATFORMS = list(URLS.keys())

JVM_HOME_FILE = "jvm_home"


MZMINE2_URL = (
    "https://github.com/mzmine/mzmine2/releases/download/v2.41.2/MZmine-2.41.2.zip"
)

MZMINE2_HOME_FILE = "mzmine2_home"


def install_jre(platform=sys.platform):
    assert (
        platform in SUPPORTED_PLATFORMS
    ), f"platform must be one of {SUPPORTED_PLATFORMS}"

    target_folder = _default_jre_folder()
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    url = URLS[platform]
    target_path = os.path.join(target_folder, os.path.basename(url))

    if os.path.exists(target_path):
        print("jre is already installed")
        return

    print("download", url)
    download(url, target_path)

    print("unpack", target_path)
    unpacked_to = unpack(target_path)

    with open(os.path.join(target_folder, JVM_HOME_FILE), "w") as fh:
        fh.write(unpacked_to)


def install_mzmine2():
    target_folder = _default_mzmine2_folder()
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    target_path = os.path.join(target_folder, os.path.basename(MZMINE2_URL))

    if os.path.exists(target_path):
        print("mzmine2 is already installed")
        return

    print("download", MZMINE2_URL)
    download(MZMINE2_URL, target_path)

    print("unpack", target_path)
    result_folder = unpack(target_path)

    with open(os.path.join(target_folder, MZMINE2_HOME_FILE), "w") as fh:
        fh.write(result_folder)


def install_example_files(overwrite=False):
    folder = os.path.join(folders.get_document_folder(), "emzed3_examples")
    if not os.path.exists(folder):
        os.makedirs(folder)

    final_target = os.path.join(folder, "emzed_ext_mzmine2")
    if os.path.exists(final_target):
        if not overwrite:
            print(f"folder {final_target} already exists")
            return
        shutil.rmtree(final_target)

    url = (
        "https://gitlab.com/api/v4/projects/53555864/repository"
        "/archive.zip?path=example_scripts"
    )

    r = requests.get(url)
    r.raise_for_status()

    def extract_flat(fh, target):
        with zipfile.ZipFile(fh) as zf:
            for m in zf.filelist:
                if m.filename.endswith("/"):
                    # skip folders
                    continue
                # from https://stackoverflow.com/questions/4917284
                zip_info = zf.getinfo(m.filename)
                zip_info.filename = os.path.basename(m.filename)
                zf.extract(zip_info, target)

    extract_flat(io.BytesIO(r.content), final_target)

    print(f"donwloaded examples to {folder}")


def get_jre_home(folder=None):
    if folder is None:
        folder = _default_jre_folder()
    jvm_home_path = os.path.join(folder, JVM_HOME_FILE)
    if not os.path.exists(jvm_home_path):
        return None

    path = open(jvm_home_path).read().strip()
    if not os.path.exists(path):
        raise RuntimeError(f"file {jvm_home_path} contains invalid path {path}")

    return path


@functools.lru_cache()
def find_java_bin(folder=None):
    if folder is None:
        folder = _default_jre_folder()
    home = get_jre_home(folder)
    java_executable = "java.exe" if sys.platform == "win32" else "java"
    for folder, __, files in os.walk(home):
        if java_executable in files:
            return os.path.join(folder, java_executable)

    raise RuntimeError(f"can not find java within {home}")


def set_java_home():
    folder = _default_jre_folder()
    path = get_jre_home(folder)
    if path is None:
        raise RuntimeError("did not find jre, did you run download_jre()?")
    os.environ["JAVA_HOME"] = path


def get_mzmine2_home():
    folder = _default_mzmine2_folder()

    mzmine2_path = os.path.join(folder, MZMINE2_HOME_FILE)

    if not os.path.exists(mzmine2_path):
        return None

    path = open(mzmine2_path).read().strip()
    if not os.path.exists(path):
        raise RuntimeError(f"file {mzmine2_path} contains invalid path {path}")

    return path


def _default_jre_folder():
    return os.path.join(default_install_target(), "jre")


def _default_mzmine2_folder():
    return os.path.join(default_install_target(), "mzmine2")
