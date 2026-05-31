/* ===================== LEAFSENSE MAIN.JS v2.0 ===================== */

const API_URL = "http://127.0.0.1:5000";

// ── Tab switcher (login page) ──
function switchTab(tab, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.auth-form').forEach(f => { f.classList.remove('active'); f.style.display='none'; });
  btn.classList.add('active');
  const form = document.getElementById(tab + 'Form');
  form.classList.add('active');
  form.style.display = 'block';
}

// ── Particles ──
function createParticles() {
  const c = document.getElementById('particles');
  if (!c) return;
  for (let i = 0; i < 18; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const s = Math.random() * 6 + 2;
    p.style.cssText = `left:${Math.random()*50}%;width:${s}px;height:${s}px;animation-duration:${Math.random()*15+10}s;animation-delay:${Math.random()*10}s;opacity:${Math.random()*0.4+0.1};`;
    if (Math.random() > 0.6) { p.style.borderRadius='50% 0 50% 0'; p.style.width=(s*2)+'px'; }
    c.appendChild(p);
  }
}

// ── File upload ──
let uploadedFile = null;

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) { uploadedFile = file; showPreview(file); }
}

function handleDrop(e) {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) { uploadedFile = file; showPreview(file); }
}

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const preview = document.getElementById('previewSection');
    const img     = document.getElementById('previewImg');
    if (preview && img) {
      img.src = e.target.result;
      preview.style.display = 'block';

      // Show filename
      const fnEl = document.getElementById('uploadFileName');
      if (fnEl) { fnEl.textContent = '📎 ' + file.name; fnEl.style.display = 'block'; }

      // Reset result and button
      const r = document.getElementById('scanResult');
      if (r) { r.style.display='none'; r.innerHTML=''; }
      const btn = document.getElementById('analyzeBtn');
      if (btn) { btn.textContent='🔬 ANALYZE SPECIMEN'; btn.disabled=false; btn.removeAttribute('style'); }
      const loading = document.getElementById('loadingSection');
      if (loading) loading.style.display = 'none';

      // Animate bar
      const bar = document.getElementById('uploadBarFill');
      if (bar) {
        bar.style.width = '0%';
        let w = 0;
        const iv = setInterval(() => { w += 5; bar.style.width = w+'%'; if(w>=100) clearInterval(iv); }, 20);
      }
    }
  };
  reader.readAsDataURL(file);
}

// ── Loading Animation ──
function showLoadingAnimation() {
  const loading = document.getElementById('loadingSection');
  if (!loading) return;
  loading.style.display = 'block';

  const steps = ['step1','step2','step3','step4'];
  steps.forEach(s => {
    const el = document.getElementById(s);
    if (el) { el.classList.remove('active','done'); }
  });

  let current = 0;
  const iv = setInterval(() => {
    if (current > 0) {
      const prev = document.getElementById(steps[current-1]);
      if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
    }
    if (current < steps.length) {
      const cur = document.getElementById(steps[current]);
      if (cur) cur.classList.add('active');
      current++;
    } else {
      clearInterval(iv);
    }
  }, 700);
}

function hideLoadingAnimation() {
  const loading = document.getElementById('loadingSection');
  if (loading) loading.style.display = 'none';
}

// ── Save to History ──
function saveToHistory(diagnosis, mode) {
  try {
    const history = JSON.parse(localStorage.getItem('leafsense_history') || '[]');
    history.push({
      disease    : diagnosis.disease,
      crop       : diagnosis.crop,
      confidence : diagnosis.confidence,
      severity   : diagnosis.severity,
      description: diagnosis.description,
      treatment  : diagnosis.treatment,
      prevention : diagnosis.prevention,
      mode       : mode,
      timestamp  : new Date().toISOString()
    });
    // Keep only last 50 scans
    if (history.length > 50) history.shift();
    localStorage.setItem('leafsense_history', JSON.stringify(history));
  } catch(e) {
    console.log('History save error:', e);
  }
}

