#!/usr/bin/env python3
"""Ubuntu .desktop entry target: resilient server startup + browser opening.

This is deliberately a short-lived launcher. The HTTP server is started in a
separate process group, so it survives the launcher closing. Detailed startup
logs are saved in ~/.local/state/tiny-engineer-dashboard/ (or XDG_STATE_HOME).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
SERVICE = 'tiny-engineer-dashboard'
VERSION = '2.1'


def state_dir() -> Path:
    base = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local' / 'state'))).expanduser()
    path = base / SERVICE
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def log(message: str) -> None:
    entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {message}\n"
    path = state_dir() / 'launcher.log'
    with path.open('a', encoding='utf-8') as f:
        f.write(entry)
    print(entry, end='', flush=True)


def health(port: int) -> bool:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=0.65) as response:
            j = json.load(response)
            return bool(j.get('ok') and j.get('service') == SERVICE and j.get('version') == VERSION and j.get('root') == str(ROOT))
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        return False


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(('127.0.0.1', port)) == 0


def start_or_reuse_server() -> tuple[int, int | None]:
    if not (ROOT / 'start_dashboard.py').is_file() or not (ROOT / 'app' / 'server.py').is_file():
        raise RuntimeError(f'Dashboard files are missing from {ROOT}. Extract the entire ZIP first.')
    try:
        preferred = int(os.environ.get('TINY_ENGINEER_PORT', '8782'))
    except ValueError as e:
        raise RuntimeError('TINY_ENGINEER_PORT must be a port number.') from e
    if not (1024 <= preferred <= 65525):
        raise RuntimeError('TINY_ENGINEER_PORT must be between 1024 and 65525.')

    # Repeated icon clicks open the already-running V2.1 instance, avoiding
    # an Address already in use crash. Older versions are not mistaken for V2.1.
    candidates = range(preferred, preferred + 10)
    for port in candidates:
        if health(port):
            log(f'Reusing running V2.1 dashboard at http://127.0.0.1:{port}/')
            return port, None

    for port in candidates:
        if port_in_use(port):
            log(f'Port {port} is occupied by another process; trying next port.')
            continue
        server_log = state_dir() / 'server.log'
        log(f'Starting server on port {port}, from {ROOT}')
        with server_log.open('ab') as fout:
            child = subprocess.Popen(
                [sys.executable, str(ROOT / 'start_dashboard.py'), '--port', str(port), '--no-browser'],
                stdin=subprocess.DEVNULL, stdout=fout, stderr=subprocess.STDOUT,
                cwd=ROOT, start_new_session=True, close_fds=True,
            )
        for _ in range(75):
            if health(port):
                log(f'Server ready at http://127.0.0.1:{port}/ (PID {child.pid})')
                return port, child.pid
            if child.poll() is not None:
                log(f'Server failed with exit code {child.returncode}; consult {server_log}')
                break
            time.sleep(.12)
        else:
            log(f'Server timed out on port {port}; consult {server_log}')
            if child.poll() is None:
                child.terminate()
                try: child.wait(timeout=2)
                except subprocess.TimeoutExpired: child.kill()
        # Try a different port only when our process immediately exited or
        # could not claim the expected address.
    raise RuntimeError('Could not start dashboard. Read server.log for details.')


def open_browser(port: int) -> None:
    url = f'http://127.0.0.1:{port}/'
    # Desktop session should supply DISPLAY or WAYLAND_DISPLAY. xdg-open is
    # the GNOME/XFCE/KDE-friendly default browser command.
    commands = []
    if shutil.which('xdg-open'):
        commands.append(['xdg-open', url])
    if shutil.which('gio'):
        commands.append(['gio', 'open', url])
    for command in commands:
        try:
            result = subprocess.run(command, timeout=7, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, check=False)
            if result.returncode == 0:
                log(f'Browser opener accepted {url} via {command[0]}')
                return
            log(f'{command[0]} exited with {result.returncode}; trying alternative.')
        except (OSError, subprocess.TimeoutExpired) as exc:
            log(f'Browser opener failed: {type(exc).__name__}; trying alternative.')
    import webbrowser
    if webbrowser.open(url):
        log(f'Browser opened using Python webbrowser at {url}')
    else:
        log(f'No working graphical browser opener. Open {url} manually.')
        # Never discard the server just because there is no graphical session.


def main() -> int:
    try:
        port, _ = start_or_reuse_server()
        open_browser(port)
        return 0
    except Exception as exc:
        try:
            log(f'LAUNCH FAILED: {type(exc).__name__}: {exc}')
        except OSError:
            print(f'Tiny Engineer launch failed: {exc}', file=sys.stderr)
        notification = shutil.which('notify-send')
        if notification and (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
            try:
                subprocess.Popen([notification, 'Tiny Engineer failed to start',
                                  f'Please see {state_dir() / "launcher.log"}'],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
            except OSError:
                pass
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
