#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import os
import subprocess
import sys
import threading
import time

from ._exceptions import MzMine2Exception
from ._installers import find_java_bin, get_mzmine2_home


def construct_java_call_cli_args():

    java_bin = find_java_bin()
    mzmine2_home = get_mzmine2_home()

    here = os.path.dirname(os.path.abspath(__file__))

    sep = ";" if sys.platform == "win32" else ":"

    class_path = sep.join(
        [
            os.path.join(mzmine2_home, "lib", "*"),
            os.path.join(here, "java", "extensions.jar"),
        ]
    )

    if sys.platform == "win32":
        class_path = class_path.replace("/", "\\\\")

    return [java_bin, "-Djava.awt.headless=true", "-ea", "-cp", class_path]


def run_java(class_name, *args):
    cli = (
        construct_java_call_cli_args()
        + ["ch.ethz.id.sis.emzed." + class_name]
        + list(map(str, args))
    )

    p = subprocess.Popen(
        cli, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )

    alive = True

    def send_alive():
        """we send every 500 ms a send alive token to the java process, so that this
        can detect if we, the python parent process is still alive.
        this is needed on windows when the user shuts down python because the
        mzmine tool takes to long. without this a zombie java process continues
        working and eats up resources
        """

        nonlocal alive
        while alive:
            try:
                p.stdin.write(str(time.time()).encode("ascii"))
                p.stdin.write(b"\n")
                p.stdin.flush()
            except OSError:
                print()
                print("p.stdin closed")
                sys.stdout.flush()
                break

            time.sleep(0.5)
            sys.stdout.flush()
        print()
        print("shutdown send alive token")
        sys.stdout.flush()

    threading.Timer(0, send_alive).start()

    def print_progress(dt=5):
        """prints a dot every dt seconds unless alive is set to False"""
        nonlocal alive
        while True:
            s = time.time()
            while alive and time.time() < s + dt:
                time.sleep(0.1)
            if not alive:
                break
            sys.stdout.write(".")
            sys.stdout.flush()
        print()
        sys.stdout.flush()

    threading.Timer(0, print_progress).start()

    def shutdown(*a):
        nonlocal alive
        alive = False

    try:
        for line in iter(p.stdout.readline, b""):
            line = str(line, "utf-8").rstrip()
            print(line)
            if line.startswith("!!!ERROR"):
                raise MzMine2Exception("calling java failed")
            if line.startswith("!!!DONE"):
                break
    except KeyboardInterrupt:
        raise
    finally:
        shutdown()

    p.wait()
    if p.returncode == 42:
        raise RuntimeError("java tool assumed python is dead")
    if p.returncode:
        cli = " ".join(cli)
        raise MzMine2Exception(f"java call {cli} failed")