// ── MAIN AI DETECTION ──
async function simulateScan() {
  if (!uploadedFile) { alert('Please upload a plant image first.'); return; }

  const btn       = document.getElementById('analyzeBtn');
  const resultEl  = document.getElementById('scanResult');

  btn.textContent = '⏳ Analyzing...';
  btn.disabled    = true;
  resultEl.style.display = 'none';

  showLoadingAnimation();

  try {
    const formData = new FormData();
    formData.append('image', uploadedFile);

    const response = await fetch(`${API_URL}/api/detect`, {
      method: 'POST', body: formData
    });

    hideLoadingAnimation();

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Server error');
    }

    const data = await response.json();
    saveToHistory(data.diagnosis, data.mode);
    renderResult(data, resultEl, btn);

  } catch (error) {
    hideLoadingAnimation();
    if (error.message.toLowerCase().includes('fetch') ||
        error.message.toLowerCase().includes('failed')) {
      resultEl.style.display = 'block';
      resultEl.innerHTML = `
        <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:24px">
          <h4 style="color:#f87171;margin-bottom:8px">⚠️ Python Backend Not Running</h4>
          <p style="color:var(--text-muted);font-size:0.88rem;line-height:1.6;margin-bottom:16px">Start the backend in VS Code terminal:</p>
          <div style="background:var(--bg);border-radius:8px;padding:16px;font-family:monospace;font-size:0.82rem;color:var(--accent)">
            cd "Leaf sense"<br>
            python app.py
          </div>
          <p style="color:var(--text-muted);font-size:0.82rem;margin-top:12px">Then upload your image again.</p>
        </div>`;
      btn.textContent = '⚠️ Backend Offline';
    } else {
      resultEl.style.display = 'block';
      resultEl.innerHTML = `<p style="color:#ef4444">❌ ${error.message}</p>`;
      btn.textContent = 'Try Again'; btn.disabled = false;
    }
  }
}

