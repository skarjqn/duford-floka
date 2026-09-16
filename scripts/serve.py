"""Run locally when the project owner opens START-WINDOWS.cmd."""
import functools
import http.server
import threading
import webbrowser
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'site'
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
with http.server.ThreadingHTTPServer(('127.0.0.1',8080),handler) as server:
    print('Floka: http://127.0.0.1:8080/  (Ctrl+C to stop)',flush=True)
    threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:8080/')).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
