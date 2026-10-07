"""Splash screen shared by the dashboard and the landing page.

Flow
1. "Click to begin". The click is what lets the browser play sound.
2. The clip in assets/intro.mp3 plays as the loading bar starts counting 1% to 100%.
   The bar is a timed intro and it also waits for the page's load event, so it holds
   at 92% if the page is still loading.
3. At 100% the screen becomes a scroll-down screen. Scrolling down, swiping up,
   pressing Down, Page Down, Space or Enter, or clicking, slides the whole screen up.

Notes
- Shows once per browser tab session. Add ?splash=1 to the address to force it.
- Browsers block sound until the visitor has clicked, pressed a key or tapped. A
  wheel scroll alone does not count. Step 1 exists for that reason. If you call
  render_splash(gate=False) the first step is skipped, and the clip then starts on
  the visitor's first click, key press or tap (within 8 s).
- With "reduce motion" on, the bar is shorter and the screen fades instead of sliding.
"""
import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

AUDIO_PATH = Path(__file__).resolve().parent / "assets" / "intro.mp3"

JS_SPLASH = r'''
function erPlay(win, a){
  if(!a){ return; }
  var p = null;
  try{ a.muted = false; a.currentTime = 0; p = a.play(); }catch(e){ p = null; }
  if(p && p.catch){
    p.catch(function(err){
      try{ win.console.warn('EmergeRoute intro: playback blocked, waiting for the next click or key press.', err && err.name); }catch(e){}
      var d = win.document, fired = false, names = ['pointerdown', 'keydown', 'touchend'];
      function cleanup(){ names.forEach(function(n){ d.removeEventListener(n, go, true); }); }
      function go(){ if(fired){ return; } fired = true; cleanup(); try{ a.currentTime = 0; a.play(); }catch(e){} }
      names.forEach(function(n){ d.addEventListener(n, go, true); });
      win.setTimeout(cleanup, 8000);
    });
  }
}

function erSplash(doc, win, opts){
  try{
    var KEY = 'er-splash-seen';
    var force = /[?&]splash=1/.test(win.location.search || '');
    var seen = false;
    try{ seen = win.sessionStorage.getItem(KEY) === '1'; }catch(e){}
    if(doc.getElementById('er-splash')){ return; }
    if(seen && !force){ return; }
    try{ win.sessionStorage.setItem(KEY, '1'); }catch(e){}
    var reduce = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var gate = !(opts && opts.gate === false);
    var DURATION = reduce ? 1200 : 3200;
    var au = null;
    if(opts && opts.audio){
      try{ au = new win.Audio(opts.audio); au.preload = 'auto'; au.volume = 1; }catch(e){ au = null; }
      if(au){
        try{ au.addEventListener('error', function(){ win.console.warn('EmergeRoute intro: the audio file could not be decoded.'); }); }catch(e){}
      }
    }
    if(!au){ try{ win.console.warn('EmergeRoute intro: no audio file was loaded (check assets/intro.mp3).'); }catch(e){} }

    var old = doc.getElementById('er-splash-style'); if(old){ old.remove(); }
    var css = [
      '#er-splash{position:fixed;left:0;top:0;width:100%;height:100%;z-index:2147483000;background:#0c0b09;color:#ece7dc;font-family:"Red Hat Display",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;transition:transform 1.2s cubic-bezier(.7,0,.2,1)}',
      '#er-splash.open{transform:translateY(-100%)}',
      '#er-splash.fade{opacity:0;transition:opacity .3s}',
      '#er-splash .core{position:absolute;left:0;top:0;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center}',
      '#er-splash .mark{font-size:clamp(1.3rem,3vw,1.9rem);font-weight:300;letter-spacing:.32em;padding-left:.32em;margin-bottom:1.6rem}',
      '#er-splash .stage{position:relative;width:min(360px,72vw);height:3.6rem}',
      '#er-splash .barwrap{position:absolute;left:0;top:0;width:100%;opacity:0;visibility:hidden;transition:opacity .4s}',
      '#er-splash.go .barwrap{opacity:1;visibility:visible}',
      '#er-splash .track{height:2px;background:#2a261d}',
      '#er-splash .fill{height:100%;width:1%;background:#d6a24a}',
      '#er-splash .row{display:flex;justify-content:space-between;margin-top:.7rem;font:12px/1 "IBM Plex Mono",ui-monospace,Consolas,monospace;color:#9a9283}',
      '#er-splash .pct{color:#ece7dc}',
      '#er-splash button{font-family:inherit;cursor:pointer}',
      '#er-splash .begin{position:absolute;left:50%;top:0;transform:translateX(-50%);white-space:nowrap;background:none;border:1px solid #2a261d;color:#ece7dc;padding:.75rem 2rem;border-radius:2px;font-size:1rem;letter-spacing:.12em}',
      '#er-splash .begin:hover{border-color:#d6a24a}',
      '#er-splash.go .begin{display:none}',
      '#er-splash .cue{position:absolute;left:50%;bottom:2.6rem;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:.9rem;background:none;border:0;color:#ece7dc;font-size:.95rem;letter-spacing:.14em;visibility:hidden;opacity:0;transition:opacity .5s}',
      '#er-splash.ready .cue{visibility:visible;opacity:1}',
      '#er-splash .cueline{position:relative;width:1px;height:46px;background:#2a261d;overflow:hidden}',
      '#er-splash .cueline::after{content:"";position:absolute;left:0;top:-40%;width:1px;height:40%;background:#d6a24a;animation:erc 1.8s ease-in-out infinite}',
      '@keyframes erc{from{top:-40%}to{top:100%}}',
      '@media (prefers-reduced-motion:reduce){#er-splash .cueline::after{animation:none;top:0;height:100%}}',
      '#er-splash .skip{position:absolute;right:1.6rem;bottom:1.6rem;background:none;border:0;color:#9a9283;text-decoration:underline;text-underline-offset:4px;font-size:.92rem}',
      '#er-splash .skip:hover{color:#ece7dc}',
      '#er-splash.ready .skip{display:none}',
      '#er-splash button:focus-visible{outline:2px solid #d6a24a;outline-offset:3px}'
    ].join('');
    var st = doc.createElement('style'); st.id = 'er-splash-style'; st.textContent = css; doc.head.appendChild(st);

    var root = doc.createElement('div');
    root.id = 'er-splash'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', 'EmergeRoute intro');
    root.innerHTML =
      '<div class="core">' +
        '<div class="mark">EmergeRoute</div>' +
        '<div class="stage">' +
          '<button class="begin" type="button">Click to begin</button>' +
          '<div class="barwrap">' +
            '<div class="track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="1"><div class="fill"></div></div>' +
            '<div class="row"><span class="msg">Preparing the dashboard</span><span class="pct">1%</span></div>' +
          '</div>' +
        '</div>' +
        '<button class="cue" type="button" aria-label="Scroll down to enter"><span>Scroll down</span><span class="cueline"></span></button>' +
        '<button class="skip" type="button">Skip intro</button>' +
      '</div>';
    doc.body.appendChild(root);

    var fill = root.querySelector('.fill'), pctEl = root.querySelector('.pct'), track = root.querySelector('.track');
    var msg = root.querySelector('.msg'), cue = root.querySelector('.cue'), skip = root.querySelector('.skip'), beginBtn = root.querySelector('.begin');
    var loaded = doc.readyState === 'complete';
    if(!loaded){ win.addEventListener('load', function(){ loaded = true; }); }
    var start = 0, pct = 0, raf = 0, started = false, ready = false, entered = false, done = false, y0 = null;

    function update(){
      fill.style.width = pct + '%'; pctEl.textContent = pct + '%'; track.setAttribute('aria-valuenow', pct);
    }
    function finish(){
      if(done){ return; } done = true;
      doc.removeEventListener('keydown', onKey);
      if(raf){ win.cancelAnimationFrame(raf); }
      if(root.parentNode){ root.parentNode.removeChild(root); }
    }
    function enter(){
      if(entered || !ready){ return; } entered = true;
      if(reduce){ root.classList.add('fade'); win.setTimeout(finish, 320); }
      else{ win.setTimeout(function(){ root.classList.add('open'); }, 60); win.setTimeout(finish, 1500); }
    }
    function step(now){
      var t = Math.min(1, (now - start) / DURATION);
      var eased = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t + 2, 2) / 2;
      var target = Math.max(1, Math.round(eased * 100));
      if(!loaded){ target = Math.min(target, 92); }
      if(target !== pct){ pct = target; update(); }
      if(pct >= 100){ ready = true; msg.textContent = 'Ready'; root.classList.add('ready'); return; }
      raf = win.requestAnimationFrame(step);
    }
    function begin(){
      if(started){ return; } started = true;
      erPlay(win, au);
      root.classList.add('go');
      pct = 1; update();
      start = win.performance.now();
      raf = win.requestAnimationFrame(step);
    }
    function onKey(e){
      if(e.key === 'Escape'){ finish(); return; }
      if(!started){ begin(); return; }
      if(ready && (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ' || e.key === 'Enter')){ e.preventDefault(); enter(); }
    }
    root.addEventListener('click', function(){ if(!started){ begin(); } });
    root.addEventListener('wheel', function(e){ if(ready && e.deltaY > 0){ enter(); } }, {passive: true});
    root.addEventListener('touchstart', function(e){ y0 = e.touches && e.touches[0] ? e.touches[0].clientY : null; }, {passive: true});
    root.addEventListener('touchmove', function(e){
      if(ready && y0 !== null && e.touches && e.touches[0] && (y0 - e.touches[0].clientY) > 24){ enter(); }
    }, {passive: true});
    cue.addEventListener('click', function(e){ e.stopPropagation(); enter(); });
    skip.addEventListener('click', function(e){ e.stopPropagation(); finish(); });
    doc.addEventListener('keydown', onKey);
    if(!gate){ begin(); }
    else{ try{ beginBtn.focus(); }catch(e){} }
  }catch(err){ /* decorative only: fail quietly */ }
}
'''


def _audio_src() -> str:
    try:
        data = AUDIO_PATH.read_bytes()
    except OSError:
        return ""
    return "data:audio/mpeg;base64," + base64.b64encode(data).decode("ascii")


def render_splash(gate: bool = True):
    """Show the splash once per tab session. Call right after st.set_page_config."""
    src = _audio_src()
    if not src:
        st.warning("Intro sound is off: " + str(AUDIO_PATH) + " was not found. Copy intro.mp3 into the assets folder.")
    boot = (
        "(function(){try{var w=window.parent;erSplash(w.document,w,{gate:"
        + ("true" if gate else "false")
        + ",audio:" + json.dumps(src) + "});}catch(e){}})();"
    )
    components.html("<script>" + JS_SPLASH + boot + "</script>", height=0)
