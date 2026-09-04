/**
 * Myntra Discovery Engine — Executive Research Instrumentation & PM Strategic Logic
 * Stitch Design System Implementation | Dynamic Data Binding
 * With Live Transparency Links to Original Google Docs & Spreadsheets
 */

const SOURCE_URLS = {
  interview: "https://docs.google.com/document/d/1PfXdj0nd1k7wpuq-AXTnNjqaLadSdzhq75SQh2O2dXg/edit?usp=sharing",
  reddit: "https://docs.google.com/document/d/1aY-pxt7R6Vbt_EgghBqK9c8MBJIzO-3bphdv72gQFsw/edit?usp=sharing",
  survey: "https://docs.google.com/spreadsheets/d/18k-B7lXFusoeXbrDY9tJkUOqNBKeMy6hTubwGkQrxOI/edit?usp=sharing"
};

/**
 * Returns a clickable transparency link for supported sources (Interview, Reddit, Survey),
 * or standard text badge for Play Store.
 */
function getSourceLink(source, label, badgeClasses = "") {
  const s = (source || "").toLowerCase();
  const url = SOURCE_URLS[s];
  if (url) {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="${badgeClasses} hover:opacity-85 transition inline-flex items-center gap-1 cursor-pointer underline-offset-2 hover:underline" title="Verify original record in ${s.toUpperCase()} Google Doc/Sheet ↗">
      <span>${label}</span>
      <span class="material-symbols-outlined text-[12px] opacity-75">open_in_new</span>
    </a>`;
  }
  return `<span class="${badgeClasses}">${label}</span>`;
}

document.addEventListener('DOMContentLoaded', () => {
  const data = window.ENGINE_DATA;
  if (!data) {
    console.error('ENGINE_DATA not initialized. Verify data.js script inclusion.');
    return;
  }

  // 1. Render Signal Funnel (5-stage Stepper)
  renderFunnel(data.funnel);

  // 2. Render Ranked Opportunities Ledger (All 11 Real Taxonomy Blockers)
  renderRankedLedger(data.opportunities);

  // 3. Render Qualitative Deliberation Archetypes
  renderDeepDives();

  // 4. Initialize MVP Sandbox Tabs
  initSandbox();

  // 5. Initialize RAG Research Console
  initRAGConsole(data.rag_qa || [], data.records || []);

  // 6. Initialize Data Lab & Specimen Explorer
  renderEvidenceWorkbench(data.records || []);

  // 7. Render Source Asymmetry Matrix (4 Sources)
  renderSourceAsymmetry(data.counts);

  // 8. Render Co-Occurrence Engine
  renderCoOccurrenceEngine(data.counts.co_occurrences);
});

/**
 * VIEW SWITCHER: EXECUTIVE STRATEGY vs RAG CHAT vs DATA LAB
 */
window.switchMainView = function(viewKey) {
  const views = {
    executive: document.getElementById('view-executive'),
    rag: document.getElementById('view-rag'),
    lab: document.getElementById('view-lab')
  };

  const navButtons = document.querySelectorAll('.nav-view-btn');

  Object.keys(views).forEach(k => {
    const el = views[k];
    if (el) {
      if (k === viewKey) {
        el.classList.remove('hidden');
        el.classList.add('flex');
      } else {
        el.classList.add('hidden');
        el.classList.remove('flex');
      }
    }
  });

  navButtons.forEach(btn => {
    const target = btn.getAttribute('data-target');
    if (target === `view-${viewKey}`) {
      btn.className = "nav-view-btn px-space-md py-space-xs rounded-xl transition-all font-body-md text-body-md bg-primary-container text-on-primary-container font-semibold shadow-sm";
    } else {
      btn.className = "nav-view-btn px-space-md py-space-xs rounded-xl transition-all font-body-md text-body-md text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface";
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
};

/**
 * PANEL 1: THE SIGNAL FUNNEL (STITCH 5-STAGE STEPPER)
 */
function renderFunnel(funnel) {
  const container = document.getElementById('funnel-pipeline-container');
  if (!container) return;

  const stages = [
    {
      stage: "Stage 01",
      metric: "63,014",
      label: "Raw Reviews",
      subTag: "Raw Unstructured Feed",
      delta: "",
      deltaClass: "",
      dotColor: "bg-outline",
      bgClass: "bg-surface-container-low"
    },
    {
      stage: "Stage 02",
      metric: "12,557",
      label: "Length ≥ 15 Tokens",
      subTag: "Low-effort filtered",
      delta: "-50,457 noise",
      deltaClass: "text-error font-semibold",
      dotColor: "",
      bgClass: "bg-surface-container-low"
    },
    {
      stage: "Stage 03",
      metric: "1,591",
      label: "Wishlist Intent",
      subTag: "Pre-purchase grammar",
      delta: "",
      deltaClass: "",
      dotColor: "bg-primary",
      bgClass: "bg-surface-container-low"
    },
    {
      stage: "Stage 04: Isolated",
      metric: "296",
      label: "Deliberation Rigor",
      subTag: "0.47% Signal Density",
      delta: "",
      deltaClass: "",
      dotColor: "bg-secondary animate-ping",
      bgClass: "bg-secondary-container/20 border border-secondary/30",
      highlightMetric: "text-secondary"
    },
    {
      stage: "Stage 05: Base",
      metric: "384",
      label: "Integrated Specimen",
      subTag: "4 Multi-Source Corpora",
      delta: "",
      deltaClass: "",
      dotColor: "material-symbols-outlined text-primary text-[14px]",
      dotIcon: "dataset",
      bgClass: "bg-surface-container-high"
    }
  ];

  container.innerHTML = stages.map(s => `
    <div class="flex flex-col p-space-md rounded-xl ${s.bgClass} transition-all">
      <div class="flex items-center justify-between mb-space-xs">
        <span class="font-label-sm text-label-sm text-on-surface-variant uppercase">${s.stage}</span>
        ${s.delta ? `<span class="font-label-sm text-label-sm ${s.deltaClass}">${s.delta}</span>` : ''}
        ${s.dotColor ? (s.dotIcon ? `<span class="${s.dotColor}">${s.dotIcon}</span>` : `<span class="w-2 h-2 rounded-full ${s.dotColor}"></span>`) : ''}
      </div>
      <span class="font-headline-lg text-headline-lg font-semibold tracking-tight ${s.highlightMetric || 'text-on-surface'}">${s.metric}</span>
      <span class="font-body-sm text-body-sm text-on-surface-variant mt-space-2xs">${s.label}</span>
      <span class="font-label-sm text-label-sm text-on-surface-variant bg-surface-container-lowest px-space-xs py-space-2xs rounded w-fit mt-space-xs border border-outline-variant/30">${s.subTag}</span>
    </div>
  `).join('');
}

/**
 * PANEL 2: RANKED OPPORTUNITIES LEDGER
 */
function renderRankedLedger(opportunities) {
  const tbody = document.getElementById('ledger-table-body');
  if (!tbody) return;

  tbody.innerHTML = opportunities.map(opp => {
    const prev = opp.prevalence;
    const elast = opp.elasticity;
    const owner = opp.ownership.owner;
    const wRate = (opp.source_weighting && opp.source_weighting.weighted_rate !== undefined) 
      ? opp.source_weighting.weighted_rate.toFixed(4)
      : '0.0000';

    const bySrc = prev.by_source || {};
    const intCnt = bySrc.interview ? bySrc.interview.count : 0;
    const survCnt = bySrc.survey ? bySrc.survey.count : 0;
    const redCnt = bySrc.reddit ? bySrc.reddit.count : 0;
    const psCnt = bySrc.play_store ? bySrc.play_store.count : 0;

    let elastHtml = '';
    if (elast === null) {
      elastHtml = `<span class="px-space-xs py-space-2xs rounded bg-surface-container text-on-surface-variant font-label-sm text-label-sm">null: unasked</span>`;
    } else {
      const isSmallSample = elast.denominator < 5;
      const rateBg = elast.rate >= 0.5 ? 'bg-secondary-fixed/50 text-on-secondary-fixed-variant' : (elast.rate > 0 ? 'bg-primary-fixed/40 text-on-primary-fixed-variant' : 'bg-error-container/40 text-on-error-container');
      
      elastHtml = `
        <div class="flex flex-col gap-1">
          <span class="px-space-xs py-space-2xs rounded ${rateBg} font-label-sm text-label-sm font-semibold w-fit">
            ${elast.fraction} (${elast.percentage}%)
          </span>
          ${isSmallSample ? `<span class="font-label-sm text-label-sm text-tertiary font-bold">[⚠️ n=${elast.denominator} &lt; 5]</span>` : ''}
        </div>
      `;
    }

    let ownerBadge = '';
    if (owner === 'product') {
      ownerBadge = `<span class="px-space-xs py-space-2xs rounded bg-primary text-on-primary font-label-sm text-label-sm font-semibold">• PRODUCT</span>`;
    } else if (owner === 'shared') {
      ownerBadge = `<span class="px-space-xs py-space-2xs rounded bg-secondary text-on-secondary font-label-sm text-label-sm font-semibold">• SHARED</span>`;
    } else if (owner === 'ops') {
      ownerBadge = `<span class="px-space-xs py-space-2xs rounded bg-surface-container-highest text-on-surface font-label-sm text-label-sm font-semibold">• OPS</span>`;
    } else {
      ownerBadge = `<span class="px-space-xs py-space-2xs rounded bg-surface-container text-on-surface-variant font-label-sm text-label-sm">• NEITHER</span>`;
    }

    const evidenceHtml = opp.evidence_samples && opp.evidence_samples.length > 0
      ? opp.evidence_samples.slice(0, 3).map(sample => `
          <div class="flex flex-col gap-space-2xs p-space-sm rounded-lg bg-surface-container-lowest border border-outline-variant/30">
            <div class="flex items-center justify-between font-label-sm text-label-sm">
              ${getSourceLink(sample.source, `[${sample.source.toUpperCase()}]`, 'px-space-xs py-space-2xs rounded bg-primary-fixed text-on-primary-fixed font-bold')}
              <span class="text-on-surface-variant">ID: ${sample.record_id.slice(0, 8)}</span>
            </div>
            <p class="font-body-sm text-body-sm text-on-surface italic mt-space-2xs">"${escapeHtml(sample.text)}"</p>
          </div>
        `).join('')
      : `<span class="font-body-sm text-body-sm text-on-surface-variant italic">No samples in narrow corpus.</span>`;

    return `
      <!-- Main Data Row -->
      <tr class="hover:bg-surface-container-low/60 transition-colors cursor-pointer group" onclick="toggleLedgerDetail('detail-row-${opp.rank}')">
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-xs">
            <span class="font-label-md text-label-md font-bold text-primary">#${opp.rank}</span>
            <span class="font-headline-sm text-headline-sm text-on-surface group-hover:text-primary transition-colors font-semibold">${opp.blocker_type}</span>
          </div>
          <span class="font-body-sm text-body-sm text-on-surface-variant block mt-space-2xs">${opp.ownership.rationale}</span>
        </td>

        <td class="py-space-md px-space-md text-right font-label-md text-label-md font-bold text-on-surface">
          ${wRate}
        </td>

        <td class="py-space-md px-space-md">
          <div class="flex flex-col gap-1">
            <span class="font-label-sm text-label-sm font-semibold text-on-surface">${prev.overall_count} / ${prev.overall_denominator} (${prev.overall_percentage}%)</span>
            <div class="flex items-center gap-space-2xs font-label-sm text-label-sm flex-wrap">
              ${getSourceLink('interview', `Int: ${intCnt}/4`, 'px-space-xs py-space-2xs rounded bg-secondary-container/50 text-on-secondary-container font-semibold')}
              ${getSourceLink('survey', `Surv: ${survCnt}/39`, 'px-space-xs py-space-2xs rounded bg-surface-container text-on-surface-variant')}
              ${getSourceLink('reddit', `Red: ${redCnt}/45`, 'px-space-xs py-space-2xs rounded bg-surface-container text-on-surface-variant')}
              <span class="px-space-xs py-space-2xs rounded bg-surface-container text-on-surface-variant">PS: ${psCnt}/296</span>
            </div>
          </div>
        </td>

        <td class="py-space-md px-space-md">
          ${elastHtml}
        </td>

        <td class="py-space-md px-space-md text-right">
          ${ownerBadge}
        </td>

        <td class="py-space-md px-space-md text-right">
          <span class="material-symbols-outlined text-[20px] text-primary group-hover:translate-y-0.5 transition-transform">
            expand_circle_down
          </span>
        </td>
      </tr>

      <!-- Expandable Detail Drawer -->
      <tr class="hidden bg-surface-container/30" id="detail-row-${opp.rank}">
        <td class="p-space-md" colspan="6">
          <div class="flex flex-col gap-space-sm p-space-md rounded-xl bg-surface-container-low border border-outline-variant/30">
            <div class="flex items-center justify-between font-label-sm text-label-sm border-b border-outline-variant/20 pb-space-2xs">
              <span class="text-primary font-bold uppercase">Corpus Evidence Extracts (Showing ${opp.evidence_samples.length} of ${opp.evidence_count})</span>
              <span class="text-on-surface-variant">Blocker: ${opp.blocker_type}</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-space-sm">
              ${evidenceHtml}
            </div>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

window.toggleLedgerDetail = function(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.toggle('hidden');
  }
};

/**
 * MVP SANDBOX TABS
 */
function initSandbox() {
  window.switchSandboxTab = function(tabKey) {
    const panels = ['price', 'restock', 'compare', 'proof'];
    panels.forEach(k => {
      const panel = document.getElementById('sandbox-panel-' + k);
      const btn = document.getElementById('tab-btn-' + k);
      if (panel && btn) {
        if (k === tabKey) {
          panel.classList.remove('hidden');
          panel.classList.add('flex');
          btn.className = "px-space-md py-space-xs rounded-lg font-label-sm text-label-sm font-semibold bg-primary text-on-primary transition-all";
        } else {
          panel.classList.add('hidden');
          panel.classList.remove('flex');
          btn.className = "px-space-md py-space-xs rounded-lg font-label-sm text-label-sm font-semibold text-on-surface-variant hover:text-on-surface transition-all";
        }
      }
    });
  };
}

/**
 * QUALITATIVE ARCHETYPES (STITCH CARDS)
 */
function renderDeepDives() {
  const container = document.getElementById('deepdives-grid-container');
  if (!container) return;

  const archetypes = [
    {
      num: "Archetype 01",
      source: "interview",
      domain: "Financial Staging",
      name: "The 'Luxury Budget Queue'",
      quote: "I keep wishlist items as a wish list for month-end salary day. If it’s still there on the 31st, I reward myself, but usually I forget what was even in there.",
      takeaway: "Deploy automated <strong>'Payday Queue'</strong> trigger digest 48 hours prior to the 1st of every calendar month with active total-cart savings summary."
    },
    {
      num: "Archetype 02",
      source: "interview",
      domain: "Logistics Friction",
      name: "The 'Return Anxiety' Stagnation",
      quote: "Returning clothes is too much hassle in my society gate, so I just leave items in my wishlist forever unless I am 100% sure it fits exactly right.",
      takeaway: "Surface <strong>'Doorstep Instant Exchange Badge'</strong> and 1-tap courier pickup reassurance directly over the wishlist tile UI to neutralize return dread."
    },
    {
      num: "Archetype 03",
      source: "interview",
      domain: "Tangibility Void",
      name: "The 'Offline Skeptic'",
      quote: "I need to know if the color bleeds after first rinse or if the fabric wrinkles like paper after an hour of sitting down.",
      takeaway: "Implement standardized <strong>GSM &amp; Fabric Rigor Specs</strong> with customer crowdsourced post-wash rating badges on product detail bottom sheets."
    },
    {
      num: "Archetype 04",
      source: "interview",
      domain: "Aspiration Storage",
      name: "The 'Moodboard Collector'",
      quote: "Wishlist is my aesthetic moodboard, not a shopping cart. I group outfits for hypothetical holidays or weddings that haven't been planned yet.",
      takeaway: "Transform flat list into <strong>Wishlist Collections/Boards</strong> with 'Buy Look Bundle' multi-SKU checkout discounts of 10% on 3+ coordinated items."
    }
  ];

  container.innerHTML = archetypes.map(a => `
    <div class="flex flex-col justify-between p-space-lg rounded-xl bg-surface-container-lowest shadow-sm border border-outline-variant/40 hover:shadow-md transition-shadow">
      <div class="flex flex-col gap-space-sm">
        <div class="flex items-center justify-between">
          <span class="font-label-sm text-label-sm text-primary uppercase font-bold">${a.num}</span>
          <div class="flex items-center gap-space-xs">
            ${getSourceLink(a.source, 'Doc Transcript', 'px-space-xs py-space-2xs rounded bg-secondary-container/50 text-on-secondary-container font-label-sm text-label-sm font-semibold')}
            <span class="px-space-xs py-space-2xs rounded bg-surface-container font-label-sm text-label-sm text-on-surface-variant">${a.domain}</span>
          </div>
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold">${a.name}</h3>
        <blockquote class="p-space-md bg-surface-container-low rounded-xl text-on-surface font-body-md text-body-md italic border-l-2 border-primary">
          "${a.quote}"
        </blockquote>
      </div>
      <div class="mt-space-md pt-space-sm border-t border-outline-variant/20 flex flex-col gap-space-2xs">
        <div class="flex items-center gap-space-xs text-secondary font-headline-sm text-headline-sm">
          <span class="material-symbols-outlined text-[18px]">bolt</span>
          <span>PM Engineering Takeaway:</span>
        </div>
        <p class="font-body-sm text-body-sm text-on-surface font-medium">
          ${a.takeaway}
        </p>
      </div>
    </div>
  `).join('');
}

/**
 * PANEL 6: RAG RESEARCH CHAT CONSOLE
 */
function initRAGConsole(presetQA, allRecords) {
  const chipsContainer = document.getElementById('rag-preset-chips');
  const answerContainer = document.getElementById('rag-active-response');
  const inputEl = document.getElementById('rag-custom-input');
  const submitBtn = document.getElementById('rag-submit-button');

  if (!chipsContainer || !answerContainer) return;

  function displayQA(qaItem) {
    let citationsHtml = '';
    if (qaItem.sample_quotes && qaItem.sample_quotes.length > 0) {
      citationsHtml = qaItem.sample_quotes.map(sq => `
        <div class="p-space-sm rounded-lg bg-surface-container-lowest border border-outline-variant/30 flex flex-col gap-space-2xs">
          <div class="flex items-center justify-between font-label-sm text-label-sm">
            ${getSourceLink(sq.source, `[${sq.source.toUpperCase()}]`, 'px-space-xs py-space-2xs rounded bg-primary-fixed text-on-primary-fixed font-bold')}
            <span class="text-on-surface-variant">CIT: ${sq.id}</span>
          </div>
          <p class="font-body-sm text-body-sm text-on-surface italic mt-space-2xs">"${escapeHtml(sq.quote)}"</p>
        </div>
      `).join('');
    } else if (qaItem.retrieved_records && qaItem.retrieved_records.length > 0) {
      citationsHtml = qaItem.retrieved_records.slice(0, 3).map(r => `
        <div class="p-space-sm rounded-lg bg-surface-container-lowest border border-outline-variant/30 flex flex-col gap-space-2xs">
          <div class="flex items-center justify-between font-label-sm text-label-sm">
            ${getSourceLink(r.source, `[${r.source.toUpperCase()}]`, 'px-space-xs py-space-2xs rounded bg-primary-fixed text-on-primary-fixed font-bold')}
            <span class="text-on-surface-variant">ID: ${r.record_id.slice(0, 8)}</span>
          </div>
          <p class="font-body-sm text-body-sm text-on-surface italic mt-space-2xs">"${escapeHtml(r.text)}"</p>
        </div>
      `).join('');
    }

    answerContainer.innerHTML = `
      <div class="flex flex-col gap-space-sm">
        <div class="flex items-center justify-between border-b border-outline-variant/20 pb-space-sm">
          <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold">${escapeHtml(qaItem.question)}</h3>
          <span class="font-label-sm text-label-sm text-secondary bg-secondary-container/50 px-space-xs py-space-2xs rounded font-bold shrink-0">
            ZERO FREE RECALL
          </span>
        </div>
        
        <div class="font-body-md text-body-md text-on-surface leading-relaxed whitespace-pre-line">
          ${escapeHtml(qaItem.grounded_answer)}
        </div>

        ${qaItem.uncovered_aspects ? `
          <div class="p-space-sm rounded-lg bg-tertiary-fixed/30 border border-tertiary/30 text-on-surface font-body-sm text-body-sm flex items-start gap-space-xs mt-space-xs">
            <span class="material-symbols-outlined text-tertiary text-[18px] shrink-0">info</span>
            <div><strong>Epistemic Boundary Note:</strong> ${escapeHtml(qaItem.uncovered_aspects)}</div>
          </div>
        ` : ''}

        <div class="mt-space-md pt-space-sm border-t border-outline-variant/20 flex flex-col gap-space-xs">
          <span class="font-label-sm text-label-sm text-on-surface-variant uppercase font-bold">
            Ground-Truth Citations Attached (${(qaItem.sample_quotes || qaItem.retrieved_records || []).length} Records) — Click Badge to Verify Source Document ↗
          </span>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-space-sm mt-space-2xs">
            ${citationsHtml}
          </div>
        </div>
      </div>
    `;
  }

  // Render Preset Inquiries as Cards
  chipsContainer.innerHTML = presetQA.map((qa, idx) => `
    <button type="button" class="rag-preset-chip-btn text-left p-space-sm rounded-xl border border-outline-variant/40 bg-surface-container-lowest hover:bg-surface-container transition-all flex items-center justify-between gap-space-xs ${idx === 0 ? 'active' : ''}" data-qid="${qa.id}">
      <span class="font-body-sm text-body-sm text-on-surface font-medium">${escapeHtml(qa.question)}</span>
      <span class="material-symbols-outlined text-[16px] text-on-surface-variant shrink-0">chevron_right</span>
    </button>
  `).join('');

  chipsContainer.querySelectorAll('.rag-preset-chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      chipsContainer.querySelectorAll('.rag-preset-chip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const qid = btn.getAttribute('data-qid');
      const found = presetQA.find(q => q.id === qid);
      if (found) displayQA(found);
    });
  });

  // Custom Search Query
  function handleCustomQuery() {
    const q = (inputEl?.value || '').trim();
    if (!q) return;

    const presetMatch = presetQA.find(p => p.question.toLowerCase() === q.toLowerCase());
    if (presetMatch) {
      displayQA(presetMatch);
      return;
    }

    const terms = q.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    const scored = allRecords.map(r => {
      let s = 0;
      const t = r.text.toLowerCase();
      terms.forEach(term => {
        if (t.includes(term)) s += 2;
        if ((r.blocker_type || '').includes(term)) s += 4;
      });
      if (r.source === 'interview') s += 3;
      if (r.source === 'survey') s += 2;
      return { record: r, score: s };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);

    if (scored.length === 0) {
      answerContainer.innerHTML = `
        <div class="flex flex-col gap-space-sm p-space-md text-center">
          <span class="material-symbols-outlined text-tertiary text-[36px] mx-auto">search_off</span>
          <h4 class="font-headline-sm text-headline-sm text-on-surface">Uncovered in Corpus</h4>
          <p class="font-body-sm text-body-sm text-on-surface-variant">The 384-record classified dataset contains no direct qualitative evidence matching "${escapeHtml(q)}". A discovery engine states its bounds openly.</p>
        </div>
      `;
      return;
    }

    const retrieved = scored.slice(0, 4).map(x => x.record);
    displayQA({
      question: q,
      grounded_answer: `Based on ${retrieved.length} retrieved records across observed feedback channels:\n• ` +
        retrieved.map(r => `[${r.source.toUpperCase()} // ${r.record_id.slice(0, 8)}]: "${r.text.slice(0, 160)}..."`).join('\n• '),
      uncovered_aspects: "Synthesized strictly from matching records in the benchmark corpus.",
      retrieved_records: retrieved
    });
  }

  submitBtn?.addEventListener('click', handleCustomQuery);
  inputEl?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleCustomQuery();
  });

  if (presetQA.length > 0) {
    displayQA(presetQA[0]);
  }
}

