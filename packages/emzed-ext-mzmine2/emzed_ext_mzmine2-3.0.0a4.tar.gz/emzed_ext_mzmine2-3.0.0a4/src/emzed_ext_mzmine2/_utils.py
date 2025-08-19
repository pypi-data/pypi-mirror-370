#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import os
import shutil
import tarfile
import tempfile
import zipfile

import requests
from emzed.config import folders

tempfolder = os.environ.get("CI_TMP")


def default_install_target():
    from . import __version__

    if tempfolder is not None:
        return tempfolder
    return os.path.join(folders.get_emzed_folder(), "emzed.ext.mzmine2", __version__)


def download(url, target_path):
    with requests.get(url, stream=True) as r:
        with open(target_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)


def unpack(archive_path):
    if archive_path.endswith(".zip"):
        return _unpack_zip(archive_path)
    elif archive_path.endswith(".tar.gz"):
        return _unpack_tar_gz(archive_path)
    else:
        raise ValueError(f"don't know how to unpack {archive_path}")


def _unpack_zip(archive_path):
    target_folder = os.path.dirname(archive_path)

    zf = zipfile.ZipFile(archive_path)
    zf.extractall(target_folder)
    return os.path.join(target_folder, zf.filelist[0].filename)


def _unpack_tar_gz(archive_path, target_folder=None):
    if target_folder is None:
        target_folder = os.path.dirname(archive_path)
    with tarfile.open(archive_path, "r:gz") as tf:
        tf.extractall(path=target_folder)

        for member in tf.members:
            if not member.name.startswith("."):
                break
        else:
            raise RuntimeError(f"invalid archive {archive_path}")

        return os.path.join(target_folder, member.name)


class MkTempWithCleanup:
    def __init__(self):
        self._paths = []

    def __call__(self, extension):
        path = tempfile.mktemp(extension)
        self._paths.append(path)
        return path

    def cleanup(self):
        for p in self._paths:
            try:
                os.remove(p)
            except IOError:
                pass


def cleanup_temp_files(function):
    def wrapped(*a, **kw):
        mktemp = MkTempWithCleanup()
        function.__globals__["mktemp"] = mktemp
        try:
            return function(*a, **kw)
        finally:
            mktemp.cleanup()

    return wrapped
