"""Optional browser/UI → REAL local HTTP API → SQLite end-to-end regression.
Run: python3 tests/e2e_chromium.py (requires playwright and Chrome/Chromium).
The page is mounted in about:blank because headless browser sandbox navigation to
127.0.0.1 is restricted in some test environments; requests are faithfully
forwarded via Python to the actual 127.0.0.1 HTTP server.
"""
import json
import shutil
import tempfile
import threading
from pathlib import Path
from urllib import error,request
from playwright.sync_api import sync_playwright
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.server import Store,Server


def run():
    with tempfile.TemporaryDirectory() as d:
        store=Store(Path(d)/'state')
        srv=Server(('127.0.0.1',0),store)
        base=f'http://127.0.0.1:{srv.server_port}'
        thr=threading.Thread(target=srv.serve_forever,daemon=True);thr.start()
        try:
            def bridge(path,body):
                req=request.Request(base+path,data=(body.encode() if body is not None else None),
                    headers=({'Content-Type':'application/json'} if body is not None else {}),
                    method='POST' if body is not None else 'GET')
                try:
                    with request.urlopen(req,timeout=15) as res:
                        return {'status':res.status,'body':res.read().decode('utf-8')}
                except error.HTTPError as ex:
                    return {'status':ex.code,'body':ex.read().decode('utf-8')}
            chromium=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
            with sync_playwright() as pw:
                kwargs={'headless':True,'args':['--no-sandbox']}
                if chromium: kwargs['executable_path']=chromium
                b=pw.chromium.launch(**kwargs)
                browser_errors=[]
                ctx=b.new_context(viewport={'width':1440,'height':1050})
                page=ctx.new_page()
                page.on('pageerror',lambda ex:browser_errors.append(str(ex)))
                page.goto('about:blank')
                html=(ROOT/'app/index.html').read_text().replace('<script src="/app.js" defer></script>','').replace('<script src="/concepts.js" defer></script>','').replace('<link rel="stylesheet" href="/style.css"/>','').replace('<link rel="stylesheet" href="/refined.css"/>','')
                page.set_content(html)
                page.add_style_tag(content=(ROOT/'app/style.css').read_text())
                page.add_style_tag(content=(ROOT/'app/refined.css').read_text())
                page.expose_function('__realApi',bridge)
                page.evaluate('''() => {window.fetch = async(path,opt={})=>{
                    const result=await window.__realApi(path,opt.body??null);
                    return new Response(result.body,{status:result.status,
                        headers:{'Content-Type':'application/json'}});
                }}''')
                page.add_script_tag(content=(ROOT/'app/concepts.js').read_text())
                page.add_script_tag(content=(ROOT/'app/app.js').read_text())
                page.locator('h1').wait_for()
                assert page.locator('h1').inner_text().startswith('Build the robot in the official design.')
                page.screenshot(path=str(ROOT/'dashboard_preview.png'),full_page=True)
                photo_loaded=page.locator('.target-photo img').evaluate('(img)=>img.naturalWidth>0')
                print('Official reference photo loaded in isolated browser:',photo_loaded)
                # Fully render every desktop view with its actual backend state.
                for tab in ('today','next','guide','engineering','roadmap','library','costs','risks','settings','overview'):
                    page.locator(f'button[data-tab="{tab}"]').first.click()
                    assert page.locator('h1').count()==1, tab
                # T002 cannot close before T001: actual validation from real server.
                page.locator('button[data-tab="guide"]').first.click()
                page.screenshot(path=str(ROOT/'tests/guide_v2.png'),full_page=False)
                assert page.locator('#guide-stage').count()==1
                assert page.locator('#guide-jump').count()==1
                # View a far mechanical step, but do not bypass the prerequisites to complete it.
                page.locator('#guide-stage').select_option('M05')
                assert 'M05' in page.locator('#guide-stage').input_value()
                page.locator('#guide-jump').select_option('T033')
                assert 'T033' in page.locator('#guide-jump').input_value()
                page.locator('#guide-stage').select_option('M01')
                page.locator('#guide-jump').select_option('T001')
                page.locator('button[data-step="T002"]').click()
                page.locator('#task-status').select_option('Done')
                for gate in ('gate-prepared','gate-performed','gate-verified'):page.locator('#'+gate).check()
                page.locator('#evidence').fill('Unable to prove prerequisite: expected failure')
                page.locator('button[data-action="save-step"]').click()
                page.wait_for_timeout(200)
                assert 'Prerequisite T001' in page.locator('#toast').inner_text()
                assert store.state()['steps'][1]['status']=='Not Started'
                # Mark real first and second tasks complete.
                page.locator('button[data-step="T001"]').click()
                page.locator('#task-status').select_option('Done')
                for gate in ('gate-prepared','gate-performed','gate-verified'):page.locator('#'+gate).check()
                page.locator('#evidence').fill('Test-only evidence from UI/API integration, not a real assembled robot')
                page.locator('button[data-action="save-step"]').click()
                page.wait_for_timeout(300)
                assert store.state()['steps'][0]['status']=='Done'
                page.locator('button[data-step="T002"]').click()
                page.locator('#task-status').select_option('Done')
                for gate in ('gate-prepared','gate-performed','gate-verified'):page.locator('#'+gate).check()
                page.locator('#evidence').fill('Test-only evidence from UI/API integration, not a real assembled robot')
                page.locator('button[data-action="save-step"]').click()
                page.wait_for_timeout(300)
                assert store.state()['steps'][1]['status']=='Done'
                assert len([r for r in store.state()['records'] if r['kind']=='library'])==2
                # Reopen upstream: downstream should be invalidated.
                page.locator('button[data-step="T001"]').click()
                page.locator('#task-status').select_option('In Progress')
                page.locator('#gate-verified').uncheck()
                page.locator('button[data-action="save-step"]').click()
                page.wait_for_timeout(300)
                assert store.state()['steps'][1]['status']=='Needs Recheck'
                # Journal evidence saved to sqlite.
                page.locator('summary').filter(has_text='Task journal').click()
                page.locator('#note-entry').fill('Temporary browser end-to-end note; not physical evidence')
                page.locator('button[data-action="add-note"]').click()
                page.wait_for_timeout(300)
                assert any('Temporary browser' in n['body'] for n in store.state()['notes'])
                # Expense form round trip.
                page.locator('button[data-tab="costs"]').first.click()
                page.locator('#expense-desc').fill('E2E test expense')
                page.locator('#expense-amount').fill('12.34')
                page.locator('button[data-action="expense-save"]').click()
                page.wait_for_timeout(300)
                assert any(x['amount']==12.34 for x in store.state()['expenses'])
                # Version save round trip.
                page.locator('button[data-tab="settings"]').first.click()
                page.locator('#version-label').fill('E2E browser snapshot')
                page.locator('button[data-action="version-save"]').click()
                page.wait_for_timeout(300)
                assert any('E2E browser' in v['label'] for v in store.state()['versions'])
                # Mobile: overlay menu and main content layout.
                page.set_viewport_size({'width':390,'height':844})
                page.screenshot(path=str(ROOT/'tests/mobile_v2.png'),full_page=False)
                page.locator('#menu').click()
                assert 'open' in page.locator('#shell').get_attribute('class')
                page.locator('button[data-tab="engineering"]').first.click()
                assert 'open' not in page.locator('#shell').get_attribute('class')
                assert 'Learn the' in page.locator('h1').inner_text()
                assert page.locator('details.lesson-card').count()==14
                assert not page.locator('details.lesson-card').first.evaluate('(el)=>el.open')
                page.locator('details.lesson-card').first.locator('summary').click()
                assert page.locator('details.lesson-card').first.evaluate('(el)=>el.open')
                page.locator('#calc-v').fill('5')
                page.locator('#calc-i').fill('2.5')
                page.locator('button[data-action="calc-power"]').click()
                assert '12.50 W' in page.locator('#power-result').inner_text()
                # Each phone-width view must remain responsive, with no body overflow.
                for mobile_tab in ('overview','today','next','guide','engineering','roadmap','library','costs','risks','settings'):
                    page.locator('#menu').click()
                    page.locator(f'button[data-tab="{mobile_tab}"]').first.click()
                    overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
                    assert overflow<=3, f'Mobile horizontal overflow {overflow}px in {mobile_tab}'
                page.locator('#menu').click()
                page.locator('button[data-tab="engineering"]').first.click()
                assert not browser_errors,browser_errors
                print('E2E PASS: all 10 screens; HTTP+SQLite quality gates; recheck; notes; expenses; versions; all 10 mobile layouts; power calculation; no script errors.')
                b.close()
        finally:
            srv.shutdown();srv.server_close();thr.join(timeout=4);store.conn.close()

if __name__=='__main__':run()
