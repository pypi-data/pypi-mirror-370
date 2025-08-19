#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import os
import shutil
import sys

import emzed.config
import pytest

from emzed_ext_mzmine2._installers import (
    get_mzmine2_home,
    install_example_files,
    install_jre,
    install_mzmine2,
    set_java_home,
)

is_ci_server = os.environ.get("CI") is not None


@pytest.fixture(scope="function")
def monkey_patch_document_folder(monkeypatch, tmp_path):
    monkeypatch.setattr(
        emzed.config.folders, "get_document_folder", lambda: str(tmp_path)
    )
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture(scope="function")
def monkey_patch_emzed_folder(monkeypatch, tmp_path):
    monkeypatch.setattr(emzed.config.folders, "get_emzed_folder", lambda: str(tmp_path))
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.mark.skipif(not is_ci_server, reason="only runs on ci server")
def test_install_jre(monkey_patch_emzed_folder):
    install_jre(sys.platform)

    set_java_home()
    try:
        assert os.environ["JAVA_HOME"] is not None
    finally:
        del os.environ["JAVA_HOME"]


@pytest.mark.skipif(not is_ci_server, reason="only runs on ci server")
def test_install_mzmine2(monkey_patch_emzed_folder):
    assert get_mzmine2_home() is None
    install_mzmine2()
    assert get_mzmine2_home() is not None


@pytest.mark.skipif(is_ci_server, reason="only runs locally")
def test_install_jre_local():
    install_jre(sys.platform)
    set_java_home()
    assert os.environ["JAVA_HOME"] is not None


@pytest.mark.skipif(is_ci_server, reason="only runs locally")
def test_install_mzmine2_local():
    install_mzmine2()
    assert "lib" in os.listdir(get_mzmine2_home())


def test_install_examples(monkey_patch_document_folder, regtest):
    install_example_files()
    print(
        sorted(
            p.name
            for p in (
                monkey_patch_document_folder / "emzed3_examples" / "emzed_ext_mzmine2"
            ).iterdir()
        ),
        file=regtest,
    )
