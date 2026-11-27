#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare YouTube IFrame API error codes for several videos in this environment."""
from playwright.sync_api import sync_playwright

PAGE = """<!doctype html><meta charset="utf-8"><body style="margin:0">
<div id="p" style="width:480px;height:270px"></div>
<script src="https://www.youtube.com/iframe_api"></script>
<script>
window.LOG = [];
function onYouTubeIframeAPIReady(){
  window.player = new YT.Player('p', {videoId: VID, playerVars:{autoplay:1, playsinline:1, rel:0},
    events:{ onReady: function(e){ LOG.push('ready'); e.target.playVideo(); },
             onError: function(e){ LOG.push('error:'+e.data); },
             onStateChange: function(e){ LOG.push('state:'+e.data); } }});
}
</script>"""

TESTS = {'bellarich': 'k9K_hEMHeXk', 'control_zoo': 'jNQXAC9IVRw', 'control_google': 'M7lc1UVf-VE'}
STATE = "() => { try { return window.player ? window.player.getPlayerState() : 'no-player'; } catch(e) { return 'err'; } }"

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vid in TESTS.items():
        ctx = b.new_context(
            viewport={'width': 700, 'height': 500},
            user_agent='Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')
        pg = ctx.new_page()
        body = PAGE.replace('VID', vid)

        def handler(route, request, body=body):
            route.fulfill(body=body, content_type='text/html')

        pg.route('https://test.local/*', handler)
        pg.goto('https://test.local/page', wait_until='domcontentloaded', timeout=20000)
        pg.wait_for_timeout(12000)
        log = pg.evaluate("() => window.LOG")
        st = pg.evaluate(STATE)
        txt = ''
        for fr in pg.frames[1:]:
            if 'youtube' in fr.url:
                try:
                    txt = fr.evaluate("() => document.body ? document.body.innerText.replace(/\\s+/g,' ').slice(0,160) : ''")
                except Exception:
                    txt = 'read failed'
        pg.screenshot(path=f'/workspace/bellarich-site/shots/embed-{name}.png')
        print(name, vid, '| log:', log, '| state:', st, '| frameText:', repr(txt))
        ctx.close()
    b.close()