function renderResult(data, resultEl, btn) {
  const d = data.diagnosis;
  const sevColors = { 'None':'#a8d832','Mild':'#fbbf24','Moderate':'#f97316','Severe':'#ef4444','Unknown':'#94a3b8' };
  const sevColor  = sevColors[d.severity] || '#94a3b8';
  const treats    = (d.treatment||[]).map(t => `<li style="padding:4px 0;color:var(--text-muted);font-size:0.87rem">→ ${t}</li>`).join('');
  const alts      = (data.alternatives||[]).map(a =>
    `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border-soft)">
      <span style="color:var(--text-muted);font-size:0.83rem">${a.disease}</span>
      <span style="color:var(--text-muted);font-size:0.83rem">${a.confidence}%</span>
    </div>`).join('');

  const modeLabel = data.mode === 'groq_vision' ? '🚀 Groq AI'
                  : data.mode === 'gemini_vision' ? '🤖 Gemini AI'
                  : '🧠 Local Model';

  resultEl.style.display = 'block';
  resultEl.innerHTML = `
    <div style="animation:fadeUp 0.4s ease">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div>
          <div style="font-size:0.68rem;letter-spacing:0.12em;color:var(--text-muted);margin-bottom:4px">
            DIAGNOSIS COMPLETE · ${modeLabel}
          </div>
          <h3 style="font-family:'Playfair Display',serif;font-size:1.3rem">${d.disease}</h3>
          <div style="font-size:0.72rem;color:var(--text-muted);margin-top:2px">
            Crop: ${d.crop || 'Unknown'} · Report: ${data.report_id}
          </div>
        </div>
        <div style="text-align:right">
          <div style="background:rgba(168,216,50,0.1);color:var(--accent);border:1px solid var(--accent);border-radius:8px;padding:6px 14px;font-size:1.1rem;font-weight:700">${d.confidence}%</div>
          <div style="font-size:0.68rem;color:var(--text-muted);margin-top:4px">CONFIDENCE</div>
        </div>
      </div>

      <div style="background:${d.severity==='None'?'rgba(168,216,50,0.08)':'rgba(239,68,68,0.08)'};border:1px solid ${sevColor}44;border-radius:8px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:10px">
        <span style="color:${sevColor};font-size:1.2rem">●</span>
        <div>
          <div style="font-size:0.68rem;letter-spacing:0.1em;color:var(--text-muted)">SEVERITY</div>
          <div style="color:${sevColor};font-weight:600">${d.severity}</div>
        </div>
      </div>

      <p style="color:var(--text);font-size:0.9rem;line-height:1.6;margin-bottom:16px">${d.description}</p>

      <div style="background:var(--bg);border:1px solid var(--border-soft);border-radius:8px;padding:16px;margin-bottom:14px">
        <div style="font-size:0.68rem;letter-spacing:0.1em;color:var(--text-muted);margin-bottom:10px">🧪 TREATMENT PROTOCOL</div>
        <ul style="list-style:none;padding:0">${treats}</ul>
      </div>

      <div style="background:rgba(168,216,50,0.04);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:14px">
        <div style="font-size:0.68rem;letter-spacing:0.1em;color:var(--text-muted);margin-bottom:6px">🛡️ PREVENTION</div>
        <p style="color:var(--text-muted);font-size:0.87rem;line-height:1.5">${d.prevention}</p>
      </div>

      ${alts ? `<div style="margin-bottom:14px"><div style="font-size:0.68rem;letter-spacing:0.1em;color:var(--text-muted);margin-bottom:8px">OTHER POSSIBILITIES</div>${alts}</div>` : ''}

      <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap">
        <button onclick="downloadReport()" style="flex:1;min-width:120px;padding:12px;background:none;border:1px solid var(--border-soft);border-radius:8px;color:var(--text-muted);cursor:pointer;font-size:0.83rem;transition:all 0.2s" onmouseover="this.style.color='var(--accent)';this.style.borderColor='var(--accent)'" onmouseout="this.style.color='var(--text-muted)';this.style.borderColor='var(--border-soft)'">
          📄 Download Report
        </button>
        <button onclick="window.location.href='dashboard.html'" style="flex:1;min-width:120px;padding:12px;background:none;border:1px solid var(--border-soft);border-radius:8px;color:var(--text-muted);cursor:pointer;font-size:0.83rem;transition:all 0.2s" onmouseover="this.style.color='var(--accent)';this.style.borderColor='var(--accent)'" onmouseout="this.style.color='var(--text-muted)';this.style.borderColor='var(--border-soft)'">
          📊 View History
        </button>
        <button onclick="document.getElementById('fileInput').click()" style="flex:1;min-width:120px;padding:12px;background:var(--accent);border:none;border-radius:8px;color:#0f2318;cursor:pointer;font-weight:600;font-size:0.83rem">
          🔄 New Scan
        </button>
      </div>
    </div>`;

  btn.textContent = '✅ Analysis Complete';
  btn.style.cssText = 'background:rgba(168,216,50,0.1);color:var(--accent);border:1px solid var(--accent);';
  window._lastDiagnosis = d;
}

function downloadReport() {
  const d = window._lastDiagnosis || {};
  const content = `
╔════════════════════════════════════════════╗
║     LEAFSENSE BOTANICAL INTELLIGENCE       ║
║          PLANT DISEASE REPORT              ║
╚════════════════════════════════════════════╝
Generated   : ${new Date().toLocaleString()}
─────────────────────────────────────────────
Disease     : ${d.disease || 'N/A'}
Crop        : ${d.crop || 'N/A'}
Confidence  : ${d.confidence || 'N/A'}%
Severity    : ${d.severity || 'N/A'}

Description : ${d.description || 'N/A'}

TREATMENT:
${(d.treatment||[]).map((t,i)=>`${i+1}. ${t}`).join('\n')}

PREVENTION: ${d.prevention || 'N/A'}
─────────────────────────────────────────────
© 2024 LeafSense Botanical Intelligence
`.trim();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], {type:'text/plain'}));
  a.download = `leafsense-${Date.now()}.txt`;
  a.click();
}

