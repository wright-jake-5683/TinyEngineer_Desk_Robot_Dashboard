"""Automated application tests; no physical servo/PCB claimed.
Run: python3 -m unittest discover -s tests -v
"""
from pathlib import Path
import json
import os
import sys
import tempfile
import threading
import unittest
from urllib import request,error
from zipfile import ZipFile
from io import BytesIO
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.guide_data import STEPS,PHASES,BOM
from app.server import Store,Server,report_bytes

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Store(Path(self.tmp.name)/'data')
        self.srv=Server(('127.0.0.1',0),self.db)
        self.thread=threading.Thread(target=self.srv.serve_forever,daemon=True)
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.srv.server_port}'
    def tearDown(self):
        self.srv.shutdown();self.srv.server_close()
        self.thread.join(timeout=3)
        self.db.conn.close()
        self.tmp.cleanup()
    def api(self,path,payload=None,method=None):
        data=json.dumps(payload).encode() if payload is not None else None
        headers={'Content-Type':'application/json'} if data else {}
        req=request.Request(self.url+path,data=data,headers=headers,method=method or ('POST' if data else 'GET'))
        try:
            with request.urlopen(req,timeout=8) as r:
                content=r.read()
                return r.status,content,r.headers
        except error.HTTPError as ex:return ex.code,ex.read(),ex.headers
    def state(self):
        code,body,_=self.api('/api/state');self.assertEqual(code,200)
        return json.loads(body)
    def done(self,sid):
        return self.api('/api/step',{'id':sid,'status':'Done',
          'gates':{'prepared':True,'performed':True,'verified':True},
          'notes':'Verified action and exit test in local laboratory test simulation only.',
          'actual_minutes':12})

    def test_seed_content_and_acyclic_deps(self):
        self.assertEqual(len(STEPS),46)
        self.assertEqual(len(PHASES),8)
        self.assertEqual(sum(x['qty']*x['unit'] for x in BOM),192.85)
        self.assertEqual({s['id'] for s in STEPS},{f'T{i:03d}' for i in range(1,47)})
        for i,s in enumerate(STEPS):
            self.assertEqual(s['depends'],[STEPS[i-1]['id']] if i else [])
            for f in ('title','purpose','actions','exit_test','if_failed','concept','source'):
                self.assertTrue(s[f],(s['id'],f))
            self.assertTrue(s['source'].startswith('https://github.com/jamro/tiny-engineer/'))
        s=self.state()
        self.assertEqual(len(s['steps']),46)
        self.assertTrue(all(t['status']=='Not Started' for t in s['steps']))
        self.assertEqual(len(s['inventory']),10)
        self.assertEqual(s['settings']['servo'],'SG90')
        self.assertIn('KEEP the ESP32 seated',STEPS[17]['actions'][-1])
        self.assertIn('after completing §3–§7',STEPS[30]['actions'][0])
        self.assertIn('From ABOVE the desk',STEPS[31]['actions'][1])
        self.assertIn('2.4 GHz home Wi-Fi',STEPS[40]['actions'][0])

    def test_prerequisites_and_quality_gates(self):
        status,body,_=self.done('T002')
        self.assertEqual(status,400)
        self.assertIn('Prerequisite',body.decode())
        status,body,_=self.api('/api/step',{'id':'T001','status':'Done','gates':{},'notes':'okay'})
        self.assertEqual(status,400);self.assertIn('quality gates',body.decode())
        status,body,_=self.api('/api/step',{'id':'T001','status':'Done',
          'gates':{'prepared':1,'performed':1,'verified':1},'notes':' '})
        self.assertEqual(status,400);self.assertIn('evidence',body.decode().lower())
        self.assertEqual(self.done('T001')[0],200)
        self.assertEqual(self.done('T002')[0],200)
        initial_completed=self.state()['steps'][0]['completed_at']
        self.assertEqual(self.api('/api/step',{'id':'T001','status':'Done','gates':{'prepared':True,'performed':True,'verified':True},'notes':'Additional evidence added later.'})[0],200)
        self.assertEqual(self.state()['steps'][0]['completed_at'],initial_completed)
        s=self.state();self.assertEqual(s['steps'][0]['status'],'Done')
        self.assertEqual(s['steps'][1]['status'],'Done')
        self.assertEqual(len([r for r in s['records'] if r['title'].startswith('Completion summary')]),2)
        status,_,_=self.api('/api/step',{'id':'T001','status':'In Progress','gates':{'prepared':1,'performed':1,'verified':0},'notes':'Retest needed'})
        self.assertEqual(status,200)
        s=self.state();self.assertEqual(s['steps'][1]['status'],'Needs Recheck')
        self.assertEqual(s['steps'][1]['gates']['verified'],False)
        self.assertEqual(next(r for r in s['records'] if 'T002' in r['title'])['status'],'Needs Recheck')

    def test_persistence_across_store_reopen(self):
        self.assertEqual(self.done('T001')[0],200)
        self.api('/api/settings',{'budget':215,'goal':'Build and document a stable desktop robot'})
        newstore=Store(Path(self.tmp.name)/'data')
        try:
            self.assertEqual(newstore.state()['steps'][0]['status'],'Done')
            self.assertEqual(newstore.settings()['budget'],215)
        finally:newstore.conn.close()

    def test_settings_and_inventory(self):
        st,body,_=self.api('/api/settings',{'start_date':'2026-13-56'})
        self.assertEqual(st,400)
        self.assertEqual(self.state()['settings']['start_date'],'2026-11-23')
        self.assertEqual(self.api('/api/settings',{'budget':250,'estimated_weekly_hours':5.5})[0],200)
        self.assertEqual(self.state()['settings']['budget'],250)
        self.assertEqual(self.api('/api/inventory',{'id':'B03','purchased':True,'actual_price':3.75,'note':'verified retailer'})[0],200)
        row=self.state()['inventory'][2]
        self.assertEqual(row['actual_price'],3.75);self.assertEqual(row['purchased'],1)

    def test_expenses_notes_and_records(self):
        st,body,_=self.api('/api/expense',{'description':'PCB', 'amount':127.55,'category':'Electronics','spent_on':'2026-11-22','notes':'invoice'})
        self.assertEqual(st,200);eid=json.loads(body)['id']
        self.assertEqual(self.state()['expenses'][0]['amount'],127.55)
        self.assertEqual(self.api('/api/note',{'step_id':'T001','body':'Tested power math independently'})[0],200)
        self.assertEqual(self.api('/api/record',{'kind':'risk','title':'Brownout','body':'Check rail current','phase':'M07'})[0],200)
        record=self.state()['records'][0]
        self.assertEqual(self.api('/api/record/edit',{'id':record['id'],'title':'Brownout risk','body':'Test at load','status':'Open'})[0],200)
        self.assertEqual(self.state()['records'][0]['title'],'Brownout risk')
        self.assertEqual(self.api('/api/record/remove',{'id':record['id']})[0],200)
        self.assertFalse(self.state()['records'])
        self.assertEqual(self.api('/api/expense/remove',{'id':eid})[0],200)
        self.assertEqual(self.state()['expenses'],[])

    def test_version_snapshot_and_restore(self):
        self.done('T001')
        st,b,_=self.api('/api/version',{'label':'V1 baseline'})
        self.assertEqual(st,200)
        self.assertEqual(len(self.state()['versions']),1)
        self.api('/api/settings',{'budget':150})
        st,b,_=self.api('/api/version/restore',{'id':self.state()['versions'][0]['id']})
        self.assertEqual(st,200, b.decode())
        self.assertEqual(self.state()['settings']['budget'],300)
        self.assertEqual(self.state()['steps'][0]['status'],'Done')
        self.assertEqual(len(self.state()['versions']),1)
        self.assertTrue(list((Path(self.tmp.name)/'data'/'backups').glob('*.json')))

    def test_backup_import_and_reject_invalid_data(self):
        self.done('T001')
        self.api('/api/version',{'label':'V1 test'})
        st,body,_=self.api('/api/export?type=json')
        backup=json.loads(body)
        self.assertEqual(backup['format'],'tiny-engineer-dashboard-backup')
        self.assertEqual(len(backup['versions']),1)
        self.assertIn('snapshot',backup['versions'][0])
        self.api('/api/step',{'id':'T001','status':'Blocked','gates':{},'notes':'Oops'})
        self.assertEqual(self.api('/api/import',backup)[0],200)
        self.assertEqual(self.state()['steps'][0]['status'],'Done')
        self.assertEqual(len(self.state()['versions']),1)
        bad=dict(backup);bad['steps']=backup['steps'][:-1]
        self.assertEqual(self.api('/api/import',bad)[0],400)
        self.assertEqual(self.state()['steps'][0]['status'],'Done')
        import copy
        tampered=copy.deepcopy(backup)
        tampered['steps'][2]['status']='Done'
        tampered['steps'][2]['gates']='{"prepared":true,"performed":true,"verified":true}'
        tampered['steps'][2]['notes']='Forged completion'
        st,body,_=self.api('/api/import',tampered)
        self.assertEqual(st,400)
        self.assertIn('prerequisites',body.decode())
        self.assertEqual(self.state()['steps'][2]['status'],'Not Started')

    def test_exports_and_pdf_content(self):
        for typ,ctype,signature in [
             ('json','application/json',b'"schema_version": 1'),
             ('md','text/markdown',b'Build Guide'),
             ('html','text/html',b'<!doctype html>'),
             ('pdf','application/pdf',b'%PDF'),
             ('csv','text/csv',b'ID,Milestone'),
             ('all','application/zip',b'PK')]:
            with self.subTest(export=typ):
                status,b,h=self.api('/api/export?type='+typ)
                self.assertEqual(status,200,(typ,b[:180]))
                self.assertTrue(h['Content-Type'].startswith(ctype),h['Content-Type'])
                self.assertIn(signature,b[:3000])
                self.assertGreater(len(b),50)
                if typ=='all':
                    with ZipFile(BytesIO(b)) as zipfile:
                        self.assertEqual(set(zipfile.namelist()),{'working-copy.json','guide.md','guide.html','guide.pdf','task-status.csv'})
        st,b,_=self.api('/api/export?type=pdf&phase=M01')
        self.assertEqual(st,200)
        st,b,_=self.api('/api/export?type=pdf&phase=INVALID')
        self.assertEqual(st,400)

    def test_storage_optimize_backup_and_github_guard(self):
        stats=self.state()['storage'];self.assertGreater(stats['db_bytes'],0)
        st,b,_=self.api('/api/optimize',{})
        self.assertEqual(st,200,b.decode())
        st,b,_=self.api('/api/backup',{})
        self.assertEqual(st,200)
        p=Path(json.loads(b)['path']);self.assertTrue(p.is_file())
        st,b,_=self.api('/api/github-backup',{})
        self.assertEqual(st,400)
        self.assertIn('GitHub remote',b.decode())

    def test_correct_robot_target_and_offline_docs(self):
        """Regression: never silently swap the creator's desk robot for an unrelated design."""
        import re
        appjs=(ROOT/'app/app.js').read_text(encoding='utf-8')
        css=(ROOT/'app/refined.css').read_text(encoding='utf-8')
        html=(ROOT/'app/index.html').read_text(encoding='utf-8')
        spec=(ROOT/'docs/TARGET_DESIGN_SPEC.md').read_text(encoding='utf-8')
        guide=(ROOT/'docs/BEGINNER_BUILD_GUIDE.md').read_text(encoding='utf-8')
        self.assertIn('jamro/tiny-engineer',appjs)
        self.assertIn('docs/tiny-engineer-preview.jpg',appjs)
        self.assertIn('target-photo',appjs)
        self.assertIn('photo-fallback',appjs)
        self.assertIn('3d_models',spec)
        self.assertIn('SG90',spec)
        self.assertIn('Not a walking',guide.replace('not a walking','Not a walking'))
        self.assertIn('T001 · Identify the robot',guide)
        self.assertIn('T046 · Finalize documentation',guide)
        self.assertIn('§12',guide)
        self.assertIn('§13',guide)
        self.assertEqual(len(re.findall(r'^### T\d{3} · ',guide,re.M)),46)
        self.assertIn('refined.css',html)
        self.assertIn('--copper:#c56a4c',css)
        self.assertIn('#BD832D',appjs)  # Reference swatch retained
        self.assertIn('#0e1114',css)
        self.assertTrue((ROOT/'docs/BEGINNER_BUILD_GUIDE.pdf').read_bytes().startswith(b'%PDF'))
        st,body,headers=self.api('/refined.css')
        self.assertEqual(st,200)
        self.assertIn('text/css',headers['Content-Type'])
        self.assertIn('raw.githubusercontent.com',self.api('/')[2].get('Content-Security-Policy',''))
        state=self.state()
        self.assertIn('jamro/tiny-engineer',str(state.get('build_target')))

    def test_serves_files_with_security_headers(self):
        for path in ('/','/app.js','/concepts.js','/style.css','/icon.svg'):
            st,b,h=self.api(path)
            self.assertEqual(st,200,(path,b[:60]))
            self.assertEqual(h['X-Content-Type-Options'],'nosniff')
            self.assertTrue(len(b)>10)
        self.assertEqual(self.api('/../../etc/passwd')[0],404)
        self.assertEqual(self.api('/api/fake')[0],404)
        health=json.loads(self.api('/api/health')[1])
        self.assertEqual(health['service'],'tiny-engineer-dashboard')
        self.assertEqual(health['version'],'2.1')

if __name__=='__main__':unittest.main()
