"""Smooth (eased) mouse-wheel scrolling for every page.

The wheel adds to a target position and the page glides toward it, independent of
frame rate. Touch scrolling, keyboard scrolling and the scrollbar stay native.
Inner scrollers (menus, tables) keep their own scrolling. Off with "reduce motion".
"""
import streamlit.components.v1 as components

JS_SMOOTH = r'''
function erSmooth(doc, win, getScroller, extraCss){
  try{
    if(win.__erSmoothCleanup){ win.__erSmoothCleanup(); }
    if(win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches){ return; }
    if(extraCss && !doc.getElementById('er-smooth-style')){
      var st = doc.createElement('style'); st.id = 'er-smooth-style'; st.textContent = extraCss; doc.head.appendChild(st);
    }
    var target = 0, raf = 0, last = 0;
    function maxOf(s){ return Math.max(0, s.scrollHeight - s.clientHeight); }
    function innerCanScroll(t, s, dy){
      for(var n = t; n && n !== s && n !== doc.body && n !== doc.documentElement; n = n.parentElement){
        var oy = win.getComputedStyle(n).overflowY;
        if((oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight + 1){
          if(dy < 0 && n.scrollTop > 0){ return true; }
          if(dy > 0 && n.scrollTop < n.scrollHeight - n.clientHeight - 1){ return true; }
        }
      }
      return false;
    }
    function tick(now){
      var s = getScroller();
      if(!s){ raf = 0; last = 0; return; }
      var d = target - s.scrollTop;
      if(Math.abs(d) < 1){ s.scrollTo({top: target, behavior: 'instant'}); raf = 0; last = 0; return; }
      var dt = last ? Math.min(50, now - last) : 16; last = now;
      var step = d * (1 - Math.exp(-dt / 120));
      if(Math.abs(step) < 1){ step = d > 0 ? 1 : -1; }
      s.scrollTo({top: s.scrollTop + step, behavior: 'instant'});
      raf = win.requestAnimationFrame(tick);
    }
    function onWheel(e){
      if(e.defaultPrevented || e.ctrlKey || e.metaKey){ return; }
      if(doc.getElementById('er-splash')){ return; }
      var s = getScroller(); if(!s){ return; }
      var inDoc = (s === doc.scrollingElement || s === doc.documentElement);
      if(!inDoc && !s.contains(e.target)){ return; }
      if(Math.abs(e.deltaX) > Math.abs(e.deltaY)){ return; }
      var dy = e.deltaMode === 1 ? e.deltaY * 16 : (e.deltaMode === 2 ? e.deltaY * s.clientHeight : e.deltaY);
      if(innerCanScroll(e.target, s, dy)){ return; }
      var m = maxOf(s); if(m <= 0){ return; }
      e.preventDefault();
      if(!raf){ target = s.scrollTop; last = 0; }
      target = Math.max(0, Math.min(m, target + dy));
      if(!raf){ raf = win.requestAnimationFrame(tick); }
    }
    doc.addEventListener('wheel', onWheel, {passive: false});
    win.__erSmoothCleanup = function(){
      doc.removeEventListener('wheel', onWheel, {passive: false});
      if(raf){ win.cancelAnimationFrame(raf); }
      win.__erSmoothCleanup = null;
    };
  }catch(err){ /* decorative only: fail quietly */ }
}
'''

SMOOTH_CSS = "[data-testid=\"stMain\"],section.main{scroll-behavior:smooth}"


def render_smooth_scroll():
    """Call once per page. Works with the page's main Streamlit scroller."""
    boot = (
        "(function(){try{var w=window.parent,d=w.document;"
        "erSmooth(d,w,function(){"
        "var m=d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');"
        "if(m&&m.scrollHeight>m.clientHeight+1){return m;}"
        "var v=d.querySelector('[data-testid=\"stAppViewContainer\"]');"
        "if(v&&v.scrollHeight>v.clientHeight+1){return v;}"
        "return d.scrollingElement||d.documentElement;},"
        "'" + SMOOTH_CSS.replace("\\", "\\\\").replace("'", "\\'") + "');"
        "}catch(e){}})();"
    )
    components.html("<script>" + JS_SMOOTH + boot + "</script>", height=0)