/**
 * DATA LAB: SPECIMEN EXPLORER
 */
function renderEvidenceWorkbench(records) {
  const container = document.getElementById('workbench-specimens-list');
  const searchInput = document.getElementById('workbench-query');
  const sourceSelect = document.getElementById('workbench-source-select');
  const blockerSelect = document.getElementById('workbench-blocker-select');
  const counterBadge = document.getElementById('workbench-record-counter');

  if (!container) return;

  function filterAndDisplay() {
    const q = (searchInput?.value || '').toLowerCase().trim();
    const src = sourceSelect?.value || 'all';
    const blk = blockerSelect?.value || 'all';

    const matches = records.filter(r => {
      if (src !== 'all' && r.source !== src) return false;
      if (blk !== 'all' && r.blocker_type !== blk) return false;
      if (q && !r.text.toLowerCase().includes(q)) return false;
      return true;
    });

    if (counterBadge) {
      counterBadge.textContent = `${matches.length} / ${records.length} SPECIMENS`;
    }

    if (matches.length === 0) {
      container.innerHTML = `
        <div class="col-span-full p-space-xl text-center text-on-surface-variant font-body-sm text-body-sm">
          No records matched the selected query filters.
        </div>
      `;
      return;
    }

    container.innerHTML = matches.slice(0, 30).map(r => `
      <div class="p-space-md rounded-xl bg-surface-container-low border border-outline-variant/30 flex flex-col justify-between gap-space-sm hover:border-primary/50 transition-colors">
        <div class="flex flex-col gap-space-2xs">
          <div class="flex items-center justify-between font-label-sm text-label-sm">
            ${getSourceLink(r.source, `[${r.source.replace('_', ' ').toUpperCase()}]`, 'px-space-xs py-space-2xs rounded bg-surface-container font-bold text-primary')}
            <span class="text-on-surface-variant">${r.record_id.slice(0, 8)}</span>
          </div>
          <p class="font-body-sm text-body-sm text-on-surface italic mt-space-xs">"${escapeHtml(r.text)}"</p>
        </div>
        <div class="flex flex-wrap gap-1 font-label-sm text-label-sm pt-space-xs border-t border-outline-variant/20">
          <span class="px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant font-semibold">blocker: ${r.blocker_type}</span>
          <span class="px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant">motive: ${r.wishlist_motive}</span>
        </div>
      </div>
    `).join('');
  }

  searchInput?.addEventListener('input', filterAndDisplay);
  sourceSelect?.addEventListener('change', filterAndDisplay);
  blockerSelect?.addEventListener('change', filterAndDisplay);

  filterAndDisplay();
}

