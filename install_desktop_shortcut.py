#!/usr/bin/env python3
"""Install (or replace) the Tiny Engineer launcher on Linux desktops."""
from __future__ import annotations
from pathlib import Path
import os
import shutil
import stat
import sys

ROOT = Path(__file__).resolve().parent
NAME = 'tiny-engineer-dashboard.desktop'


def desktop_quote(value: str | Path) -> str:
    """Quote an Exec argument according to the Desktop Entry specification."""
    # % is a field-code introducer even inside quoted Exec args.
    value = str(value).replace('%', '%%')
    # These characters must be escaped inside a double-quoted argument.
    for ch in ('\\', '"', '$', '`'):
        value = value.replace(ch, '\\' + ch)
    return '"' + value + '"'


def desktop_file() -> str:
    if not (ROOT / 'launch_dashboard.py').is_file():
        raise FileNotFoundError('Missing launch_dashboard.py; extract the whole V2.1 package.')
    # If installed in a project-local virtual environment, honor that Python.
    local_python = ROOT / '.venv' / 'bin' / 'python'
    interpreter = local_python if local_python.is_file() else Path(sys.executable).resolve()
    if not interpreter.is_file():
        fallback = shutil.which('python3')
        if not fallback:
            raise FileNotFoundError('Cannot find Python 3 to run the desktop launcher.')
        interpreter = Path(fallback)
    return '\n'.join([
        '[Desktop Entry]',
        'Version=1.0',
        'Type=Application',
        'Name=Tiny Engineer Desk Robot Studio',
        'GenericName=Local robotics build dashboard',
        'Comment=Open the local Tiny Engineer dashboard and beginner build guide',
        'Exec=' + desktop_quote(interpreter) + ' ' + desktop_quote(ROOT / 'launch_dashboard.py'),
        'Path=' + str(ROOT),
        'Icon=' + str(ROOT / 'app' / 'icon.svg'),
        'Terminal=false',
        'StartupNotify=false',
        'Categories=Development;Education;Utility;',
        '',
    ])


def write_launcher(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)


def main() -> None:
    data_home = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))).expanduser()
    apps = data_home / 'applications'
    entry = desktop_file()
    out = apps / NAME
    write_launcher(out, entry)
    print('Installed application menu shortcut:', out)

    desktop = Path.home() / 'Desktop'
    if desktop.is_dir():
        dest = desktop / NAME
        write_launcher(dest, entry)
        print('Installed desktop shortcut:', dest)
        # GNOME also tracks the allowed-to-launch state in metadata; best effort
        # only, because it can depend on the user's graphical session.
        gio = shutil.which('gio')
        if gio:
            import subprocess
            try:
                subprocess.run([gio, 'set', str(dest), 'metadata::trusted', 'true'],
                               check=False, capture_output=True, timeout=4)
            except (OSError, subprocess.TimeoutExpired):
                pass
        print('In GNOME Files, right-click the desktop shortcut and choose "Allow Launching" if prompted.')
    print('The installer has replaced the older shortcut of the same name.')
    print('Click the launcher to start the local server and open your browser.')
    print('If the browser does not open, view ~/.local/state/tiny-engineer-dashboard/launcher.log')
    print('Keep this extracted application folder in place; reinstall after moving it.')


if __name__ == '__main__':
    main()
