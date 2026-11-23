"""Local-only Tiny Engineer project dashboard. Python stdlib + optional reportlab for PDF."""
import argparse
import csv
import datetime as dt
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape as xml_escape

from .guide_data import STEPS, PHASES, BOM, SOURCE_INDEX
APP_DIR = Path(__file__).resolve().parent
VALID_STATUSES={'Not Started','In Progress','Blocked','Needs Recheck','Done'}
MAX_BODY=8*1024*1024
DEFAULT_START='2026-11-23'

class UserError(Exception): pass

def utcnow(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def jsonstr(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'))
def nint(v, default=0,lo=0,hi=1_000_000):
    try: return max(lo,min(hi,int(v)))
    except (ValueError,TypeError): return default

def as_float(x,default=0,lo=0,hi=1000000):
    try: return max(lo,min(hi,float(x)))
    except (ValueError,TypeError): return default

def validate_str(x, limit=12000):
    if not isinstance(x,str): raise UserError('Expected text.')
    if len(x)>limit: raise UserError(f'Text too long (max {limit}).')
    return x

class Store:
    def __init__(self,base):
        self.base=Path(base).expanduser().resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.path=self.base/'project.sqlite3'
        self.lock=threading.RLock()
        self.conn=sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory=sqlite3.Row
        self.conn.execute('PRAGMA busy_timeout=5000')
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.create_schema()
    def create_schema(self):
        with self.lock, self.conn:
            self.conn.executescript('''
              CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS steps(id TEXT PRIMARY KEY,status TEXT NOT NULL DEFAULT 'Not Started',
                gates TEXT NOT NULL DEFAULT '{}',notes TEXT NOT NULL DEFAULT '',actual_minutes INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT NOT NULL DEFAULT '',updated_at TEXT NOT NULL DEFAULT '',planned_date TEXT NOT NULL DEFAULT '');
              CREATE TABLE IF NOT EXISTS inventory(id TEXT PRIMARY KEY,name TEXT NOT NULL,category TEXT NOT NULL,
                quantity INTEGER NOT NULL,unit_price REAL NOT NULL,kind TEXT NOT NULL, purchased INTEGER NOT NULL DEFAULT 0,
                actual_price REAL NOT NULL DEFAULT 0,url TEXT NOT NULL DEFAULT '',note TEXT NOT NULL DEFAULT '');
              CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT NOT NULL,title TEXT NOT NULL,
                body TEXT NOT NULL,phase TEXT NOT NULL DEFAULT '',status TEXT NOT NULL DEFAULT 'Open',created_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,description TEXT NOT NULL,
                amount REAL NOT NULL,category TEXT NOT NULL,spent_on TEXT NOT NULL,notes TEXT NOT NULL DEFAULT '');
              CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT,step_id TEXT NOT NULL,
                body TEXT NOT NULL,created_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY AUTOINCREMENT,label TEXT NOT NULL,
                created_at TEXT NOT NULL,snapshot TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,
                action TEXT NOT NULL,detail TEXT NOT NULL);
            ''')
            default_settings={
               'name':'Tiny Engineer · Desk Robot Studio','goal':'Replicate the original jamro Tiny Engineer seated desk-robot assembly using SG90 prints, a chair and miniature desk (laptop, mug, bell and lamp), integrated PCB, five servos, OLED face and speaker; then verify motion and agent-triggered interactions.',
               'budget':300,'servo':'SG90','architecture':'Integrated main control PCB',
               'start_date':DEFAULT_START,'estimated_weekly_hours':8,'github_remote':'',
               'notes':'Reference materials: jamro/tiny-engineer. The project is a desktop animatronic robot, not a walking robot.',
               'version':'V2','warning_storage_mb':40}
            self.conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('settings',?)",(jsonstr(default_settings),))
            for s in STEPS:
                self.conn.execute('INSERT OR IGNORE INTO steps(id,updated_at) VALUES (?,?)',(s['id'],utcnow()))
            for i,b in enumerate(BOM,1):
                self.conn.execute('''INSERT OR IGNORE INTO inventory(id,name,category,quantity,unit_price,kind,url)
                  VALUES(?,?,?,?,?,?,?)''',(f'B{i:02d}',b['name'],b['category'],b['qty'],b['unit'],b['kind'],b['url']))
    def fetchall(self,sql,args=()): return [dict(r) for r in self.conn.execute(sql,args).fetchall()]
    def log(self,action,detail=''):
        self.conn.execute('INSERT INTO events(created_at,action,detail) VALUES(?,?,?)',(utcnow(),action,str(detail)[:1500]))
    def settings(self): return json.loads(self.conn.execute("SELECT value FROM meta WHERE key='settings'").fetchone()[0])
    def disk_stats(self):
        self.conn.execute('PRAGMA wal_checkpoint(PASSIVE)')
        files=[self.path,Path(str(self.path)+'-wal'),Path(str(self.path)+'-shm')]
        size=sum(f.stat().st_size for f in files if f.exists())
        usage=shutil.disk_usage(self.base)
        return {'db_bytes':size,'db_mb':round(size/1024**2,3),'free_gb':round(usage.free/1024**3,2),
                'disk_bytes':usage.total,'warning':size>self.settings().get('warning_storage_mb',40)*1024**2,
                'path':str(self.path),'backup_dir':str(self.base/'backups')}
    def state(self,include_events=True):
        with self.lock:
            rows={s['id']:s for s in self.fetchall('SELECT * FROM steps ORDER BY id')}
            for s in STEPS:
                r=rows[s['id']]
                r['gates']=json.loads(r['gates'])
                r.update({k:v for k,v in s.items() if k not in r})
                r['invalid_dependency']=any(rows.get(d,{}).get('status')!='Done' for d in s['depends']) and r['status']=='Done'
            return dict(settings=self.settings(),steps=[rows[s['id']] for s in STEPS],
              phases=[dict(id=p[0],title=p[1],description=p[2]) for p in PHASES],
              inventory=self.fetchall('SELECT * FROM inventory ORDER BY id'),
              expenses=self.fetchall('SELECT * FROM expenses ORDER BY spent_on DESC,id DESC'),
              records=self.fetchall('SELECT * FROM records ORDER BY id DESC'),
              notes=self.fetchall('SELECT * FROM notes ORDER BY id DESC LIMIT 800'),
              versions=[{'id':v['id'],'label':v['label'],'created_at':v['created_at']} for v in self.fetchall('SELECT id,label,created_at FROM versions ORDER BY id DESC')],
              events=self.fetchall('SELECT * FROM events ORDER BY id DESC LIMIT 120') if include_events else [],
              sources=[dict(title=t,url=u) for t,u in SOURCE_INDEX],build_target={'name':'Tiny Engineer — stock seated desk robot','servo':'SG90','print_folder':'3d_models/parts/sg90/3mf','architecture':'Integrated main control PCB','shape':'Seated humanoid and miniature desk','photo':'https://raw.githubusercontent.com/jamro/tiny-engineer/8821a07969788f52c232cab2c377d797524d4334/docs/tiny-engineer-preview.jpg','cad':'https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md','assembly':'https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md','viewer':'https://tinyengineer.dev/assembly/'},storage=self.disk_stats())
    def update_step(self,p):
        sid=validate_str(p.get('id',''),10); step=next((s for s in STEPS if s['id']==sid),None)
        if not step: raise UserError('Unknown step id.')
        st=validate_str(p.get('status','Not Started'),30)
        if st not in VALID_STATUSES: raise UserError('Invalid step status.')
        gates=p.get('gates',{})
        if not isinstance(gates,dict): raise UserError('Gate values must be an object.')
        gates={k:bool(gates.get(k,False)) for k in ('prepared','performed','verified')}
        notes=validate_str(p.get('notes',''),16000)
        minutes=nint(p.get('actual_minutes',0),hi=100000)
        planned=validate_str(p.get('planned_date',''),20)
        if planned:
            try: dt.date.fromisoformat(planned)
            except ValueError: raise UserError('Planned date must be YYYY-MM-DD.')
        with self.lock,self.conn:
            previous_row=self.conn.execute('SELECT status,completed_at FROM steps WHERE id=?',(sid,)).fetchone()
            current=previous_row['status']
            if st=='Done':
                if not all(gates.values()): raise UserError('Complete all three quality gates before marking Done.')
                if not notes.strip(): raise UserError('Add a short observation or evidence note before marking Done.')
                for dep in step['depends']:
                    row=self.conn.execute('SELECT status FROM steps WHERE id=?',(dep,)).fetchone()
                    if not row or row['status']!='Done':
                        raise UserError(f'Prerequisite {dep} must be Done before completing {sid}.')
            completed=(previous_row['completed_at'] or utcnow()) if (st=='Done' and current=='Done') else (utcnow() if st=='Done' else '')
            self.conn.execute('UPDATE steps SET status=?,gates=?,notes=?,actual_minutes=?,completed_at=?,updated_at=?,planned_date=? WHERE id=?',
                   (st,jsonstr(gates),notes,minutes,completed,utcnow(),planned,sid))
            if current=='Done' and st!='Done':
                i=next(i for i,v in enumerate(STEPS) if v['id']==sid)
                for later in STEPS[i+1:]:
                    old=self.conn.execute('SELECT status,gates FROM steps WHERE id=?',(later['id'],)).fetchone()
                    if old['status']=='Done':
                        g=json.loads(old['gates']);g['verified']=False
                        self.conn.execute("UPDATE steps SET status='Needs Recheck',gates=?,completed_at='',updated_at=? WHERE id=?",
                                          (jsonstr(g),utcnow(),later['id']))
                        self.conn.execute("UPDATE records SET status='Needs Recheck' WHERE kind='library' AND title LIKE ?",
                                          (f'Completion summary · {later["id"]} — %',))
                self.log('Cascade recheck',f'Changed {sid} from Done; downstream completed steps now need re-verification')
            if st=='Done' and current!='Done':
                synopsis=f"Verified task: {sid} — {step['title']}\nExit test: {step['exit_test']}\nBuilder evidence: {notes}\nActual time: {minutes} minutes\nSource: {step['source']}"
                summary_title=f"Completion summary · {sid} — {step['title']}"
                self.conn.execute('DELETE FROM records WHERE kind=? AND title=?',('library',summary_title))
                self.conn.execute('INSERT INTO records(kind,title,body,phase,status,created_at) VALUES(?,?,?,?,?,?)',
                    ('library',summary_title,synopsis,step['phase'],'Closed',utcnow()))
            self.log('Step status',f'{sid} {current} → {st}')
        return {'ok':True,'id':sid,'status':st}
    def save_settings(self,p):
        allowed={'name':(150,str),'goal':(4000,str),'budget':(None,'number'),'servo':(100,str),
          'architecture':(150,str),'start_date':(10,str),'estimated_weekly_hours':(None,'number'),
          'github_remote':(300,str),'notes':(4000,str),'version':(50,str),
          'warning_storage_mb':(None,'number')}
        s=self.settings()
        for k,v in p.items():
            if k not in allowed:continue
            limit,t=allowed[k]
            s[k]=validate_str(v,limit) if t==str else as_float(v)
        try: dt.date.fromisoformat(s['start_date'])
        except ValueError: raise UserError('Start date must be YYYY-MM-DD.')
        s['estimated_weekly_hours']=max(0.25,s['estimated_weekly_hours'])
        s['warning_storage_mb']=max(1,s['warning_storage_mb'])
        with self.lock,self.conn:
            self.conn.execute("UPDATE meta SET value=? WHERE key='settings'",(jsonstr(s),))
            self.log('Settings','Updated project settings')
        return {'ok':True}
    def update_inventory(self,p):
        ident=validate_str(p.get('id',''),20)
        if not re.fullmatch(r'B\d+',ident):raise UserError('Bad inventory id')
        with self.lock,self.conn:
            prev=self.conn.execute('SELECT * FROM inventory WHERE id=?',(ident,)).fetchone()
            if not prev:raise UserError('Inventory item not found')
            purchased=1 if p.get('purchased',False) else 0
            actual=as_float(p.get('actual_price',prev['actual_price']))
            note=validate_str(p.get('note',prev['note']),3000)
            self.conn.execute('UPDATE inventory SET purchased=?,actual_price=?,note=? WHERE id=?',(purchased,actual,note,ident))
            self.log('Inventory',f'{ident} purchased={purchased}')
        return {'ok':True}
    def add_record(self,p):
        kind=validate_str(p.get('kind',''),30)
        if kind not in ('library','risk','decision','milestone_note'): raise UserError('Invalid record type')
        title=validate_str(p.get('title',''),300).strip();body=validate_str(p.get('body',''),25000)
        phase=validate_str(p.get('phase',''),20);status=validate_str(p.get('status','Open'),40)
        if not title: raise UserError('Title cannot be blank')
        if phase and phase not in [x[0] for x in PHASES]: raise UserError('Invalid milestone id')
        with self.lock,self.conn:
            cur=self.conn.execute('INSERT INTO records(kind,title,body,phase,status,created_at) VALUES(?,?,?,?,?,?)',
                                  (kind,title,body,phase,status,utcnow()))
            self.log('New record',f'{kind}: {title}')
        return {'ok':True,'id':cur.lastrowid}
    def edit_record(self,p):
        rid=nint(p.get('id'));title=validate_str(p.get('title',''),300).strip()
        body=validate_str(p.get('body',''),25000)
        status=validate_str(p.get('status','Open'),40)
        if not title: raise UserError('Title cannot be blank')
        with self.lock,self.conn:
            cur=self.conn.execute('UPDATE records SET title=?,body=?,status=? WHERE id=?',(title,body,status,rid))
            if not cur.rowcount:raise UserError('Record not found')
            self.log('Edited record',str(rid))
        return {'ok':True}
    def remove_record(self,p):
        rid=nint(p.get('id'))
        with self.lock,self.conn:
            self.conn.execute('DELETE FROM records WHERE id=?',(rid,))
            self.log('Deleted record',str(rid))
        return {'ok':True}
    def add_expense(self,p):
        desc=validate_str(p.get('description',''),300).strip()
        if not desc:raise UserError('Expense description required')
        amt=as_float(p.get('amount',0),hi=1000000)
        cat=validate_str(p.get('category','Other'),100)
        date=validate_str(p.get('spent_on',dt.date.today().isoformat()),10)
        try: dt.date.fromisoformat(date)
        except ValueError:raise UserError('Invalid expense date')
        note=validate_str(p.get('notes',''),2000)
        with self.lock,self.conn:
            cur=self.conn.execute('INSERT INTO expenses(description,amount,category,spent_on,notes) VALUES (?,?,?,?,?)',
                (desc,amt,cat,date,note));self.log('Expense',f'{desc}: ${amt:.2f}')
        return {'ok':True,'id':cur.lastrowid}
    def remove_expense(self,p):
        eid=nint(p.get('id'))
        with self.lock,self.conn:
            self.conn.execute('DELETE FROM expenses WHERE id=?',(eid,));self.log('Expense deleted',str(eid))
        return {'ok':True}
    def add_note(self,p):
        sid=validate_str(p.get('step_id',''),10)
        if not any(s['id']==sid for s in STEPS):raise UserError('Invalid step')
        body=validate_str(p.get('body',''),10000).strip()
        if not body:raise UserError('Write a note first')
        with self.lock,self.conn:
            cur=self.conn.execute('INSERT INTO notes(step_id,body,created_at) VALUES(?,?,?)',(sid,body,utcnow()))
            self.log('Task chat',sid)
        return {'ok':True,'id':cur.lastrowid}
    def payload(self,include_versions=True):
        with self.lock:
            return {'format':'tiny-engineer-dashboard-backup','schema_version':1,
              'created_at':utcnow(),'settings':self.settings(),
              'steps':self.fetchall('SELECT * FROM steps ORDER BY id'),
              'inventory':self.fetchall('SELECT * FROM inventory ORDER BY id'),
              'records':self.fetchall('SELECT * FROM records ORDER BY id'),
              'expenses':self.fetchall('SELECT * FROM expenses ORDER BY id'),
              'notes':self.fetchall('SELECT * FROM notes ORDER BY id'),
              'versions':self.fetchall('SELECT id,label,created_at,snapshot FROM versions ORDER BY id') if include_versions else [],
              'sources':[{'title':t,'url':u} for t,u in SOURCE_INDEX]}
    def backup_file(self,label='manual'):
        dest=self.base/'backups';dest.mkdir(exist_ok=True)
        stamp=dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        filename=f'tiny-engineer-{label}-{stamp}.json'
        path=dest/filename
        path.write_text(json.dumps(self.payload(),ensure_ascii=False,indent=2),encoding='utf8')
        return path
    def import_payload(self,p):
        if not isinstance(p,dict) or p.get('format')!='tiny-engineer-dashboard-backup' or p.get('schema_version')!=1:
            raise UserError('Invalid or unsupported Tiny Engineer backup format')
        steps=p.get('steps',[])
        valid_ids={s['id'] for s in STEPS}
        if not isinstance(steps,list) or len(steps)!=len(STEPS) or any(not isinstance(s,dict) for s in steps) or {s.get('id') for s in steps}!=valid_ids:
            raise UserError('Backup step IDs do not match this version; import stopped to prevent data loss.')
        # Imported progress must obey exactly the same evidence and dependency
        # invariants as user-created progress. A restored backup cannot bypass
        # the sequential safety gates by setting later steps to Done directly.
        imported={row['id']:row for row in steps}
        for sequence_step in STEPS:
            row=imported[sequence_step['id']]
            if row.get('status') not in VALID_STATUSES:
                raise UserError('Imported status is invalid: '+sequence_step['id'])
            try:
                gates=json.loads(row.get('gates','{}')) if isinstance(row.get('gates','{}'),str) else row.get('gates',{})
            except (ValueError,TypeError):
                raise UserError('Invalid imported quality gates: '+sequence_step['id'])
            if not isinstance(gates,dict):raise UserError('Invalid imported gates object')
            if row.get('status')=='Done':
                if not all(gates.get(k) is True for k in ('prepared','performed','verified')) or not isinstance(row.get('notes'),str) or not row['notes'].strip():
                    raise UserError('Imported Done status is missing evidence: '+sequence_step['id'])
                if any(imported[dep].get('status')!='Done' for dep in sequence_step['depends']):
                    raise UserError('Imported Done task has unfinished prerequisites: '+sequence_step['id'])
        for key in ('inventory','expenses','records','notes'):
            if not isinstance(p.get(key),list):raise UserError(f'Backup missing {key} list')
        newset=p.get('settings')
        if not isinstance(newset,dict):raise UserError('Backup missing settings')
        required_settings={'name':str,'goal':str,'start_date':str,'servo':str,'architecture':str,'notes':str,'version':str,'github_remote':str}
        for key,typ in required_settings.items():
            if not isinstance(newset.get(key),typ):raise UserError('Invalid imported setting: '+key)
        try:
            dt.date.fromisoformat(newset['start_date'])
            for key in ('budget','estimated_weekly_hours','warning_storage_mb'):
                if not isinstance(newset.get(key),(int,float)) or not (0<=float(newset[key])<1e9):raise UserError('Invalid imported setting: '+key)
        except ValueError:raise UserError('Invalid imported start date')
        prior=self.backup_file('pre-import')
        with self.lock,self.conn:
            for row in steps:
                st=row.get('status','Not Started')
                if st not in VALID_STATUSES:raise UserError('Invalid imported status')
                self.conn.execute('UPDATE steps SET status=?,gates=?,notes=?,actual_minutes=?,completed_at=?,updated_at=?,planned_date=? WHERE id=?',
                    (st,row.get('gates','{}') if isinstance(row.get('gates','{}'),str) else jsonstr(row['gates']),
                     validate_str(row.get('notes',''),16000),nint(row.get('actual_minutes',0)),
                     validate_str(row.get('completed_at',''),80),utcnow(),
                     validate_str(row.get('planned_date',''),20),row['id']))
            self.conn.execute("UPDATE meta SET value=? WHERE key='settings'",(jsonstr(newset),))
            for table in ('inventory','expenses','records','notes'):
                self.conn.execute(f'DELETE FROM {table}')
                names={
                 'inventory':'id,name,category,quantity,unit_price,kind,purchased,actual_price,url,note',
                 'expenses':'id,description,amount,category,spent_on,notes',
                 'records':'id,kind,title,body,phase,status,created_at',
                 'notes':'id,step_id,body,created_at'}[table].split(',')
                for row in p[table]:
                    if not isinstance(row,dict):raise UserError('Invalid backup record')
                    vals=[row.get(k,'') for k in names]
                    self.conn.execute(f'INSERT INTO {table} ({",".join(names)}) VALUES({",".join("?" for _ in names)})',vals)
            versions=p.get('versions',[])
            # Preserve the existing snapshot history for in-app restores. For a full
            # imported backup, replace history with the exported snapshots.
            if versions and all(isinstance(v,dict) and isinstance(v.get('snapshot'),str) for v in versions):
                self.conn.execute('DELETE FROM versions')
                for v in versions:
                    self.conn.execute('INSERT INTO versions(id,label,created_at,snapshot) VALUES(?,?,?,?)',
                        (nint(v['id']),validate_str(v['label'],160),validate_str(v['created_at'],80),validate_str(v['snapshot'],MAX_BODY)))
            self.log('Import',f'Restored backup; previous state saved as {prior.name}')
        return {'ok':True,'previous_backup':str(prior)}
    def create_version(self,label):
        label=validate_str(label,160).strip()
        if not label:raise UserError('Version label required')
        snapshot=jsonstr(self.payload(include_versions=False))
        with self.lock,self.conn:
            self.conn.execute('INSERT INTO versions(label,created_at,snapshot) VALUES(?,?,?)',(label,utcnow(),snapshot))
            self.log('Version snapshot',label)
        return {'ok':True,'label':label}
    def restore_version(self,ident):
        with self.lock:
            row=self.conn.execute('SELECT snapshot FROM versions WHERE id=?',(nint(ident),)).fetchone()
            if not row:raise UserError('Version not found')
            snapshot=json.loads(row['snapshot'])
        return self.import_payload(snapshot)
    def optimize(self):
        # Explicit user action; retains all project records.
        with self.lock:
            self.conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            self.conn.execute('VACUUM')
            with self.conn:self.log('Optimize','Checkpoint and VACUUM completed')
        return {'ok':True,'message':'SQLite checkpoint and VACUUM completed. No project records deleted.'}
    def github_backup(self):
        remote=self.settings().get('github_remote','').strip()
        # No userinfo, arbitrary remote hosts, shell interpolation or dynamic command injection.
        if not re.fullmatch(r'(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?|git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?)',remote):
            raise UserError('Set a GitHub remote like https://github.com/YOURNAME/YOUR-PRIVATE-REPO.git in Settings (no tokens in URL).')
        if not shutil.which('git'):raise UserError('git command is not installed')
        path=self.base/'github-backup';path.mkdir(exist_ok=True)
        (path/'project-backup.json').write_text(json.dumps(self.payload(),indent=2,ensure_ascii=False),encoding='utf8')
        (path/'README.md').write_text('# Tiny Engineer Dashboard backup\nThis repository stores project metadata and notes. Do not include passwords or private keys.\n')
        def run(*args):
            ret=subprocess.run(['git',*args],cwd=path,capture_output=True,text=True,timeout=35,
                               env={**os.environ,'GIT_TERMINAL_PROMPT':'0'})
            if ret.returncode:raise UserError('Git backup failed: '+(ret.stderr or ret.stdout)[-900:])
            return ret.stdout
        with self.lock:
            if not (path/'.git').exists():run('init','-b','main')
            run('config','user.name','Tiny Engineer Dashboard')
            run('config','user.email','dashboard@localhost.invalid')
            remotes=run('remote').splitlines()
            if 'origin' in remotes:run('remote','set-url','origin',remote)
            else:run('remote','add','origin',remote)
            run('add','project-backup.json','README.md')
            if run('status','--porcelain').strip():run('commit','-m',f'Tiny Engineer backup {utcnow()}')
            run('push','-u','origin','main')
            with self.conn:self.log('GitHub backup','Push to configured origin/main succeeded')
        return {'ok':True,'message':'Backup committed and pushed to origin/main'}

def selected_steps(state,phase=''):
    return [s for s in state['steps'] if not phase or s['phase']==phase]

def build_markdown(state,phase=''):
    settings=state['settings']; steps=selected_steps(state,phase)
    out=[f"# {settings['name']} — Project Library & Build Guide",'','Generated from your persistent project state.',
          'Hardware outcomes are user-reported; this report is not a physical verification certificate.','',
          f"**Goal:** {settings['goal']}",f"**Budget:** ${settings['budget']:,.2f}",
          f"**Start:** {settings['start_date']}",f"**Servo:** {settings['servo']}",
          f"**Architecture:** {settings['architecture']}",'','## Build sequence','']
    for i,s in enumerate(steps,1):
        out += [f"### {s['id']} · {s['title']} ({s['status']})",'',f"**Time estimate:** {s['minutes']} min",'',
            f"**Why this matters:** {s['purpose']}",'','**Instructions:**']
        out += [f'{n}. {a}' for n,a in enumerate(s['actions'],1)]
        out += ['',f"**Exit test:** {s['exit_test']}",f"**If it fails:** {s['if_failed']}",
            f"**Engineering concept — {s['concept']}:** {s['formula']}",f"**Example:** {s['example']}",
            f"**Safety:** {s['safety']}" if s['safety'] else '',f"**My evidence:** {s['notes'] or 'Not recorded'}",
            f"**Source:** {s['source']}",'']
    out+=['## Expenses','']+[f"- {x['spent_on']} — {x['description']}: ${x['amount']:.2f} ({x['category']})" for x in state['expenses']]
    out+=['','## Library, decisions, and risks','']
    for r in state['records']:
        if phase and r['phase'] not in ('',phase):continue
        out += [f"### {r['kind'].title()}: {r['title']}",f"Status: {r['status']} | Milestone: {r['phase']}",r['body'],'']
    out+=['## Source bibliography','']+[f'- [{r["title"]}]({r["url"]})' for r in state['sources']]
    return '\n'.join(x for x in out if x is not None)

def build_html(state,phase=''):
    md=build_markdown(state,phase)
    # Rich, readable HTML without allowing user text to execute as markup.
    return '<!doctype html><html><head><meta charset="utf-8"><title>Tiny Engineer report</title><style>body{background:#22100e;color:#f2e9d6;font:16px/1.65 system-ui;max-width:890px;margin:30px auto;padding:24px}pre{white-space:pre-wrap;font:inherit}h1{color:#c56a4c}</style></head><body><h1>Tiny Engineer · Export</h1><pre>'+html.escape(md)+'</pre></body></html>'

def build_pdf(state,phase=''):
    try:
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:raise UserError('PDF exports need reportlab. Install it with: python3 -m pip install reportlab')
    font='Helvetica'
    ttf='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if Path(ttf).exists():
        if 'DejaVuSans' not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont('DejaVuSans',ttf))
        font='DejaVuSans'
    buf=io.BytesIO();doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=46,leftMargin=46,topMargin=48,bottomMargin=49,title='Tiny Engineer - Beginner Build Guide',author='Tiny Engineer Autumn Lab')
    stylesheet=getSampleStyleSheet()
    body=ParagraphStyle('body-x',parent=stylesheet['BodyText'],fontName=font,fontSize=9.2,leading=14,spaceAfter=6)
    small=ParagraphStyle('small-x',parent=body,fontSize=8.2,leading=12,textColor=colors.HexColor('#494437'))
    heading=ParagraphStyle('heading-x',parent=body,fontSize=15,leading=19,spaceBefore=16,spaceAfter=9,textColor=colors.HexColor('#7A3D1B'))
    title=ParagraphStyle('title-x',parent=body,fontSize=23,leading=29,spaceAfter=18,textColor=colors.HexColor('#421414'))
    phase_style=ParagraphStyle('phase-x',parent=heading,fontSize=17,leading=22,textColor=colors.HexColor('#421414'),spaceBefore=22,spaceAfter=12)
    story=[Paragraph('Tiny Engineer · Build Guide and Project Report',title),
        Paragraph(xml_escape(state['settings']['goal']),body),
        Paragraph('Physical build tests must be performed by the builder; dashboard checkmarks are user reports, not lab certification.',small)]
    def P(txt,style=body):return Paragraph(xml_escape(str(txt)).replace('\n','<br/>'),style)
    old_phase=None
    for step in selected_steps(state,phase):
        if step['phase']!=old_phase:
            matching=next((v for v in PHASES if v[0]==step['phase']),None)
            if matching: story.append(Paragraph(xml_escape(f'{matching[0]} · {matching[1]}'),phase_style))
            old_phase=step['phase']
        section=[P(f"{step['id']} · {step['title']} — {step['status']}",heading),
                 P('Purpose: '+step['purpose']),P('Estimated time: '+str(step['minutes'])+' minutes',small)]
        section += [P(f'{i}. {a}') for i,a in enumerate(step['actions'],1)]
        section += [P('Pass condition: '+step['exit_test']),P('If failed: '+step['if_failed']),
                   P('Engineering: '+step['concept']+' — '+step['formula']),P('Example: '+step['example'])]
        if step['safety']:section.append(P('Safety: '+step['safety']))
        section += [P('Evidence: '+(step['notes'] or 'Not yet recorded'),small),P('Official source: '+step['source'],small),Spacer(1,5)]
        story.append(KeepTogether(section[:4]))
        story.extend(section[4:])
    story.append(P('Source material: https://github.com/jamro/tiny-engineer',small))
    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#D4C6B0'))
        canvas.line(46,37,A4[0]-46,37)
        canvas.setFont('Helvetica',7.5)
        canvas.setFillColor(colors.HexColor('#494437'))
        canvas.drawString(46,26,'Tiny Engineer Autumn Lab | Beginner Build Guide')
        canvas.drawRightString(A4[0]-46,26,f'Page {document.page}')
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buf.getvalue()

