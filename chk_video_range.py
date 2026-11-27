#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP Range를 지원하는 로컬 서버로 소개 영상 카드를 검증한다(GitHub Pages와 같은 조건).

- 접속 전: preload="metadata"가 실제로 몇 바이트를 받는지
- 탭 한 번(touch tap): video 표시 + 재생(소리 켜짐) + duration 480.3
- 5초로 seek: Range 요청으로 실제 프레임이 그려지는지(스크린샷 + 픽셀 분산)
- 콘솔 에러 0 / 실패 요청 0 / 가로 넘침 0
Usage: python3 chk_video_range.py [url] [tag]
"""
import http.server, socketserver, threading, json, sys, os, re

ROOT = '/workspace/bellarich-site'
PORT = 8768
URL = sys.argv[1] if len(sys.argv) > 1 else f'http://127.0.0.1:{PORT}/index.html'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'local'
REMOTE = URL.startswith('http') and '127.0.0.1' not in URL

BYTES = {}

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def log_message(self, *a):
        pass
    def do_GET(self):
        path = self.translate_path(self.path)
        rng = self.headers.get('Range')
        if not (os.path.isfile(path) and rng):
            return super().do_GET()
        m = re.match(r'bytes=(\d*)-(\d*)', rng)
        size = os.path.getsize(path)
        start = int(m.group(1) or 0)
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        length = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(length))
        self.end_headers()
        sent = 0
        try:
            with open(path, 'rb') as f:
                f.seek(start)
                left = length
                while left > 0:
                    buf = f.read(min(64 * 1024, left))
                    if not buf:
                        break
                    self.wfile.write(buf)
                    left -= len(buf); sent += len(buf)
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            key = self.path.split('?')[0]
            BYTES[key] = BYTES.get(key, 0) + sent

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

srv = None
if not REMOTE:
    srv = Server(('127.0.0.1', PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

from playwright.sync_api import sync_playwright

STATE = """() => {
  const v = document.getElementById('videoPlayer');
  const c = document.getElementById('videoCard');
  const b = document.getElementById('videoPlay');
  const rb = b.getBoundingClientRect(), rv = v.getBoundingClientRect();
  return {cardClass: c.className,
          btn: {visible: rb.width > 0 && rb.height > 0, w: Math.round(rb.width), h: Math.round(rb.height),
                display: getComputedStyle(b).display, aria: b.getAttribute('aria-label'), tag: b.tagName},
          video: {display: getComputedStyle(v).display, w: Math.round(rv.width), h: Math.round(rv.height),
                  paused: v.paused, muted: v.muted, volume: v.volume, controls: v.controls,
                  playsinline: v.hasAttribute('playsinline'), preload: v.preload,
                  readyState: v.readyState, duration: v.duration, currentTime: Math.round(v.currentTime*100)/100,
                  videoWidth: v.videoWidth, videoHeight: v.videoHeight, error: v.error ? v.error.code : null,
                  poster: v.getAttribute('poster'), title: v.getAttribute('title'),
                  src: (v.querySelector('source') || {}).src,
                  seekable: v.seekable.length ? [v.seekable.start(0), v.seekable.end(0)] : []},
          stageTop: Math.round(document.querySelector('.video-card__stage').getBoundingClientRect().top),
          cap: document.querySelector('.video-card__cap').textContent.replace(/\\s+/g, ' ').trim(),
          yt: document.querySelector('.video-card__yt').getAttribute('href'),
          scrollW: document.documentElement.scrollWidth, vw: document.documentElement.clientWidth};
}"""

def lum_std(pg, box):
    """표시 영역의 픽셀 밝기 분산(검은 화면이면 0에 가까움)."""
    return pg.evaluate("""(b) => {
      return new Promise(res => {
        const v = document.getElementById('videoPlayer');
        const c = document.createElement('canvas');
        const w = 64, h = 36; c.width = w; c.height = h;
        const g = c.getContext('2d');
        try { g.drawImage(v, 0, 0, w, h); } catch(e) { return res({err: String(e).slice(0,60)}); }
        const d = g.getImageData(0, 0, w, h).data;
        let s = 0, s2 = 0, n = 0;
        for (let i = 0; i < d.length; i += 4) { const l = (d[i]*.299 + d[i+1]*.587 + d[i+2]*.114); s += l; s2 += l*l; n++; }
        const mean = s / n;
        res({mean: Math.round(mean*10)/10, std: Math.round(Math.sqrt(s2/n - mean*mean)*10)/10});
      });
    }""", box)

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for label, vp, dsf, mobile in (('1440', {'width': 1440, 'height': 900}, 1, False),
                                   ('390', {'width': 390, 'height': 844}, 2, True),
                                   ('360', {'width': 360, 'height': 740}, 2, True)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf, is_mobile=mobile, has_touch=mobile,
                            user_agent=('Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36') if mobile else None)
        pg = ctx.new_page()
        fails, errs, cons, reqs = [], [], [], []
        pg.on('request', lambda r: reqs.append((r.resource_type, r.url)))
        pg.on('requestfailed', lambda r: fails.append((r.url[:110], str(r.failure))))
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.on('console', lambda m: cons.append(m.text[:200]) if m.type == 'error' else None)
        BYTES.clear()
        pg.goto(URL, wait_until='load', timeout=60000)
        pg.wait_for_timeout(2500)
        d = {}
        d['bytes_before_click'] = dict(BYTES)
        d['media_requests_before_click'] = [u for t, u in reqs if 'intro.mp4' in u]
        d['state_before'] = pg.evaluate(STATE)
        pg.evaluate("document.getElementById('videoCard').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(600)
        pg.screenshot(path=f'{ROOT}/shots/{TAG}-{label}-a-card.png')
        BYTES.clear()
        if mobile:
            box = pg.locator('#videoPlay').bounding_box()
            pg.touchscreen.tap(box['x'] + box['width']/2, box['y'] + box['height']/2)
        else:
            pg.click('#videoPlay')
        pg.wait_for_timeout(3500)
        d['state_playing'] = pg.evaluate(STATE)
        d['bytes_for_playback'] = dict(BYTES)
        pg.screenshot(path=f'{ROOT}/shots/{TAG}-{label}-b-playing.png')
        d['frame_playing'] = lum_std(pg, None)
        # 5초로 이동해 프레임 확인
        pg.evaluate("() => { const v = document.getElementById('videoPlayer'); v.pause(); v.currentTime = 5; }")
        pg.wait_for_timeout(3000)
        d['state_at5s'] = pg.evaluate(STATE)
        pg.screenshot(path=f'{ROOT}/shots/{TAG}-{label}-c-5s.png')
        d['frame_5s'] = lum_std(pg, None)
        d['bytes_seek'] = dict(BYTES)
        d['failed'] = fails
        d['page_errors'] = errs
        d['console_errors'] = cons
        out[label] = d
        ctx.close()
    b.close()
if srv:
    srv.shutdown()
print(json.dumps(out, ensure_ascii=False, indent=1))
