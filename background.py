"""Scroll-driven 3D road-network background, shared by every page.

The same script (JS_CORE) is used by the Streamlit pages here and is pasted
into landing/index.html, so the whole site moves the same way.

Tune the look with the intensity argument (0.0 invisible to 1.0 strong).
Motion happens only while the visitor scrolls. With "reduce motion" turned on
in the operating system, the background stays still.
"""
import json

import streamlit.components.v1 as components

JS_CORE = r'''
function erMount(doc, win, getMain, intensity, extraCss){
  try{
    if(win.__erBgCleanup){ win.__erBgCleanup(); }
    var old = doc.getElementById('er-bg'); if(old){ old.remove(); }
    if(extraCss && !doc.getElementById('er-bg-style')){
      var st = doc.createElement('style'); st.id = 'er-bg-style'; st.textContent = extraCss; doc.head.appendChild(st);
    }
    var reduce = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var NS = 'http://www.w3.org/2000/svg', S = 2600, STEP = 300, FIRST = 200, N = 8;
    var wrap = doc.createElement('div');
    wrap.id = 'er-bg'; wrap.setAttribute('aria-hidden', 'true');
    wrap.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;z-index:-1;pointer-events:none;overflow:hidden;perspective:1100px;perspective-origin:50% 35%;';
    var plane = doc.createElement('div');
    var mask = 'radial-gradient(closest-side,#000 45%,transparent 100%)';
    plane.style.cssText = 'position:absolute;left:50%;top:50%;width:'+S+'px;height:'+S+'px;margin:-'+(S/2)+'px 0 0 -'+(S/2)+'px;will-change:transform;opacity:'+intensity+';-webkit-mask-image:'+mask+';mask-image:'+mask+';';
    var svg = doc.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 '+S+' '+S); svg.setAttribute('width', S); svg.setAttribute('height', S);
    var h = '', i, j, c, x, y, hot;
    for(i = 0; i < N; i++){
      c = FIRST + i*STEP;
      h += '<line x1="0" y1="'+c+'" x2="'+S+'" y2="'+c+'" stroke="#2a261d" stroke-width="14"/>';
      h += '<line x1="'+c+'" y1="0" x2="'+c+'" y2="'+S+'" stroke="#2a261d" stroke-width="14"/>';
    }
    for(i = 0; i < N; i++){
      for(j = 0; j < N; j++){
        x = FIRST + i*STEP; y = FIRST + j*STEP;
        hot = (x === 800 && y === 1100) || (x === 1700 && y === 1700);
        h += '<rect x="'+(x-13)+'" y="'+(y-13)+'" width="26" height="26" fill="'+(hot?'#c8553d':'#0c0b09')+'" stroke="'+(hot?'#c8553d':'#4a4437')+'" stroke-width="3"/>';
      }
    }
    h += '<path id="er-route" d="M0 1100 H800 V500 H1700 V1700 H2300 V2600" fill="none" stroke="#d6a24a" stroke-opacity="0.6" stroke-width="9"/>';
    svg.innerHTML = h;
    plane.appendChild(svg); wrap.appendChild(plane);
    doc.body.insertBefore(wrap, doc.body.firstChild);

    var route = svg.querySelector('#er-route');
    var L = route.getTotalLength();
    route.style.strokeDasharray = L;
    var target = 0, cur = 0, rp = 0, raf = 0;

    function pose(p, r){
      plane.style.transform = 'translateZ(-150px) rotateX('+(64-14*p)+'deg) rotateZ('+(-10*p)+'deg) translateY('+(-900*p)+'px)';
      route.style.strokeDashoffset = L*(1-r);
    }
    function tick(){
      var rt = 0.12 + 0.88*target;
      cur += (target-cur)*0.1; rp += (rt-rp)*0.06;
      pose(cur, rp);
      if(Math.abs(target-cur) > 0.0004 || Math.abs(rt-rp) > 0.0004){ raf = win.requestAnimationFrame(tick); } else { raf = 0; }
    }
    function pOf(s){ var m = s.scrollHeight - s.clientHeight; return m > 0 ? Math.min(1, Math.max(0, s.scrollTop/m)) : 0; }

    if(reduce){ pose(0.35, 1); return; }

    var main = getMain();
    target = main ? pOf(main) : pOf(doc.scrollingElement || doc.documentElement);
    pose(0, 0); raf = win.requestAnimationFrame(tick);

    function onScroll(e){
      var t = e.target, m = getMain(), s = null;
      if(m && t === m){ s = m; }
      else if(t === doc || t === doc.documentElement || t === doc.body){ s = doc.scrollingElement || doc.documentElement; }
      if(!s){ return; }
      target = pOf(s);
      if(!raf){ raf = win.requestAnimationFrame(tick); }
    }
    doc.addEventListener('scroll', onScroll, true);
    win.__erBgCleanup = function(){
      doc.removeEventListener('scroll', onScroll, true);
      if(raf){ win.cancelAnimationFrame(raf); }
      win.__erBgCleanup = null;
    };
  }catch(err){ /* decorative only: fail quietly */ }
}
'''

STREAMLIT_CSS = (
    "html{background:#0c0b09 !important}"
    "body{background:transparent !important}"
    ".stApp,[data-testid=\"stAppViewContainer\"],[data-testid=\"stMain\"],section.main,"
    "[data-testid=\"stHeader\"]{background:transparent !important}"
)


def render_background(intensity: float = 0.6):
    """Attach the background to the Streamlit page. Call once per page, after the theme CSS."""
    boot = (
        "(function(){try{"
        "var w=window.parent,d=w.document;"
        "erMount(d,w,function(){return d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');},"
        + str(intensity) + "," + json.dumps(STREAMLIT_CSS) + ");"
        "}catch(e){}})();"
    )
    components.html("<script>" + JS_CORE + boot + "</script>", height=0)
