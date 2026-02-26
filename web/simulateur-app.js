/**
 * INFERNUM AETERNA — Simulateur de Build : Logique interactive
 * State management, validation, rendering, URL hash, events.
 */
(function () {
  'use strict';

  // ══════════════════════════════════════════════════════════════════════════
  //  STATE
  // ══════════════════════════════════════════════════════════════════════════

  var S = {
    faction: null,      // "shinigami" | "togabito" | "arrancar" | "quincy"
    rangIdx: 0,         // index dans SIM_RANGS[faction]
    voieIdx: 0,         // index dans la liste des voies
    unlocked: {},       // { aptId: true }
    selected: null,     // apt id or null
  };

  var PALIER_NOM = {1: "\u25C8 \u00C9veil", 2: "\u25C6 Ma\u00EEtrise", 3: "\u2726 Transcendance"};

  // ══════════════════════════════════════════════════════════════════════════
  //  HELPERS
  // ══════════════════════════════════════════════════════════════════════════

  function $(id) { return document.getElementById(id); }

  function faction() { return SIM_FACTIONS[S.faction]; }
  function rangs() { return SIM_RANGS[S.faction]; }
  function rang() { return rangs()[S.rangIdx]; }
  function voies() { return faction().voies; }
  function voie() { return voies()[S.voieIdx]; }

  function budget() { return rang().budget; }

  function spent() {
    var total = 0;
    var f = faction();
    for (var i = 0; i < f.voies.length; i++) {
      var apts = f.voies[i].apt;
      for (var j = 0; j < apts.length; j++) {
        if (S.unlocked[apts[j].id]) total += apts[j].c;
      }
    }
    return total;
  }

  function spentInVoie(voieObj) {
    var total = 0;
    for (var j = 0; j < voieObj.apt.length; j++) {
      if (S.unlocked[voieObj.apt[j].id]) total += voieObj.apt[j].c;
    }
    return total;
  }

  function findApt(aptId) {
    var f = faction();
    for (var i = 0; i < f.voies.length; i++) {
      for (var j = 0; j < f.voies[i].apt.length; j++) {
        if (f.voies[i].apt[j].id === aptId) return f.voies[i].apt[j];
      }
    }
    return null;
  }

  function findAptVoie(aptId) {
    var f = faction();
    for (var i = 0; i < f.voies.length; i++) {
      for (var j = 0; j < f.voies[i].apt.length; j++) {
        if (f.voies[i].apt[j].id === aptId) return f.voies[i];
      }
    }
    return null;
  }

  function countInVoie(voieObj, palier) {
    var n = 0;
    for (var j = 0; j < voieObj.apt.length; j++) {
      if (voieObj.apt[j].p === palier && S.unlocked[voieObj.apt[j].id]) n++;
    }
    return n;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  VALIDATION (port de data/aptitudes/__init__.py)
  // ══════════════════════════════════════════════════════════════════════════

  function canUnlock(aptId) {
    var apt = findApt(aptId);
    if (!apt) return {ok: false, msg: "Aptitude inconnue."};

    if (S.unlocked[aptId]) return {ok: false, msg: "D\u00E9j\u00E0 d\u00E9bloqu\u00E9e."};

    // Acc\u00E8s restreint (voies sp\u00E9ciales : Shunk\u014D, Kenpachi)
    var voieCheck = findAptVoie(aptId);
    if (voieCheck && voieCheck.accesRestreint) {
      return {ok: false, msg: "Voie \u00E0 acc\u00E8s restreint : " + voieCheck.accesRestreint};
    }

    // Budget
    var cost = apt.c;
    if (spent() + cost > budget()) {
      return {ok: false, msg: "Budget insuffisant (" + (spent()+cost) + " > " + budget() + " \u970A\u529B)."};
    }

    // Prereqs
    for (var i = 0; i < apt.prereqIds.length; i++) {
      if (!S.unlocked[apt.prereqIds[i]]) {
        var pre = findApt(apt.prereqIds[i]);
        return {ok: false, msg: "Pr\u00E9requis manquant : " + (pre ? pre.nom : apt.prereqIds[i])};
      }
    }

    var v = findAptVoie(aptId);

    // P2: at least 1 P1 in same voie
    if (apt.p === 2) {
      if (countInVoie(v, 1) < 1) {
        return {ok: false, msg: "Au moins 1 aptitude P1 dans cette Voie requise."};
      }
    }

    // P3: rank check + 2 P2 in voie
    if (apt.p === 3) {
      if (!rang().p3) {
        return {ok: false, msg: "Votre rang ne permet pas d'acc\u00E9der au Palier 3."};
      }
      if (countInVoie(v, 2) < 2) {
        return {ok: false, msg: "Au moins 2 aptitudes P2 dans cette Voie requises."};
      }
    }

    // rangMin check
    if (apt.rangMin) {
      var minBudget = getRangBudget(apt.rangMin);
      if (budget() < minBudget) {
        return {ok: false, msg: "Rang minimum requis : " + apt.rangMin};
      }
    }

    return {ok: true, msg: ""};
  }

  function getRangBudget(rangCle) {
    var r = rangs();
    for (var i = 0; i < r.length; i++) {
      if (r[i].cle === rangCle) return r[i].budget;
    }
    return 999;
  }

  function canRemove(aptId) {
    if (!S.unlocked[aptId]) return {ok: false, msg: "Non d\u00E9bloqu\u00E9e."};

    // Check dependants
    var f = faction();
    for (var i = 0; i < f.voies.length; i++) {
      for (var j = 0; j < f.voies[i].apt.length; j++) {
        var other = f.voies[i].apt[j];
        if (other.id === aptId || !S.unlocked[other.id]) continue;
        for (var k = 0; k < other.prereqIds.length; k++) {
          if (other.prereqIds[k] === aptId) {
            return {ok: false, msg: other.nom + " d\u00E9pend de cette aptitude."};
          }
        }
      }
    }
    return {ok: true, msg: ""};
  }

  function nodeState(apt) {
    if (S.unlocked[apt.id]) return "unlocked";
    var r = canUnlock(apt.id);
    if (r.ok) return "available";
    // Distinguish "blocked by rank/P3" from simply locked
    if (apt.p === 3 && !rang().p3) return "blocked";
    if (apt.rangMin && budget() < getRangBudget(apt.rangMin)) return "blocked";
    return "locked";
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  RENDERING : Faction Select
  // ══════════════════════════════════════════════════════════════════════════

  function renderFactionSelect() {
    var grid = $('factionGrid');
    var html = '';
    var keys = ["shinigami", "togabito", "arrancar", "quincy"];
    var rgbs = {
      shinigami: "232,232,240", togabito: "107,31,168",
      arrancar: "138,138,122", quincy: "26,58,107"
    };
    keys.forEach(function(k) {
      var f = SIM_FACTIONS[k];
      var emblem = '';
      if (window.InfernumFX && window.InfernumFX.getEmblemSVG) {
        emblem = InfernumFX.getEmblemSVG(k, f.couleur);
      }
      html += '<div class="faction-card" data-faction="' + k + '" style="--card-color:' + f.couleur + ';--card-rgb:' + rgbs[k] + '">';
      html += '<div class="card-kanji">' + f.kanji + '</div>';
      if (emblem) html += '<div class="card-emblem">' + emblem + '</div>';
      html += '<div class="card-nom" style="color:' + f.couleur + '">' + f.nom + '</div>';
      html += '<div class="card-accroche">' + f.accroche + '</div>';
      html += '</div>';
    });
    grid.innerHTML = html;

    grid.querySelectorAll('.faction-card').forEach(function(card) {
      card.addEventListener('click', function() {
        selectFaction(this.dataset.faction);
      });
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  RENDERING : Build Screen
  // ══════════════════════════════════════════════════════════════════════════

  function selectFaction(fk) {
    S.faction = fk;
    S.rangIdx = 0;
    S.voieIdx = 0;
    S.unlocked = {};
    S.selected = null;

    // Apply faction color
    var f = faction();
    document.documentElement.style.setProperty('--faction-color', f.couleur);
    var rgbs = {shinigami:"232,232,240",togabito:"107,31,168",arrancar:"138,138,122",quincy:"26,58,107"};
    document.documentElement.style.setProperty('--fc-rgb', rgbs[fk]);

    if (window.InfernumFX) InfernumFX.setFaction(fk);

    $('factionSelect').style.display = 'none';
    $('buildScreen').style.display = 'flex';
    $('btnChangeFaction').style.display = '';

    renderRankBar();
    renderVoieBar();
    renderTree();
    renderMeter();
    renderDetail();
    renderSummary();
    updateHash();
  }

  function renderRankBar() {
    var r = rangs();
    var html = '';
    r.forEach(function(rk, i) {
      var cls = i === S.rangIdx ? ' active' : '';
      html += '<div class="rank-chip' + cls + '" data-idx="' + i + '">';
      html += rk.emoji + ' ' + rk.nom;
      html += ' <span class="chip-budget">[' + rk.budget + ']</span>';
      html += '</div>';
    });
    $('rankChips').innerHTML = html;

    $('rankChips').querySelectorAll('.rank-chip').forEach(function(chip) {
      chip.addEventListener('click', function() {
        S.rangIdx = parseInt(this.dataset.idx);
        renderRankBar();
        renderTree();
        renderMeter();
        renderDetail();
        renderSummary();
        updateHash();
      });
    });
  }

  function renderVoieBar() {
    var vs = voies();
    var html = '';
    vs.forEach(function(v, i) {
      var cls = i === S.voieIdx ? ' active' : '';
      html += '<button class="voie-pill' + cls + '" data-idx="' + i + '">';
      html += v.kanji + ' ' + v.nom;
      html += '</button>';
    });
    $('voieBar').innerHTML = html;

    $('voieBar').querySelectorAll('.voie-pill').forEach(function(pill) {
      pill.addEventListener('click', function() {
        S.voieIdx = parseInt(this.dataset.idx);
        S.selected = null;
        renderVoieBar();
        renderTree();
        renderDetail();
      });
    });
  }

  function renderMeter() {
    var s = spent();
    var b = budget();
    var pct = b > 0 ? Math.min(100, (s / b) * 100) : 0;
    var fill = $('meterFill');
    fill.style.width = pct + '%';

    // Color based on usage
    var ratio = b > 0 ? s / b : 0;
    if (ratio < 0.6) {
      fill.style.background = 'linear-gradient(90deg, var(--faction-color), var(--faction-color))';
    } else if (ratio < 0.85) {
      fill.style.background = 'linear-gradient(90deg, var(--faction-color), #C9A84C)';
    } else {
      fill.style.background = 'linear-gradient(90deg, #C9A84C, #CC4444)';
    }

    $('meterLabel').textContent = s + ' / ' + b + ' \u970A\u529B';
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  RENDERING : Tree
  // ══════════════════════════════════════════════════════════════════════════

  function renderTree() {
    var v = voie();
    var apts = v.apt;

    // Group by palier
    var rows = {1: [], 2: [], 3: []};
    apts.forEach(function(a) { rows[a.p].push(a); });

    // Layout dimensions
    var W = 620, H = 420;
    var yMap = {1: 12, 2: 48, 3: 85};
    var positions = {};

    // Position nodes in each row
    [1, 2, 3].forEach(function(p) {
      var items = rows[p];
      var n = items.length;
      if (n === 0) return;
      var margin = 14;
      var span = 100 - 2 * margin;
      items.forEach(function(a, j) {
        var x = n === 1 ? 50 : margin + (j * span / (n - 1));
        positions[a.id] = {x: x, y: yMap[p]};
      });
    });

    // Build SVG connections
    var svgPaths = '';
    apts.forEach(function(a) {
      if (!a.prereqIds || !a.prereqIds.length) return;
      var to = positions[a.id];
      if (!to) return;
      a.prereqIds.forEach(function(pid) {
        var from = positions[pid];
        if (!from) return; // cross-voie prereq, skip line
        var x1 = from.x * W / 100, y1 = from.y * H / 100;
        var x2 = to.x * W / 100, y2 = to.y * H / 100;
        var cy1 = y1 + (y2 - y1) * 0.4;
        var cy2 = y1 + (y2 - y1) * 0.6;

        // Determine connection state
        var cls = 'conn-inactive';
        if (S.unlocked[pid] && S.unlocked[a.id]) {
          cls = 'conn-active';
        } else if (S.unlocked[pid]) {
          cls = 'conn-available';
        }

        svgPaths += '<path class="' + cls + '" d="M' + x1 + ',' + y1 + ' C' + x1 + ',' + cy1 + ' ' + x2 + ',' + cy2 + ' ' + x2 + ',' + y2 + '"/>';
      });
    });

    // Build HTML
    var html = '<div class="tree-svg-wrap" style="height:' + H + 'px">';
    html += '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid meet">';
    html += svgPaths;
    html += '</svg>';

    // Nodes
    apts.forEach(function(a) {
      var pos = positions[a.id];
      if (!pos) return;
      var state = nodeState(a);
      var sel = S.selected === a.id ? ' selected' : '';
      html += '<div class="tree-node node-' + state + sel + '" data-id="' + a.id + '" data-p="' + a.p + '" style="left:' + pos.x + '%;top:' + pos.y + '%">';
      html += '<div class="node-circle">';
      html += '<span class="node-kanji">' + a.kanji + '</span>';
      html += '<span class="node-check">\u2713</span>';
      html += '</div>';
      html += '<span class="node-label">' + a.nom + '</span>';
      html += '</div>';
    });

    html += '</div>';
    $('treeCanvas').innerHTML = html;

    // Bind node clicks
    $('treeCanvas').querySelectorAll('.tree-node').forEach(function(node) {
      node.addEventListener('click', function() {
        S.selected = this.dataset.id;
        renderTree();
        renderDetail();
      });
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  RENDERING : Detail Panel
  // ══════════════════════════════════════════════════════════════════════════

  function renderDetail() {
    if (!S.selected) {
      $('detailEmpty').style.display = 'flex';
      $('detailContent').classList.remove('visible');
      return;
    }

    var apt = findApt(S.selected);
    if (!apt) return;

    $('detailEmpty').style.display = 'none';
    $('detailContent').classList.add('visible');

    $('detPalier').textContent = PALIER_NOM[apt.p] + ' \u2014 ' + apt.c + ' \u970A\u529B';
    $('detNom').textContent = apt.nom;
    $('detKanji').textContent = apt.kanji;
    $('detDesc').textContent = apt.desc;

    // Prereqs
    if (apt.prereqIds.length > 0) {
      var names = apt.prereqIds.map(function(pid) {
        var pa = findApt(pid);
        var met = S.unlocked[pid];
        return '<span style="color:' + (met ? '#4CAF50' : '#CC4444') + '">' + (pa ? pa.nom : pid) + (met ? ' \u2713' : ' \u2717') + '</span>';
      });
      $('detPrereqs').innerHTML = 'Pr\u00E9requis : ' + names.join(' + ');
      $('detPrereqs').style.display = '';
    } else {
      $('detPrereqs').style.display = 'none';
    }

    // Condition RP
    if (apt.cond) {
      $('detCond').textContent = '\u26A0 ' + apt.cond;
      $('detCond').style.display = '';
    } else {
      $('detCond').style.display = 'none';
    }

    // Button
    var btn = $('detBtn');
    if (S.unlocked[apt.id]) {
      var rem = canRemove(apt.id);
      btn.textContent = 'Retirer';
      btn.className = 'detail-btn btn-remove';
      btn.disabled = !rem.ok;
      btn.title = rem.ok ? '' : rem.msg;
      btn.onclick = function() { doRemove(apt.id); };
    } else {
      var un = canUnlock(apt.id);
      btn.textContent = un.ok ? 'D\u00E9bloquer (' + apt.c + ' \u970A\u529B)' : un.msg;
      btn.className = 'detail-btn';
      btn.disabled = !un.ok;
      btn.title = '';
      btn.onclick = function() { doUnlock(apt.id); };
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  ACTIONS
  // ══════════════════════════════════════════════════════════════════════════

  function doUnlock(aptId) {
    var r = canUnlock(aptId);
    if (!r.ok) return;
    S.unlocked[aptId] = true;

    // Flash animation
    var node = document.querySelector('.tree-node[data-id="' + aptId + '"]');
    if (node) {
      node.style.animation = 'unlockFlash 0.5s ease';
      setTimeout(function() { node.style.animation = ''; }, 500);
    }

    renderTree();
    renderMeter();
    renderDetail();
    renderSummary();
    updateHash();
  }

  function doRemove(aptId) {
    var r = canRemove(aptId);
    if (!r.ok) return;
    delete S.unlocked[aptId];
    renderTree();
    renderMeter();
    renderDetail();
    renderSummary();
    updateHash();
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  RENDERING : Summary
  // ══════════════════════════════════════════════════════════════════════════

  function renderSummary() {
    if (!S.faction) return;
    var f = faction();
    var html = '';
    f.voies.forEach(function(v) {
      var s = spentInVoie(v);
      if (s > 0) {
        html += '<span><span class="sv-name">' + v.nom + '</span>: ' + s + '</span>';
      }
    });
    if (!html) html = '<span>Aucune aptitude d\u00E9bloqu\u00E9e</span>';
    $('summaryVoies').innerHTML = html;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  URL HASH SERIALIZATION
  // ══════════════════════════════════════════════════════════════════════════

  function updateHash() {
    if (!S.faction) return;
    var ids = Object.keys(S.unlocked);
    var hash = S.faction + '.' + rang().cle;
    if (ids.length > 0) hash += '.' + ids.join(',');
    history.replaceState(null, '', '#' + hash);
  }

  function loadFromHash() {
    var hash = location.hash.replace('#', '');
    if (!hash) return false;
    var parts = hash.split('.');
    if (parts.length < 2) return false;

    var fk = parts[0];
    var rangCle = parts[1];
    var aptIds = parts[2] ? parts[2].split(',') : [];

    if (!SIM_FACTIONS[fk]) return false;

    S.faction = fk;

    // Find rang index
    var r = SIM_RANGS[fk];
    S.rangIdx = 0;
    for (var i = 0; i < r.length; i++) {
      if (r[i].cle === rangCle) { S.rangIdx = i; break; }
    }

    // Load aptitudes
    S.unlocked = {};
    aptIds.forEach(function(id) {
      if (id) S.unlocked[id] = true;
    });

    S.voieIdx = 0;
    S.selected = null;

    return true;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  EXPORT / IMPORT
  // ══════════════════════════════════════════════════════════════════════════

  function exportJSON() {
    return JSON.stringify({
      v: 1,
      faction: S.faction,
      rang: rang().cle,
      aptitudes: Object.keys(S.unlocked)
    }, null, 2);
  }

  function importJSON(json) {
    try {
      var data = JSON.parse(json);
      if (!data.faction || !SIM_FACTIONS[data.faction]) {
        showToast('Faction invalide dans le JSON.');
        return;
      }
      selectFaction(data.faction);
      // Set rang
      var r = SIM_RANGS[data.faction];
      for (var i = 0; i < r.length; i++) {
        if (r[i].cle === data.rang) { S.rangIdx = i; break; }
      }
      S.unlocked = {};
      if (data.aptitudes) {
        data.aptitudes.forEach(function(id) { S.unlocked[id] = true; });
      }
      renderRankBar();
      renderTree();
      renderMeter();
      renderDetail();
      renderSummary();
      updateHash();
      showToast('Build import\u00E9 avec succ\u00E8s !');
    } catch (e) {
      showToast('JSON invalide : ' + e.message);
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  TOAST
  // ══════════════════════════════════════════════════════════════════════════

  var toastTimer;
  function showToast(msg) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { t.classList.remove('show'); }, 2500);
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  EVENT BINDINGS
  // ══════════════════════════════════════════════════════════════════════════

  function bindEvents() {
    // Change faction
    $('btnChangeFaction').addEventListener('click', function(e) {
      e.preventDefault();
      S.faction = null;
      S.unlocked = {};
      S.selected = null;
      $('buildScreen').style.display = 'none';
      $('factionSelect').style.display = '';
      $('btnChangeFaction').style.display = 'none';
      history.replaceState(null, '', location.pathname);
      document.documentElement.style.setProperty('--faction-color', 'var(--or-ancien)');
      if (window.InfernumFX) InfernumFX.setFaction('default');
    });

    // Summary toggle
    $('summaryToggle').addEventListener('click', function() {
      this.classList.toggle('open');
      $('summaryDetails').classList.toggle('open');
    });

    // Copy link
    $('btnCopyLink').addEventListener('click', function() {
      navigator.clipboard.writeText(location.href).then(function() {
        showToast('Lien copi\u00E9 !');
      });
    });

    // Export JSON
    $('btnExportJSON').addEventListener('click', function() {
      var json = exportJSON();
      navigator.clipboard.writeText(json).then(function() {
        showToast('JSON copi\u00E9 dans le presse-papier !');
      });
    });

    // Import JSON
    $('btnImportJSON').addEventListener('click', function() {
      $('importTextarea').value = '';
      $('importModal').classList.add('open');
    });
    $('importCancel').addEventListener('click', function() {
      $('importModal').classList.remove('open');
    });
    $('importConfirm').addEventListener('click', function() {
      var val = $('importTextarea').value.trim();
      $('importModal').classList.remove('open');
      if (val) importJSON(val);
    });

    // Reset
    $('btnReset').addEventListener('click', function() {
      S.unlocked = {};
      S.selected = null;
      renderTree();
      renderMeter();
      renderDetail();
      renderSummary();
      updateHash();
      showToast('Build r\u00E9initialis\u00E9.');
    });

    // Hash change
    window.addEventListener('hashchange', function() {
      if (loadFromHash()) {
        var f = faction();
        document.documentElement.style.setProperty('--faction-color', f.couleur);
        var rgbs = {shinigami:"232,232,240",togabito:"107,31,168",arrancar:"138,138,122",quincy:"26,58,107"};
        document.documentElement.style.setProperty('--fc-rgb', rgbs[S.faction]);
        if (window.InfernumFX) InfernumFX.setFaction(S.faction);
        $('factionSelect').style.display = 'none';
        $('buildScreen').style.display = 'flex';
        $('btnChangeFaction').style.display = '';
        renderRankBar();
        renderVoieBar();
        renderTree();
        renderMeter();
        renderDetail();
        renderSummary();
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  INIT
  // ══════════════════════════════════════════════════════════════════════════

  function init() {
    // Init FX
    if (window.InfernumFX) {
      InfernumFX.init();
    }

    renderFactionSelect();
    bindEvents();

    // Check for hash on load
    if (loadFromHash()) {
      selectFaction(S.faction);
      // Re-apply loaded state (selectFaction resets unlocked)
      // So we reload from hash after faction is set
      loadFromHash();
      renderRankBar();
      renderVoieBar();
      renderTree();
      renderMeter();
      renderDetail();
      renderSummary();
    }
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
