"""Desktop launcher regression: real detached HTTP server with fake xdg-open.

Does not touch the user's home, applications, browser, or project database.
"""
from pathlib import Path
import json
import os
import re
import shutil
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import unittest
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]


def unused_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        return s.getsockname()[1]


class DesktopLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='tiny-launcher-test-')
        base=Path(self.tmp.name)
        self.home=base/'home'
        self.home.mkdir()
        (self.home/'Desktop').mkdir()
        self.install_dir=base/'Project with spaces'
        self.install_dir.mkdir()
        for filename in ('install_desktop_shortcut.py','launch_dashboard.py','start_dashboard.py'):
            shutil.copy2(ROOT/filename,self.install_dir/filename)
        shutil.copytree(ROOT/'app',self.install_dir/'app',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        self.bin=base/'bin'
        self.bin.mkdir()
        fake=self.bin/'xdg-open'
        fake.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> "$FAKE_OPEN_LOG"\nexit 0\n')
        fake.chmod(0o755)
        self.fake_opens=base/'browser_opens.log'
        self.port=unused_port()
        self.env=os.environ.copy()
        self.env.update({'HOME':str(self.home),'XDG_DATA_HOME':str(self.home/'.local/share'),
                         'XDG_STATE_HOME':str(self.home/'.local/state'),
                         'TINY_ENGINEER_PORT':str(self.port),
                         'FAKE_OPEN_LOG':str(self.fake_opens),
                         'PATH':str(self.bin)+os.pathsep+self.env.get('PATH','')})
        self.servers=[]

    def tearDown(self):
        log=self.home/'.local/state/tiny-engineer-dashboard/launcher.log'
        if log.is_file():
            for pid in set(int(x) for x in re.findall(r'\(PID (\d+)\)',log.read_text())):
                try:os.kill(pid,signal.SIGTERM)
                except ProcessLookupError:pass
        self.tmp.cleanup()

    def installer(self):
        result=subprocess.run([sys.executable,str(self.install_dir/'install_desktop_shortcut.py')],
                              cwd=self.install_dir,env=self.env,text=True,capture_output=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        path=self.home/'.local/share/applications/tiny-engineer-dashboard.desktop'
        self.assertTrue(path.exists())
        desktop_copy=self.home/'Desktop/tiny-engineer-dashboard.desktop'
        self.assertEqual(path.read_bytes(),desktop_copy.read_bytes())
        self.assertTrue(os.access(desktop_copy,os.X_OK))
        entry=path.read_text()
        self.assertIn('Terminal=false',entry)
        self.assertIn('Name=Tiny Engineer Desk Robot Studio',entry)
        exec_line=next(x[5:] for x in entry.splitlines() if x.startswith('Exec='))
        command=shlex.split(exec_line)
        self.assertEqual(command[0],sys.executable)
        self.assertEqual(command[1],str(self.install_dir/'launch_dashboard.py'))
        return command

    def test_launcher_from_installed_shortcut_reuses_server(self):
        command=self.installer()
        for i in range(2):
            result=subprocess.run(command,env=self.env,cwd=self.home,text=True,capture_output=True,timeout=22)
            self.assertEqual(result.returncode,0,(result.stdout,result.stderr))
            with urlopen(f'http://127.0.0.1:{self.port}/api/health',timeout=4) as f:
                health=json.load(f)
            self.assertEqual(health['service'],'tiny-engineer-dashboard')
            self.assertEqual(health['version'],'2.1')
            self.assertEqual(health['root'],str(self.install_dir))
            with urlopen(f'http://127.0.0.1:{self.port}/',timeout=4) as f:
                self.assertIn(b'Tiny Engineer',f.read(2000))
        opens=self.fake_opens.read_text().splitlines()
        self.assertEqual(opens,[f'http://127.0.0.1:{self.port}/']*2)
        log=(self.home/'.local/state/tiny-engineer-dashboard/launcher.log').read_text()
        self.assertEqual(log.count('Server ready'),1)
        self.assertIn('Reusing running V2.1',log)
        self.assertTrue((self.home/'.local/state/tiny-engineer-dashboard/server.log').is_file())
        self.assertTrue((self.home/'.local/share/tiny-engineer-dashboard/project.sqlite3').is_file())

    def test_busy_default_port_tries_next(self):
        import http.server
        import threading
        port=unused_port()
        blocker=http.server.HTTPServer(('127.0.0.1',port),http.server.BaseHTTPRequestHandler)
        t=threading.Thread(target=blocker.serve_forever,daemon=True)
        t.start()
        self.env['TINY_ENGINEER_PORT']=str(port)
        try:
            command=self.installer()
            result=subprocess.run(command,env=self.env,cwd=self.home,text=True,capture_output=True,timeout=22)
            self.assertEqual(result.returncode,0,(result.stdout,result.stderr))
            opened=self.fake_opens.read_text().strip()
            self.assertNotEqual(opened,f'http://127.0.0.1:{port}/')
            self.assertIn('Port', (self.home/'.local/state/tiny-engineer-dashboard/launcher.log').read_text())
            target=int(re.search(r':(\d+)/$',opened).group(1))
            with urlopen(f'http://127.0.0.1:{target}/api/health',timeout=4) as r:
                self.assertEqual(json.load(r)['version'],'2.1')
        finally:
            blocker.shutdown();blocker.server_close();t.join(timeout=3)

    def test_stable_copper_theme(self):
        css=(ROOT/'app/refined.css').read_text()
        icon=(ROOT/'app/icon.svg').read_text()
        js=(ROOT/'app/app.js').read_text()
        self.assertIn('--copper:#c56a4c',css)
        self.assertIn('background:var(--copper)',css)
        self.assertIn('stroke="#C56A4C"',icon)
        self.assertIn("'#BD832D'",js) # reference swatch preserved


if __name__=='__main__':unittest.main()