def report_bytes(store,typ='json',phase=''):
    state=store.state(); data=store.payload()
    if phase and phase not in [p[0] for p in PHASES]:raise UserError('Invalid milestone')
    if typ=='json':return ('application/json',json.dumps(data,indent=2,ensure_ascii=False).encode('utf8'),'working-copy.json')
    if typ=='md':return ('text/markdown',build_markdown(state,phase).encode('utf8'),'guide.md')
    if typ=='html':return ('text/html',build_html(state,phase).encode('utf8'),'guide.html')
    if typ=='pdf':return ('application/pdf',build_pdf(state,phase),'guide.pdf')
    if typ=='csv':
        o=io.StringIO();w=csv.writer(o);w.writerow(['ID','Milestone','Title','Status','Estimate minutes','Actual minutes','Evidence'])
        for s in selected_steps(state,phase):w.writerow([s['id'],s['phase'],s['title'],s['status'],s['minutes'],s['actual_minutes'],s['notes']])
        return ('text/csv',o.getvalue().encode('utf-8-sig'),'task-status.csv')
    if typ=='all':
        buf=io.BytesIO()
        with ZipFile(buf,'w',ZIP_DEFLATED) as z:
            for fmt in ('json','md','html','pdf','csv'):
                mime,b,f=report_bytes(store,fmt,phase)
                z.writestr(f,b)
        return ('application/zip',buf.getvalue(),'all-formats.zip')
    raise UserError('Unsupported export type')

