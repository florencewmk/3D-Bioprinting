/* === CONTENT-AWARE SLIDE MOTION (independent of navigation/chart controllers) === */
(() => {
  if (window.slideMotion) return;
  const stage = document.getElementById('deckStage');
  if (!stage || !Element.prototype.animate) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const style = document.getElementById('slide-motion-style') || document.createElement('style');
  style.id = 'slide-motion-style';
  style.textContent = `
    .slide{transition:opacity .62s cubic-bezier(.22,.61,.36,1)}
    .slide.active{z-index:2}
    .slide.motion-exiting{visibility:visible;opacity:0;pointer-events:none;z-index:1}
    /* This controller owns these entrances; keep background/process animations. */
    .slide.active .hero,.slide.active .poster,.slide.active .contents-heading{animation:none}
    @media(prefers-reduced-motion:reduce){
      .slide{transition:none!important}
      .slide.motion-exiting{visibility:hidden}
    }
    @media print{
      .slide{transition:none!important}
      .slide.motion-exiting{visibility:visible!important;opacity:1!important}
    }`;
  if (!style.isConnected) document.head.append(style);
  const slides = [...stage.querySelectorAll('.slide')];
  const running = new Map();
  const cleanup = new Map();
  let current = null;
  let printing = false;
  const title = slide => slide.getAttribute('aria-label')?.replace(/^\d+\.\s*/, '') || '';
  const position = (el, axis) => parseFloat(el.style[axis]) || 0;
  const add = (plan, nodes, delay = 0, duration = 850, lift = 0) => {
    for (const el of nodes) plan.push({el, delay, duration, lift});
  };
  const select = (slide, selector) => [...slide.querySelectorAll(selector)];

  function planFor(slide) {
    const plan = [];
    const name = title(slide);
    let kind = 'evidence';
    if (slide.querySelector('.hero')) {
      kind = 'cover';
      add(plan, select(slide, '.eyebrow'), 0, 800, 10);
      add(plan, select(slide, '.cover-descriptor'), 160, 900, 14);
      add(plan, select(slide, '.cover-focus'), 320, 1100, 18);
      add(plan, select(slide, '.hero-sub,.signature'), 580, 900, 10);
      add(plan, select(slide, '.cover-lung'), 180, 1200);
    } else if (slide.querySelector('.profile-photo')) {
      kind = 'presenter';
      add(plan, select(slide, '.profile-name'), 0, 850, 12);
      // The embedded character animates its own entrance.
      const portrait = slide.querySelector('.profile-photo');
      if (!portrait.querySelector('img[data-intro-src],img[src^="data:image/svg+xml"]')) {
        add(plan, [portrait], 180, 1000);
      }
      // Presenter bullet visibility and click timing belong to its own controller.
    } else if (slide.querySelector('.contents-list')) {
      kind = 'agenda';
      add(plan, select(slide, '.contents-heading'), 0, 900, 14);
      select(slide, '.chapter').forEach((el, i) => add(plan, [el], 220 + i * 210, 800, 12));
    } else if (slide.querySelector('.question-center')) {
      kind = 'question';
      add(plan, select(slide, '.question-center h1'), 220, 1100, 12);
      // Retain the existing 18-second photographic zoom.
    } else if (slide.querySelector('.origin-copy')) {
      kind = 'origin';
      add(plan, select(slide, '.origin-copy'), 0, 1000, 12);
      add(plan, select(slide, '.origin-diagram'), 320, 1100);
      add(plan, select(slide, '.origin-process,.origin-source'), 700, 800);
    } else if (slide.querySelector('#historyTimeline')) {
      kind = 'history';
      add(plan, select(slide, '.history-kicker,.history-heading'), 0, 800, 10);
      add(plan, select(slide, '.history-focus'), 180, 900);
      add(plan, select(slide, '.history-rail'), 350, 1000);
      // Do not animate individual panels: the history controller steps them.
    } else if (slide.querySelector('#publicationChart,#organChart')) {
      kind = 'data';
      add(plan, select(slide, '#publicationChart,#organChart'), 0, 650);
      // Preserve chart-owned year progression, scales and the 6-second reveal.
    } else if (slide.querySelector('.references')) {
      kind = 'references';
      add(plan, select(slide, '.references'), 0, 750);
    } else if (slide.querySelector('.closing-scene')) {
      kind = 'closing';
      add(plan, select(slide, '.closing-scene'), 0, 800);
    } else if (slide.querySelector('.poster')) {
      kind = 'statement';
      add(plan, select(slide, '.poster'), 100, 1100, 16);
      add(plan, select(slide, 'video,.media-credit,.backup-original'), 200, 900);
    } else {
      add(plan, select(slide, '.source-art'), 140, 950);
      const lines = select(slide, ':scope > .textline');
      const comparison = /Four light-based|UV \/ violet|SLA · DLP/.test(name);
      const roadmap = /From research to real-world/.test(name);
      const conclusion = name === 'Layers to living tissue';
      if (conclusion) {
        kind = 'conclusion';
        let step = 0;
        for (const el of lines) {
          const match = el.textContent.trim().match(/^0([1-7])\s/);
          if (match) step = Number(match[1]);
          add(plan, [el], step ? 360 + (step - 1) * 300 : 0, 750);
        }
      } else if (comparison || roadmap) {
        kind = comparison ? 'comparison' : 'roadmap';
        for (const el of lines) {
          const top = position(el, 'top');
          const column = Math.min(comparison ? 3 : 2, Math.floor(position(el, 'left') / (comparison ? 480 : 640)));
          add(plan, [el], top < 280 ? 0 : 380 + column * 260, 800);
        }
      } else {
        kind = /Mechanism|activation|Working|process|layer at a time|Laser|photopolymerization|STLG|TPP/i.test(name) ? 'mechanism' : 'evidence';
        // Keep every wrapped line and bullet in the same reveal band. Opacity
        // alone preserves exact alignment with converted scientific diagrams.
        const tops = [...new Set(lines.map(el => position(el, 'top')).filter(y => y >= 300))].sort((a,b) => a-b);
        const bands = [];
        for (const y of tops) if (!bands.length || y - bands[bands.length - 1] > 115) bands.push(y);
        for (const el of lines) {
          const y = position(el, 'top');
          const band = Math.max(0, bands.findLastIndex(start => y >= start));
          add(plan, [el], y < 300 ? 0 : 350 + Math.min(band, 4) * 180, 800);
        }
      }
      add(plan, select(slide, ':scope > video'), 180, 900);
    }
    if (!plan.length) {
      kind = 'reading';
      add(plan, [...slide.children].filter(el => !el.matches('nav,footer,.sr-only,script,style')), 0, 850);
    }
    slide.dataset.motion = kind;
    return plan;
  }

  // Describe every slide, including later additions, without changing content.
  slides.forEach(slide => {slide.classList.remove('motion-exiting'); planFor(slide);});
  function stop(slide) {
    (running.get(slide) || []).forEach(animation => animation.cancel());
    running.delete(slide);
  }
  function enter(slide) {
    stop(slide);
    if (reduced.matches || printing || document.body.classList.contains('editing')) return;
    const animations = planFor(slide).map(({el, delay, duration, lift}) => {
      const frames = lift
        ? [{opacity:0,translate:`0 ${lift}px`},{opacity:1,translate:'0 0'}]
        : [{opacity:0},{opacity:1}];
      const animation = el.animate(frames, {duration, delay, easing:'cubic-bezier(.22,.61,.36,1)', fill:'backwards'});
      animation.onfinish = () => animation.cancel();
      return animation;
    });
    running.set(slide, animations);
  }
  function sync() {
    const next = stage.querySelector('.slide.active');
    if (!next || next === current) return;
    const previous = current;
    current = next;
    for (const slide of slides) {
      clearTimeout(cleanup.get(slide));
      slide.classList.remove('motion-exiting');
      if (slide !== next) stop(slide);
    }
    if (previous && !reduced.matches && !printing) {
      previous.classList.add('motion-exiting');
      cleanup.set(previous, setTimeout(() => previous.classList.remove('motion-exiting'), 660));
    }
    enter(next);
  }
  new MutationObserver(sync).observe(stage, {subtree:true, attributes:true, attributeFilter:['class']});
  new MutationObserver(() => {
    if (document.body.classList.contains('editing')) slides.forEach(stop);
  }).observe(document.body, {attributes:true, attributeFilter:['class']});
  reduced.addEventListener('change', () => {
    slides.forEach(stop);
    slides.forEach(slide => slide.classList.remove('motion-exiting'));
  });
  addEventListener('beforeprint', () => {printing = true; slides.forEach(stop);});
  addEventListener('afterprint', () => {printing = false;});
  window.slideMotion = {version:1, transitionMs:620, planFor, replay:() => current && enter(current)};
  sync();
})();
