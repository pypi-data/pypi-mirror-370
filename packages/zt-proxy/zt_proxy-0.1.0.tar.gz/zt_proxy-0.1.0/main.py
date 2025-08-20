#!/usr/bin/env python3
import os
import sys
import traceback
from mitmproxy.tools.main import mitmdump


def run_proxy(listen_port=8080, addon_path=None, ignore_hosts=None, mode="regular"):
    """
    Starts the mitmproxy proxy with the given parameters.
    """
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)
    addon = addon_path or os.path.join(base, "interceptor", "interceptor_addon.py")
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