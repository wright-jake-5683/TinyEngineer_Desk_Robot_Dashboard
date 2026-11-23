"""Chromium rendering+interaction smoke test with stubbed fetch (admin blocks loopback navigation)."""
import json
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'app'
state=json.load(urlopen('http://127.0.0.1:8782/api/state'))
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1440,'height':1050},device_scale_factor=1)
    page=ctx.new_page()
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('about:blank')
    html=(ROOT/'index.html').read_text().replace('<script src="/app.js" defer></script>','').replace('<script src="/concepts.js" defer></script>','').replace('<link rel="stylesheet" href="/style.css"/>','').replace('<link rel="stylesheet" href="/refined.css"/>','')
    page.set_content(html)
    page.add_style_tag(content=(ROOT/'style.css').read_text())
    page.add_style_tag(content=(ROOT/'refined.css').read_text())
    page.evaluate('''s=>{window.__testState=s;window.fetch=async(path,opt)=>{
     const p=opt?.body?JSON.parse(opt.body):{};
     if(path==='/api/step'){
       const entry=window.__testState.steps.find(x=>x.id===p.id);
       Object.assign(entry,p);
     }
     return new Response(JSON.stringify(path==='/api/state'?window.__testState:{ok:true}),
           {status:200,headers:{'Content-Type':'application/json'}})
    }}''',state)
    page.add_script_tag(content=(ROOT/'concepts.js').read_text())
    page.add_script_tag(content=(ROOT/'app.js').read_text())
    page.locator('h1').wait_for()
    print('home title:',page.locator('h1').inner_text())
    assert page.locator('h1').inner_text().startswith('Build the robot in the official design.')
    page.screenshot(path=str(ROOT.parent/'dashboard_preview.png'),full_page=True)
    for tab in ['today','next','guide','engineering','roadmap','library','costs','risks','settings']:
        page.locator(f'button[data-tab="{tab}"]').first.click()
        page.wait_for_timeout(150)
        assert page.locator('h1').count()==1,(tab,page.locator('#main').inner_text()[:200])
        print(tab, page.locator('h1').inner_text())
        page.screenshot(path=str(ROOT.parent/'tests'/f'{tab}.png'),full_page=False)
    page.locator('button[data-tab="engineering"]').first.click()
    page.locator('#calc-v').fill('5')
    page.locator('#calc-i').fill('2.5')
    page.locator('button[data-action="calc-power"]').click()
    assert '12.50 W' in page.locator('#power-result').inner_text()
    page.locator('button[data-tab="guide"]').first.click()
    assert 'One step at a time.' in page.locator('h1').inner_text()
    page.locator('#task-status').select_option('In Progress')
    page.locator('button[data-action="save-step"]').click()
    page.wait_for_timeout(250)
    assert page.locator('#task-status').input_value()=='In Progress'
    print('browser errors:',errors)
    assert not errors,errors
    b.close()
