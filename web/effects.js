/**
 * Infernum Aeterna — Effets visuels immersifs
 * Particules canvas + overlay fond dynamique par faction
 * Zéro dépendance externe.
 */
(function () {
  'use strict';

  // ── Config par faction ──────────────────────────
  var FACTION_FX = {
    shinigami: {
      type: 'petals',
      colors: ['rgba(232,232,240,0.35)', 'rgba(232,232,240,0.55)', 'rgba(232,232,240,0.25)'],
      bg: 'radial-gradient(ellipse at 50% 0%, rgba(232,232,240,0.10), transparent 60%)',
      rgb: '232,232,240'
    },
    togabito: {
      type: 'embers',
      colors: ['rgba(139,0,0,0.5)', 'rgba(107,31,168,0.4)', 'rgba(180,40,40,0.35)'],
      bg: 'radial-gradient(at 50% 100%, rgba(107,31,168,0.12), transparent 50%), radial-gradient(at 100% 50%, rgba(139,0,0,0.08), transparent 40%)',
      rgb: '107,31,168'
    },
    arrancar: {
      type: 'sand',
      colors: ['rgba(138,138,122,0.4)', 'rgba(220,210,190,0.3)', 'rgba(160,150,130,0.25)'],
      bg: 'radial-gradient(at 50% 50%, rgba(138,138,122,0.10), transparent 55%)',
      rgb: '138,138,122'
    },
    quincy: {
      type: 'light',
      colors: ['rgba(26,58,107,0.5)', 'rgba(100,150,255,0.35)', 'rgba(60,100,180,0.3)'],
      bg: 'radial-gradient(at 30% 0%, rgba(26,58,107,0.12), transparent 50%), radial-gradient(at 70% 0%, rgba(26,58,107,0.10), transparent 50%)',
      rgb: '26,58,107'
    }
  };

  var DEFAULT_FX = {
    type: 'default',
    colors: ['rgba(201,168,76,0.25)', 'rgba(201,168,76,0.18)'],
    bg: 'radial-gradient(at 50% 50%, rgba(201,168,76,0.06), transparent 50%)',
    rgb: '201,168,76'
  };

  // ── State ───────────────────────────────────────
  var canvas, ctx, overlay;
  var particles = [];
  var currentFX = DEFAULT_FX;
  var W = 0, H = 0;
  var running = false;
  var isMobile = false;
  var isSmall = false;
  var MAX_PARTICLES = 50;
  var SPAWN_RATE = 0.25;

  // ── Helpers ─────────────────────────────────────
  function rand(min, max) { return Math.random() * (max - min) + min; }

  function checkMobile() {
    isMobile = window.innerWidth < 768;
    isSmall = window.innerWidth < 480;
    MAX_PARTICLES = isSmall ? 0 : (isMobile ? 12 : 40);
  }

  function resize() {
    checkMobile();
    if (!canvas) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (isSmall) {
      canvas.style.display = 'none';
    } else {
      canvas.style.display = 'block';
    }
  }

  var resizeTimer;
  function debouncedResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 150);
  }

  // ── Particle factory ────────────────────────────
  function spawnParticle() {
    var fx = currentFX;
    var color = fx.colors[Math.floor(Math.random() * fx.colors.length)];
    var p = { x: 0, y: 0, vx: 0, vy: 0, size: 0, alpha: 1, life: 0, maxLife: 0, color: color, type: fx.type };

    switch (fx.type) {
      case 'petals':
        p.x = rand(0, W);
        p.y = rand(-20, -5);
        p.vx = rand(-0.3, 0.3);
        p.vy = rand(0.4, 1.0);
        p.size = rand(4, 9);
        p.maxLife = rand(200, 400);
        p.phase = rand(0, Math.PI * 2);
        p.rotW = rand(1.5, 3);
        break;

      case 'embers':
        p.x = rand(0, W);
        p.y = rand(H + 5, H + 20);
        p.vx = rand(-0.5, 0.5);
        p.vy = rand(-0.6, -1.4);
        p.size = rand(3, 7);
        p.maxLife = rand(150, 350);
        p.flicker = rand(0, Math.PI * 2);
        break;

      case 'sand':
        p.x = rand(-20, -5);
        p.y = rand(0, H);
        p.vx = rand(0.5, 1.2);
        p.vy = rand(-0.15, 0.15);
        p.size = rand(2, 5);
        p.maxLife = rand(250, 500);
        p.angular = Math.random() < 0.35;
        break;

      case 'light':
        p.x = rand(0, W);
        p.y = rand(H + 5, H + 20);
        p.vx = rand(-0.25, 0.25);
        p.vy = rand(-0.4, -0.8);
        p.size = rand(3, 6);
        p.maxLife = rand(200, 450);
        p.phase = rand(0, Math.PI * 2);
        p.isCross = Math.random() < 0.3;
        break;

      default: // 'default' — gold
        p.x = rand(0, W);
        p.y = rand(0, H);
        p.vx = rand(-0.2, 0.2);
        p.vy = rand(-0.2, 0.2);
        p.size = rand(2, 4);
        p.maxLife = rand(300, 600);
        break;
    }

    p.life = 0;
    return p;
  }

  // ── Draw helpers ────────────────────────────────
  function drawPetal(p) {
    var progress = p.life / p.maxLife;
    var fadeIn = Math.min(progress * 5, 1);
    var fadeOut = Math.max(1 - (progress - 0.7) / 0.3, 0);
    var alpha = Math.min(fadeIn, fadeOut);
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(p.x, p.y);
    // Petal as rotated ellipse
    var angle = Math.sin(p.phase + p.life * 0.02) * 0.5;
    ctx.rotate(angle);
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.ellipse(0, 0, p.size * p.rotW, p.size, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawEmber(p) {
    var progress = p.life / p.maxLife;
    var fadeIn = Math.min(progress * 5, 1);
    var fadeOut = Math.max(1 - (progress - 0.6) / 0.4, 0);
    var flicker = 0.7 + 0.3 * Math.sin(p.flicker + p.life * 0.15);
    var alpha = Math.min(fadeIn, fadeOut) * flicker;
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawSand(p) {
    var progress = p.life / p.maxLife;
    var fadeIn = Math.min(progress * 4, 1);
    var fadeOut = Math.max(1 - (progress - 0.7) / 0.3, 0);
    var alpha = Math.min(fadeIn, fadeOut);
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    if (p.angular) {
      // Angular fragment
      ctx.translate(p.x, p.y);
      ctx.rotate(p.life * 0.01);
      ctx.beginPath();
      ctx.moveTo(-p.size, -p.size * 0.5);
      ctx.lineTo(p.size * 0.7, -p.size * 0.3);
      ctx.lineTo(p.size * 0.5, p.size * 0.6);
      ctx.lineTo(-p.size * 0.3, p.size * 0.4);
      ctx.closePath();
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawLight(p) {
    var progress = p.life / p.maxLife;
    var fadeIn = Math.min(progress * 5, 1);
    var fadeOut = Math.max(1 - (progress - 0.7) / 0.3, 0);
    var osc = 0.8 + 0.2 * Math.sin(p.phase + p.life * 0.05);
    var alpha = Math.min(fadeIn, fadeOut) * osc;
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 1;

    if (p.isCross) {
      // Quincy cross shape (2 lines)
      var s = p.size * 2;
      ctx.beginPath();
      ctx.moveTo(p.x - s, p.y);
      ctx.lineTo(p.x + s, p.y);
      ctx.moveTo(p.x, p.y - s);
      ctx.lineTo(p.x, p.y + s);
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawDefault(p) {
    var progress = p.life / p.maxLife;
    var fadeIn = Math.min(progress * 5, 1);
    var fadeOut = Math.max(1 - (progress - 0.7) / 0.3, 0);
    var alpha = Math.min(fadeIn, fadeOut);
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // ── Update + render loop ────────────────────────
  function tick() {
    if (!running) return;
    requestAnimationFrame(tick);

    if (isSmall) return; // pas de rendu sur petits ecrans

    ctx.clearRect(0, 0, W, H);

    // Spawn
    var maxSpawn = currentFX.type === 'default' ? 25 : MAX_PARTICLES;
    if (particles.length < maxSpawn && Math.random() < SPAWN_RATE) {
      particles.push(spawnParticle());
    }

    // Update + draw
    for (var i = particles.length - 1; i >= 0; i--) {
      var p = particles[i];
      p.life++;
      p.x += p.vx;
      p.y += p.vy;

      // Type-specific motion
      if (p.type === 'petals') {
        p.x += Math.sin(p.phase + p.life * 0.015) * 0.4;
      }

      // Remove dead
      if (p.life >= p.maxLife || p.x < -30 || p.x > W + 30 || p.y < -30 || p.y > H + 30) {
        particles.splice(i, 1);
        continue;
      }

      // Draw
      switch (p.type) {
        case 'petals': drawPetal(p); break;
        case 'embers': drawEmber(p); break;
        case 'sand': drawSand(p); break;
        case 'light': drawLight(p); break;
        default: drawDefault(p); break;
      }
    }
  }

  // ── Emblem SVG builder ──────────────────────────
  function getEmblemSVG(factionKey, color) {
    var c = color || '#fff';
    switch (factionKey) {
      case 'shinigami':
        // Losanges imbriques — 3 diamants concentriques + croix
        return '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="' + c + '">'
          + '<g stroke-width="1.5" opacity="0.7">'
          + '<polygon points="100,20 180,100 100,180 20,100"/>'
          + '<polygon points="100,45 155,100 100,155 45,100"/>'
          + '<polygon points="100,68 132,100 100,132 68,100"/>'
          + '<line x1="100" y1="10" x2="100" y2="190"/>'
          + '<line x1="10" y1="100" x2="190" y2="100"/>'
          + '</g></svg>';

      case 'togabito':
        // Chaines en cercle — 8 maillons ovales en anneau
        var links = '';
        for (var i = 0; i < 8; i++) {
          var angle = (i * 45) * Math.PI / 180;
          var cx = 100 + 65 * Math.cos(angle);
          var cy = 100 + 65 * Math.sin(angle);
          var rot = i * 45;
          links += '<ellipse cx="' + cx.toFixed(1) + '" cy="' + cy.toFixed(1) + '" rx="22" ry="12" transform="rotate(' + rot + ' ' + cx.toFixed(1) + ' ' + cy.toFixed(1) + ')"/>';
        }
        return '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="' + c + '">'
          + '<g stroke-width="1.5" opacity="0.7">' + links + '</g></svg>';

      case 'arrancar':
        // Masque brise — croissant avec fissures + trou d'oeil
        return '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="' + c + '">'
          + '<g stroke-width="1.5" opacity="0.7">'
          + '<path d="M55,60 Q100,30 145,60 Q155,90 145,120 Q130,145 100,155 Q70,145 55,120 Q45,90 55,60 Z"/>'
          + '<circle cx="80" cy="90" r="15"/>'
          + '<circle cx="120" cy="90" r="12" stroke-dasharray="4 3"/>'
          + '<line x1="95" y1="55" x2="90" y2="80" stroke-dasharray="3 2"/>'
          + '<line x1="110" y1="50" x2="115" y2="78" stroke-dasharray="3 2"/>'
          + '<line x1="100" y1="110" x2="100" y2="145" stroke-dasharray="3 2"/>'
          + '<path d="M70,130 Q100,160 130,130" stroke-dasharray="4 3"/>'
          + '</g></svg>';

      case 'quincy':
        // Croix etoilee — etoile 5 branches + croix centrale + cercle
        return '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="' + c + '">'
          + '<g stroke-width="1.5" opacity="0.7">'
          + '<circle cx="100" cy="100" r="75"/>'
          + '<polygon points="100,25 112,78 168,78 122,110 136,165 100,132 64,165 78,110 32,78 88,78"/>'
          + '<line x1="100" y1="35" x2="100" y2="165"/>'
          + '<line x1="35" y1="100" x2="165" y2="100"/>'
          + '<circle cx="100" cy="100" r="20"/>'
          + '</g></svg>';

      default:
        return '';
    }
  }

  // ── Public API ──────────────────────────────────
  window.InfernumFX = {
    init: function () {
      if (running) return;

      // Create overlay
      overlay = document.createElement('div');
      overlay.id = 'fx-bg-overlay';
      document.body.insertBefore(overlay, document.body.firstChild);

      // Create canvas
      canvas = document.createElement('canvas');
      canvas.id = 'fx-particles';
      document.body.insertBefore(canvas, overlay.nextSibling);
      ctx = canvas.getContext('2d');

      resize();
      window.addEventListener('resize', debouncedResize);

      running = true;
      tick();
    },

    setFaction: function (id) {
      var fx = FACTION_FX[id] || DEFAULT_FX;
      var changed = fx !== currentFX;
      currentFX = fx;

      // Update overlay bg
      if (overlay) {
        overlay.style.background = fx.bg;
      }

      // Set --fc-rgb CSS variable for glow effects
      document.documentElement.style.setProperty('--fc-rgb', fx.rgb);

      // Clear particles on faction change for clean transition
      if (changed) {
        particles = [];
      }
    },

    getEmblemSVG: getEmblemSVG
  };
})();
