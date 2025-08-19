#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import os
import sys

import pytest

from emzed.config import folders

is_ci_server = os.environ.get("CI") is not None


def test_import():
    import emzed_ext_mzmine2

    emzed_ext_mzmine2.init()


def test_plugin():
    import emzed_ext_mzmine2 as mzm  # noqa: 401


def test_inital_import(monkeypatch, tmpdir):

    monkeypatch.setattr(folders, "get_emzed_folder", lambda: tmpdir.strpath)
    if "emzed_ext_mzmine2" in sys.modules:
        del sys.modules["emzed_ext_mzmine2"]
    import emzed_ext_mzmine2  # noqa: 401

    with pytest.raises(ImportError):
        emzed_ext_mzmine2.pick_peaks

    assert dir(emzed_ext_mzmine2) == ["init"]

    tmpdir.remove(ignore_errors=True)


@pytest.mark.skipif(not is_ci_server, reason="only runs on ci server")
def test_init(monkeypatch, tmpdir):
    monkeypatch.setattr(folders, "get_emzed_folder", lambda: tmpdir.strpath)
    if "emzed_ext_mzmine2" in sys.modules:
        del sys.modules["emzed_ext_mzmine2"]
    import emzed_ext_mzmine2  # noqa: 401

    emzed_ext_mzmine2.init()

    tmpdir.remove(ignore_errors=True)