class Server(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=True
    def __init__(self,addr,store):
        self.store=store
        super().__init__(addr, Handler)

class Handler(BaseHTTPRequestHandler):
    server_version='TinyEngineerDashboard/1.0'
    def log_message(self,*args):pass
    def headers_out(self,code,ctype,n,length=None,filename=None):
        self.send_response(code);self.send_header('Content-Type',ctype)
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: https://raw.githubusercontent.com; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        if length is not None:self.send_header('Content-Length',str(length))
        self.end_headers()
    def send_data(self,b,ctype='application/json',code=200,filename=None):
        if isinstance(b,(dict,list)):b=json.dumps(b,ensure_ascii=False).encode('utf8')
        if isinstance(b,str):b=b.encode('utf8')
        self.headers_out(code,ctype,len(b),filename=filename)
        self.wfile.write(b)
    def err(self,e,code=400):self.send_data({'ok':False,'error':str(e)},code=code)
    def _parse(self):
        size=nint(self.headers.get('Content-Length','0'),hi=MAX_BODY+1)
        if size>MAX_BODY:raise UserError('Request body too large.')
        try:return json.loads(self.rfile.read(size))
        except (ValueError,UnicodeDecodeError):raise UserError('Request must be valid JSON.')
    def do_GET(self):
        url=urlparse(self.path);path=url.path;params=parse_qs(url.query)
        try:
            if path=='/api/state':return self.send_data(self.server.store.state())
            if path=='/api/storage':return self.send_data(self.server.store.disk_stats())
            if path=='/api/export':
                kind=params.get('type',['json'])[0];phase=params.get('phase',[''])[0]
                mime,data,name=report_bytes(self.server.store,kind,phase)
                if phase:name=phase+'-'+name
                return self.send_data(data,mime,filename=name)
            if path=='/api/health':return self.send_data({'ok':True,'service':'tiny-engineer-dashboard','version':'2.1','root':str(APP_DIR.parent),'port':self.server.server_port})
            target={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/concepts.js':'concepts.js','/style.css':'style.css','/refined.css':'refined.css','/icon.svg':'icon.svg'}.get(path)
            if target:
                content=(APP_DIR/target).read_bytes()
                ctype={'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8',
                       'css':'text/css; charset=utf-8','svg':'image/svg+xml'}.get(target.split('.')[-1],'application/octet-stream')
                return self.send_data(content,ctype)
            return self.err('Not found.',404)
        except (UserError,ValueError) as e:return self.err(e)
        except Exception as e:return self.err('Server error: '+str(e),500)
    def do_POST(self):
        url=urlparse(self.path)
        try:
            payload=self._parse()
            action={'/api/step':self.server.store.update_step,
             '/api/settings':self.server.store.save_settings,
             '/api/inventory':self.server.store.update_inventory,
             '/api/record':self.server.store.add_record,
             '/api/record/edit':self.server.store.edit_record,
             '/api/record/remove':self.server.store.remove_record,
             '/api/expense':self.server.store.add_expense,
             '/api/expense/remove':self.server.store.remove_expense,
             '/api/note':self.server.store.add_note,
             '/api/import':self.server.store.import_payload,
             '/api/version':lambda p:self.server.store.create_version(p.get('label','')),
             '/api/version/restore':lambda p:self.server.store.restore_version(p.get('id')),
             '/api/backup':lambda p:{'ok':True,'path':str(self.server.store.backup_file())},
             '/api/github-backup':lambda p:self.server.store.github_backup(),
             '/api/optimize':lambda p:self.server.store.optimize()}.get(url.path)
            if not action:return self.err('Unknown action.',404)
            return self.send_data(action(payload))
        except UserError as e:return self.err(e)
        except Exception as e:return self.err('Server error: '+str(e),500)

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--port',type=int,default=8782)
    arg.add_argument('--data-dir',default=os.getenv('TINY_ENGINEER_DATA_DIR',str(Path.home()/'.local/share/tiny-engineer-dashboard')))
    arg.add_argument('--no-browser',action='store_true')
    args=arg.parse_args();store=Store(args.data_dir)
    server=Server(('127.0.0.1',args.port),store)
    url=f'http://127.0.0.1:{server.server_port}/'
    print(f'Tiny Engineer Dashboard running at {url}',flush=True)
    print(f'SQLite database: {store.path}',flush=True)
    print('Press Ctrl+C to stop.',flush=True)
    if not args.no_browser:
        import webbrowser
        threading.Timer(.7,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nStopping dashboard.')
    finally:server.server_close();store.conn.close()

if __name__=='__main__':main()
