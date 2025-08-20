#!/usr/bin/env python3
import os
import sys
import traceback
from mitmproxy.tools.main import mitmdump
import importlib.resources


def run_proxy(listen_port=8080, addon_path=None, ignore_hosts=None, mode="regular"):
    """
    Starts the mitmproxy proxy with the given parameters.
    """
    if addon_path is None:
        try:
            # Use importlib.resources to get the path to the addon file
            with importlib.resources.path("interceptor", "interceptor_addon.py") as addon_file:
                addon = str(addon_file)
        except Exception:
            # Fallback to local path if running in source tree
            base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)
            addon = os.path.join(base, "interceptor", "interceptor_addon.py")
    else:
        addon = addon_path

    ignore = ignore_hosts or r"(^|\.)dev-gliner\.zerotrusted\.ai$|(^|\.)dev-history\.zerotrusted\.ai$"

    try:
        mitmdump([
            "--mode", mode,
            "--listen-port", str(listen_port),
            "--ignore-hosts", ignore,
            "-s", addon
        ])
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code != 0:
            print(f"\nmitmdump exited with code {code}")
        raise
    except Exception:
        print("\nUnhandled exception:")
        traceback.print_exc()