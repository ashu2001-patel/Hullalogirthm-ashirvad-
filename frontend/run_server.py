#!/usr/bin/env python3
import http.server
import socketserver
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 5000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"")
    print(f"========================================")
    print(f"GEOSPATIAL FRONTEND RUNNING")
    print(f"========================================")
    print(f"")
    print(f"OPEN IN BROWSER: http://127.0.0.1:{PORT}")
    print(f"")
    print(f"API Backend:  http://127.0.0.1:8001")
    print(f"API Docs:     http://127.0.0.1:8001/docs")
    print(f"")
    httpd.serve_forever()