// ── Plant filter (recommendations) ──
function filterPlants(cat, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.plant-card').forEach(card => {
    card.style.display = (cat==='all' || card.dataset.cat===cat) ? 'block' : 'none';
  });
}

// ── AI Chat ──
async function askAI() {
  const input     = document.getElementById('aiInput');
  const responseEl = document.getElementById('aiResponse');
  if (!input || !responseEl || !input.value.trim()) return;
  const query = input.value.trim();
  responseEl.style.display = 'block';
  responseEl.innerHTML = '<span style="color:var(--text-muted)">🌿 Thinking...</span>';

  const q = query.toLowerCase();
  const answers = [
    {keys:['tomato','blight'],      ans:'Tomatoes get Early Blight (bullseye spots) and Late Blight (dark patches). Use chlorothalonil for early, copper fungicide for late — immediately.'},
    {keys:['water','irrigat'],      ans:'Deep watering 2–3× per week beats daily shallow watering. Always water at the base to prevent fungal diseases.'},
    {keys:['fertiliz','nitrogen'],  ans:'Use NPK 10-10-10 for most plants. Leafy greens need more N; fruiting crops need more P and K during fruiting.'},
    {keys:['wheat','rust','grain'], ans:'Wheat rust: apply triazole fungicide at flag-leaf stage. Monitor during cool humid weather. Rotate crops every 2–3 years.'},
    {keys:['pest','aphid','mite'],  ans:'For aphids/mites: blast with water jet, then apply neem oil (2 tbsp/gallon) weekly. For heavy infestations use insecticidal soap.'},
    {keys:['potato'],               ans:'Potato late blight is the most dangerous — apply metalaxyl at first sign, hill soil around plants, consider early harvest if severe.'},
  ];

  let answer = `For "${query}": Ensure proper drainage, sunlight, and balanced nutrition. Upload a plant photo on the Home page for a precise AI diagnosis.`;
  for (const item of answers) {
    if (item.keys.some(k => q.includes(k))) { answer = item.ans; break; }
  }

  setTimeout(() => {
    responseEl.innerHTML = `
      <div style="font-size:0.68rem;letter-spacing:0.1em;color:var(--accent);margin-bottom:8px">🌿 LEAFSENSE AI</div>
      <p style="color:var(--text);font-size:0.9rem;line-height:1.6">${answer}</p>`;
    input.value = '';
  }, 500);
}

// ── API health check ──
async function checkAPIStatus() {
  const badge = document.querySelector('.server-badge');
  if (!badge) return;
  try {
    const res = await fetch(`${API_URL}/api/health`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      badge.innerHTML = '<span class="status-dot"></span> AI BACKEND: ONLINE';
      badge.style.borderColor = 'rgba(168,216,50,0.3)';
    }
  } catch {
    badge.innerHTML = '<span style="width:8px;height:8px;border-radius:50%;background:#ef4444;display:inline-block;box-shadow:0 0 8px #ef4444"></span> AI BACKEND: OFFLINE';
  }
}

// ── Init ──
document.addEventListener('DOMContentLoaded', function() {
  // AI chat enter key
  const aiInput = document.getElementById('aiInput');
  if (aiInput) aiInput.addEventListener('keypress', e => { if(e.key==='Enter') askAI(); });

  // Scroll reveal
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.service-card,.step-card,.team-card,.plant-card,.timeline-content,.science-item,.history-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  createParticles();

  // Navbar scroll
  const navbar = document.querySelector('.navbar');
  if (navbar) window.addEventListener('scroll', () => {
    navbar.style.background = window.scrollY > 50
      ? 'rgba(8,18,12,0.98)' : 'rgba(15,35,24,0.92)';
  });

  // Theme
  if (localStorage.getItem('leafsense_theme') === 'light') {
    document.body.classList.add('light-mode');
    const btn = document.getElementById('themeBtn');
    if (btn) btn.textContent = '☀️';
  }

  checkAPIStatus();
});