/**
 * DATA LAB: SOURCE ASYMMETRY (4 SOURCES)
 */
function renderSourceAsymmetry(counts) {
  const container = document.getElementById('source-asymmetry-grid');
  if (!container) return;

  const cats = counts.category_totals;

  container.innerHTML = `
    <!-- Interviews Card -->
    <div class="p-space-lg rounded-xl bg-surface-container-low border border-outline-variant/30 flex flex-col justify-between">
      <div class="flex flex-col gap-space-xs">
        <div class="flex items-center justify-between">
          <span class="font-label-sm text-label-sm text-primary font-bold uppercase">Source 01: Interviews (n=4)</span>
          ${getSourceLink('interview', 'Open Doc ↗', 'text-primary font-label-sm text-label-sm font-bold')}
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface">User In-Depth Interviews</h3>
        <p class="font-body-sm text-body-sm text-on-surface-variant">Self-reported intentional behavior. Weight: 4.0×</p>
      </div>
      <div class="flex flex-col gap-space-2xs my-space-md font-label-sm text-label-sm">
        <div class="flex justify-between text-secondary font-semibold"><span>Psychological Deliberation:</span><span>100.0%</span></div>
        <div class="flex justify-between text-on-surface-variant"><span>Structural Platform Friction:</span><span>0.0%</span></div>
      </div>
      <span class="font-label-sm text-label-sm text-on-surface-variant pt-space-xs border-t border-outline-variant/20">Top: quality_doubt, no_reviews, budget</span>
    </div>

    <!-- Survey Card -->
    <div class="p-space-lg rounded-xl bg-surface-container-low border border-outline-variant/30 flex flex-col justify-between">
      <div class="flex flex-col gap-space-xs">
        <div class="flex items-center justify-between">
          <span class="font-label-sm text-label-sm text-primary font-bold uppercase">Source 02: Survey (n=39)</span>
          ${getSourceLink('survey', 'Open Sheet ↗', 'text-primary font-label-sm text-label-sm font-bold')}
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface">Targeted Consumer Survey</h3>
        <p class="font-body-sm text-body-sm text-on-surface-variant">Pre-purchase stated elasticity. Weight: 3.0×</p>
      </div>
      <div class="flex flex-col gap-space-2xs my-space-md font-label-sm text-label-sm">
        <div class="flex justify-between text-secondary font-semibold"><span>Psychological Deliberation:</span><span>${cats.psychological.by_source.survey.percentage}%</span></div>
        <div class="flex justify-between text-on-surface-variant"><span>Structural Platform Friction:</span><span>${cats.structural.by_source.survey.percentage}%</span></div>
      </div>
      <span class="font-label-sm text-label-sm text-on-surface-variant pt-space-xs border-t border-outline-variant/20">Top: quality_doubt, price_wait, paralysis</span>
    </div>

    <!-- Play Store Card -->
    <div class="p-space-lg rounded-xl bg-surface-container-low border border-outline-variant/30 flex flex-col justify-between">
      <div class="flex flex-col gap-space-xs">
        <div class="flex items-center justify-between">
          <span class="font-label-sm text-label-sm text-primary font-bold uppercase">Source 03: Play Store (n=296)</span>
          ${getSourceLink('reddit', 'Open Reddit Doc ↗', 'text-on-surface-variant font-label-sm text-label-sm')}
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface">Google Play Reviews</h3>
        <p class="font-body-sm text-body-sm text-on-surface-variant">Organic complaint stream. Weight: 1.0×</p>
      </div>
      <div class="flex flex-col gap-space-2xs my-space-md font-label-sm text-label-sm">
        <div class="flex justify-between text-primary font-semibold"><span>Structural Platform Friction:</span><span>${cats.structural.by_source.play_store.percentage}%</span></div>
        <div class="flex justify-between text-on-surface-variant"><span>Psychological Deliberation:</span><span>${cats.psychological.by_source.play_store.percentage}%</span></div>
      </div>
      <span class="font-label-sm text-label-sm text-on-surface-variant pt-space-xs border-t border-outline-variant/20">Top: serviceability (126), out_of_stock (48)</span>
    </div>
  `;
}

