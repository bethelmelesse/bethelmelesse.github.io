(() => {
  document.documentElement.classList.add('js');
  const header = document.getElementById('siteHeader');
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  const progressBar = document.getElementById('progressBar');
  const yearEl = document.getElementById('year');
  const sections = document.querySelectorAll('main > section, #hero, footer[id]');
  const navAnchors = document.querySelectorAll('.nav-link');

  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Header background + scroll progress
  const onScroll = () => {
    const scrollTop = window.scrollY;
    header.classList.toggle('scrolled', scrollTop > 60);

    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = progress + '%';

    let current = '';
    sections.forEach((sec) => {
      const top = sec.offsetTop - 120;
      if (scrollTop >= top) current = sec.id;
    });
    navAnchors.forEach((a) => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile nav toggle
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.classList.toggle('open', isOpen);
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
  navAnchors.forEach((a) => {
    a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      navToggle.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });

  // Flip cards (click, Enter or Space)
  const flipCards = [...document.querySelectorAll('.flip-card')];
  const setFlipped = (card, on) => {
    card.classList.toggle('flipped', on);
    card.setAttribute('aria-pressed', String(on));
  };
  let stopAutoFlip = () => {};
  flipCards.forEach((card) => {
    const flip = () => {
      stopAutoFlip();
      setFlipped(card, !card.classList.contains('flipped'));
    };
    card.addEventListener('click', (e) => {
      if (!e.target.closest('a')) flip();
    });
    card.addEventListener('keydown', (e) => {
      if (e.target === card && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        flip();
      }
    });
  });

  // Auto-flip: one random card at a time while the grid is on screen,
  // paused on hover, stopped for good once the visitor flips a card
  const hobbyGrid = document.querySelector('.hobby-grid');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (hobbyGrid && flipCards.length > 1 && !reduceMotion) {
    let timer = null, current = null, last = null, inView = false, hovered = false, stopped = false;
    const tick = () => {
      if (current) {
        setFlipped(current, false);
        last = current;
        current = null;
      } else {
        const choices = flipCards.filter((c) => c !== last);
        current = choices[Math.floor(Math.random() * choices.length)];
        setFlipped(current, true);
      }
    };
    const update = () => {
      const run = inView && !hovered && !stopped && !document.hidden;
      if (run && !timer) timer = setInterval(tick, 2200);
      if (!run && timer) { clearInterval(timer); timer = null; }
    };
    stopAutoFlip = () => {
      if (stopped) return;
      stopped = true;
      update();
      if (current) setFlipped(current, false);
      current = null;
    };
    new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; update(); }, { threshold: 0.4 }).observe(hobbyGrid);
    hobbyGrid.addEventListener('mouseenter', () => { hovered = true; update(); });
    hobbyGrid.addEventListener('mouseleave', () => { hovered = false; update(); });
    document.addEventListener('visibilitychange', update);
  }

  // Scroll-reveal animations
  const revealEls = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  revealEls.forEach((el) => observer.observe(el));
})();
