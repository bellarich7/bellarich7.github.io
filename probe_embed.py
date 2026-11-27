#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare YouTube IFrame API error codes for several videos, run inside the live site origin."""
import json, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich7.github.io/?v=embedtest'
TESTS = {'bellarich': 'k9K_hEMHeXk', 'control_zoo': 'jNQXAC9IVRw', 'control_google': 'M7lc1UVf-VE'}

INJECT = """(videoIds) => new Promise(resolve => {
  const box = document.createElement('div');
  box.style.cssText = 'position:fixed;left:0;top:0;width:480px;height:270px;z-index:99999;background:#000';
  document.body.appendChild(box);
  const out = [];
  let idx = 0;
  function next(){
    if(idx >= videoIds.length) { resolve(out); return; }
    const id = videoIds[idx++];
    const host = document.createElement('div');
    const hid = 'probe' + idx;
    host.id = hid;
    box.innerHTML = '';
    box.appendChild(host);
    const rec = {videoId: id, log: []};
    out.push(rec);
    let done = false;
    const player = new YT.Player(hid, {
      videoId: id,
      playerVars: {autoplay: 1, playsinline: 1, rel: 0},
      events: {
        onReady: function(e){ rec.log.push('ready'); try { e.target.playVideo(); } catch(err){ rec.log.push('playVideo-threw'); } },
        onError: function(e){ rec.log.push('error:' + e.data); },
        onStateChange: function(e){ rec.log.push('state:' + e.data); }
      }
    });
    setTimeout(function(){
      try { rec.state = player.getPlayerState(); } catch(e) { rec.state = 'n/a'; }
      try {
        const ifr = document.querySelector('#' + hid + ' iframe') || document.querySelector('#probe' + idx + ' iframe');
        rec.iframeSrc = ifr ? ifr.src : null;
      } catch(e) {}
      next();
    }, 9000);
  }
  next();
})"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1000, 'height': 700},
                        user_agent='Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 '
                                   '(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')
    pg = ctx.new_page()
    reqfail = []
    pg.on('requestfailed', lambda r: reqfail.append(r.url + ' :: ' + str(r.failure)))
    pg.goto(URL, wait_until='networkidle', timeout=45000)
    pg.evaluate("() => { if(!window.YT || !window.YT.Player){ const s=document.createElement('script'); s.src='https://www.youtube.com/iframe_api'; document.head.appendChild(s);} }")
    pg.wait_for_function("() => window.YT && window.YT.Player", timeout=25000)
    res = pg.evaluate(INJECT, list(TESTS.values()))
    print(json.dumps({'results': res, 'failed_requests': reqfail[:10]}, ensure_ascii=False, indent=1))
    b.close()