/**
 * DATA LAB: CO-OCCURRENCE ENGINE
 */
function renderCoOccurrenceEngine(coOccurrences) {
  const container = document.getElementById('cooccurrence-engine-grid');
  if (!container) return;

  const buildCard = (title, pairData, k1, k2) => {
    const validPairs = pairData.pairs.filter(p => p[k1] !== 'none' && p[k2] !== 'none').slice(0, 4);
    const rows = validPairs.map(p => `
      <div class="flex items-center justify-between py-1 border-b border-outline-variant/20 font-label-sm text-label-sm">
        <div class="flex items-center gap-1">
          <span class="px-1.5 py-0.5 rounded bg-surface-container text-on-surface font-semibold">${p[k1]}</span>
          <span class="text-on-surface-variant">×</span>
          <span class="px-1.5 py-0.5 rounded bg-surface-container text-on-surface font-semibold">${p[k2]}</span>
        </div>
        <span class="font-bold text-primary">${p.overall.count} / ${p.overall.denominator} (${p.overall.percentage}%)</span>
      </div>
    `).join('');

    return `
      <div class="p-space-md rounded-xl bg-surface-container-low border border-outline-variant/30 flex flex-col gap-space-xs">
        <h4 class="font-headline-sm text-headline-sm text-on-surface">${title}</h4>
        <div class="mt-space-2xs flex flex-col">${rows}</div>
      </div>
    `;
  };

  container.innerHTML = `
    ${buildCard("Blocker Type × Journey Stage", coOccurrences.blocker_type__x__journey_stage, "blocker_type", "journey_stage")}
    ${buildCard("Blocker Type × External Action", coOccurrences.blocker_type__x__external_action, "blocker_type", "external_action")}
    ${buildCard("Blocker Type × Category", coOccurrences.blocker_type__x__blocker_category, "blocker_type", "blocker_category")}
    ${buildCard("Wishlist Motive × Blocker", coOccurrences.wishlist_motive__x__blocker_type, "wishlist_motive", "blocker_type")}
  `;
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, '&amp;')
             .replace(/</g, '&lt;')
             .replace(/>/g, '&gt;')
             .replace(/"/g, '&quot;')
             .replace(/'/g, '&#039;');
}
