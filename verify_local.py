#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serve bellarich-site/ over http and run verify_check.run() against it."""
import functools
import http.server
import socketserver
import threading
import json
import sys

import verify_check

ROOT = '/workspace/bellarich-site'
PORT = 8765

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
Handler.log_message = lambda *a, **k: None
httpd = socketserver.TCPServer(('127.0.0.1', PORT), Handler)
httpd.allow_reuse_address = True
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()

try:
    rep = verify_check.run(f'http://127.0.0.1:{PORT}/check/', True)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
finally:
    httpd.shutdown()
