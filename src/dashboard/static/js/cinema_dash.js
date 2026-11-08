/**
 * DarkFactory Cinema Studio — Master Frontend Orchestrator SPA
 */

let activeVideoData = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSSE();
  refreshAllData();

  window.cinemaVideo.init("main-cinema-video", "video-letterbox-bars", "video-subtitle-banner");

  // Periodic telemetry refresh
  setInterval(refreshTelemetry, 5000);
});

// ── Tab Navigation ────────────────────────────────────
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-content").forEach(c => {
    c.classList.toggle("active", c.id === `tab-${tabId}`);
  });
}

// ── Real-Time SSE Log Streaming ───────────────────────
function initSSE() {
  const terminal = document.getElementById("terminal-output");
  if (!terminal) return;

  const eventSource = new EventSource("/api/stream-logs");

  eventSource.onmessage = (event) => {
    const line = document.createElement("div");
    line.className = "terminal-line";
    const text = event.data;

    if (text.includes("[ERROR]") || text.includes("[CRITICAL]")) {
      line.classList.add("error");
    } else if (text.includes("[WARN]")) {
      line.classList.add("warn");
    } else if (text.includes("[SUCCESS]")) {
      line.classList.add("success");
    } else if (text.includes("[SYSTEM]") || text.includes("[ACTION]")) {
      line.classList.add("system");
    }

    line.innerText = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
  };

  eventSource.onerror = () => {
    console.warn("SSE connection interrupted. Reconnecting...");
  };
}

// ── Data Refreshers ───────────────────────────────────
async function refreshAllData() {
  await Promise.all([
    refreshTelemetry(),
    loadScreenplays(),
    loadVisualQueues(),
    loadAudioLibrary(),
    loadApprovalQueue(),
    loadQuarantineReports(),
  ]);
}

async function refreshTelemetry() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const k = data.kpis;

    setText("kpi-productions", k.total_productions || 0);
    setText("kpi-completed", k.completed_episodes || 0);
    setText("kpi-pending", k.pending_approvals || 0);
    setText("kpi-greendollar", `${k.green_dollar_rate}%`);
    setText("kpi-quarantine", k.quarantined_count || 0);
    setText("kpi-scripts", k.scripts_count || 0);

    // Daemon pill
    const pill = document.getElementById("daemon-status-pill");
    const led = document.getElementById("daemon-led");
    const label = document.getElementById("daemon-status-label");
    if (pill && led && label) {
      if (k.daemon_status === "producing") {
        led.className = "pulse-led pulse-led-producing";
        label.innerText = "PRODUZINDO EPISÓDIO";
      } else if (k.daemon_status === "idle") {
        led.className = "pulse-led pulse-led-ok";
        label.innerText = "DAEMON 24/7 ONLINE";
      } else {
        led.className = "pulse-led";
        label.innerText = "SUPERVISOR OFFLINE";
      }
    }

    // Google Flow Quota bar
    const quota = k.google_flow_quota;
    if (quota) {
      setText("flow-omni-usage", `${quota.omni_used}/${quota.omni_limit}`);
      setText("flow-veo-usage", `${quota.veo_used}/${quota.veo_limit}`);
    }
  } catch (e) {
    console.warn("Error refreshing telemetry:", e);
  }
}

async function loadScreenplays() {
  try {
    const res = await fetch("/api/screenplays");
    const screenplays = await res.json();
    const container = document.getElementById("screenplays-list");
    if (!container) return;

    if (screenplays.length === 0) {
      container.innerHTML = `<div style="color:var(--label-secondary); padding:20px; text-align:center;">Nenhum roteiro sintetizado ainda. Digite um tema acima para produzir.</div>`;
      return;
    }

    const first = screenplays[0];
    setText("current-script-title", first.title);
    setText("current-script-logline", first.logline);

    // Populate timelines if available
    const tls = first.timelines || {};
    setText("thread-a-desc", tls.slow_clock || "O Relógio Lento: Gênese silenciosa, decisões secretas e falhas de engenharia ocorridas antes do colapso.");
    setText("thread-b-desc", tls.fast_clock || "O Relógio Rápido: Os 20 minutos ou 60 segundos de colapso iminente em tempo real.");
    setText("thread-c-desc", tls.aftermath || "O Pós-Impacto: Depoimentos desclassificados, testemunhos e as cicatrizes históricas.");

    // Populate alternative titles
    const titlesEl = document.getElementById("alt-titles-list");
    if (titlesEl && first.alternative_titles) {
      titlesEl.innerHTML = first.alternative_titles.map(t => `<li style="margin-bottom:6px; color:#FFE066;">${t}</li>`).join("");
    }
  } catch (e) {
    console.warn("Error loading screenplays:", e);
  }
}

async function loadVisualQueues() {
  try {
    const res = await fetch("/api/visual-queues");
    const data = await res.json();

    const veoTable = document.getElementById("veo-queue-tbody");
    if (veoTable && data.veo3_4k) {
      const items = data.veo3_4k.items || [];
      setText("veo-queue-count", `${items.length} Prompts 4K`);
      veoTable.innerHTML = items.map((item, idx) => `
        <tr>
          <td class="mono">#${idx + 1}</td>
          <td><strong style="color:var(--cinema-gold);">${item.scene_id || 'Scene'}</strong></td>
          <td>${item.prompt || item.camera_prompt || 'Cinematic 4K shot on 35mm IMAX'}</td>
          <td><span class="pill" style="border-color:#30D158; color:#30D158;">2.39:1 UHD</span></td>
        </tr>
      `).join("") || `<tr><td colspan="4" style="text-align:center; padding:16px;">Fila vazia</td></tr>`;
    }

    const omniTable = document.getElementById("omni-queue-tbody");
    if (omniTable && data.omni_flash) {
      const items = data.omni_flash.items || [];
      setText("omni-queue-count", `${items.length} Tomadas`);
      omniTable.innerHTML = items.map((item, idx) => `
        <tr>
          <td class="mono">#${idx + 1}</td>
          <td>${item.continuity_id || 'Clip'}</td>
          <td>${item.description || item.prompt || 'Continuity sequence'}</td>
          <td><span class="pill" style="border-color:#00D2FF; color:#00D2FF;">Omni 15s</span></td>
        </tr>
      `).join("") || `<tr><td colspan="4" style="text-align:center; padding:16px;">Fila vazia</td></tr>`;
    }
  } catch (e) {
    console.warn("Error loading visual queues:", e);
  }
}

async function loadAudioLibrary() {
  try {
    const res = await fetch("/api/audio-library");
    const stems = await res.json();
    window.soundLab.loadStems(stems);

    setText("voice-stem-label", stems.voice[0]?.name || "Voz (CosyVoice/Kokoro)");
    setText("ost-stem-label", stems.ost[0]?.name || "Trilha Lyria (Procedural)");
    setText("foley-stem-label", stems.foley[0]?.name || "Foley (MMAudio/Whoosh)");
    setText("master-stem-label", stems.master[0]?.name || "Master EBU R128 (-14 LUFS)");
  } catch (e) {
    console.warn("Error loading audio stems:", e);
  }
}

async function loadApprovalQueue() {
  try {
    const res = await fetch("/api/approval-queue");
    const items = await res.json();

    if (items.length === 0) {
      setText("approval-empty-notice", "Nenhum documentário aguardando aprovação no momento.");
      return;
    }

    activeVideoData = items[0];
    const vid = activeVideoData;

    // Setup Video
    const videoEl = document.getElementById("main-cinema-video");
    if (videoEl && vid.url) {
      videoEl.src = vid.url;
    }

    // Subtitles
    const subSelect = document.getElementById("subtitles-selector");
    if (subSelect && vid.subtitles) {
      subSelect.innerHTML = `<option value="">Sem legendas</option>` +
        vid.subtitles.map(s => `<option value="${s.url}">${s.lang.toUpperCase()} Subtitles</option>`).join("");
    }

    // SEO Package
    const seo = vid.seo_package || {};
    setText("seo-video-title", seo.title || vid.filename);
    setText("seo-video-desc", seo.description || "Historical documentary thriller synthesized by DarkFactory.");
    setText("seo-video-tags", (seo.tags || ["dark documentary", "history", "cold war", "imax"]).join(", "));

    // Thumbnails A/B/C
    const thumbsContainer = document.getElementById("thumbnails-grid-container");
    if (thumbsContainer && vid.thumbnails) {
      thumbsContainer.innerHTML = vid.thumbnails.map((t, idx) => `
        <div class="thumbnail-candidate ${idx === 0 ? 'selected' : ''}" data-variant="${t.variant}" onclick="cinemaVideo.selectThumbnail('${t.variant}')">
          <span class="thumb-tag">VARIANTE ${t.variant}</span>
          <img src="${t.url}" alt="${t.label}" onerror="this.src='/static/favicon.svg'">
          <div style="padding:8px; font-size:11px; color:#ddd; background:rgba(10,14,22,0.9);">
            <strong>${t.label}</strong>
            <p style="font-size:10px; color:#aaa; margin-top:3px;">${t.hypothesis}</p>
          </div>
        </div>
      `).join("");
    }

    // Green Dollar Pre-Rate
    const gd = vid.green_dollar;
    if (gd) {
      setText("gd-status", gd.status);
      setText("gd-score", `${gd.score}% GREEN DOLLAR`);
      setText("gd-suitability", gd.ad_suitability);
    }
  } catch (e) {
    console.warn("Error loading approval queue:", e);
  }
}

async function loadQuarantineReports() {
  try {
    const res = await fetch("/api/quarantine");
    const reports = await res.json();
    const container = document.getElementById("quarantine-tbody");
    if (!container) return;

    if (reports.length === 0) {
      container.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:16px; color:#30D158;">Zero vídeos em quarentena. Esteira 100% em conformidade.</td></tr>`;
      return;
    }

    container.innerHTML = reports.map(r => `
      <tr>
        <td class="mono">${r.dir_name}</td>
        <td style="color:#FF453A;">${r.data?.reason || 'Reprovado por inspeção'}</td>
        <td class="mono">${r.quarantined_at.split('T')[0]}</td>
      </tr>
    `).join("");
  } catch (e) {
    console.warn("Error loading quarantine:", e);
  }
}

// ── Interactive Actions ───────────────────────────────
async function triggerNewTopic() {
  const input = document.getElementById("input-topic");
  const topic = input?.value.trim();
  if (!topic) {
    alert("Digite um tema ou incidente histórico.");
    return;
  }

  showToast(`Iniciando produção autônoma para: "${topic}"...`);
  try {
    const res = await fetch("/api/trigger-topic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, dry_run: false })
    });
    const result = await res.json();
    if (result.status === "started") {
      switchTab("terminal");
    } else {
      alert(result.message || "Falha ao iniciar produção.");
    }
  } catch (e) {
    alert(`Erro ao conectar com API: ${e}`);
  }
}

async function triggerPhase(phaseNum) {
  showToast(`Disparando Fase ${phaseNum}...`);
  try {
    const res = await fetch("/api/run-phase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phase: phaseNum })
    });
    const result = await res.json();
    if (result.status === "started") {
      switchTab("terminal");
    }
  } catch (e) {
    alert(`Erro ao rodar fase: ${e}`);
  }
}

async function daemonAction(action) {
  showToast(`Enviando comando '${action}' ao Daemon 24/7...`);
  try {
    const res = await fetch("/api/daemon-control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    const result = await res.json();
    showToast(result.message);
    refreshTelemetry();
  } catch (e) {
    alert(`Erro ao controlar daemon: ${e}`);
  }
}

// ── 1-Click Approval Decision Actions ─────────────────
async function submitApproval(action) {
  if (!activeVideoData) {
    alert("Nenhum vídeo carregado na fila.");
    return;
  }

  let notes = null;
  if (action === "reject_quarantine") {
    notes = prompt("Motivo da rejeição para quarentena (ex: áudio recortado, artefatos no Veo):");
    if (!notes) return;
  }

  try {
    const res = await fetch("/api/approval-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video_id: activeVideoData.video_id,
        action: action,
        quarantine_notes: notes,
        selected_thumbnail: window.cinemaVideo.selectedThumbnailVariant
      })
    });
    const result = await res.json();
    showToast(`Decisão registrada: ${result.action || result.status}`);
    loadApprovalQueue();
    refreshTelemetry();
  } catch (e) {
    alert(`Erro na ação de aprovação: ${e}`);
  }
}

function downloadFullPackage() {
  if (!activeVideoData) {
    alert("Nenhum vídeo disponível para empacotar.");
    return;
  }
  window.open(`/api/download-package/${activeVideoData.video_id}`, "_blank");
}

// ── Sound Lab Mixer Controls ──────────────────────────
function toggleSoundLabPlayback() {
  const isPlaying = window.soundLab.togglePlayAll();
  const btn = document.getElementById("btn-soundlab-play");
  if (btn) {
    btn.innerHTML = isPlaying
      ? `<svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor"><rect x="3" y="2" width="3.5" height="12"/><rect x="9.5" y="2" width="3.5" height="12"/></svg> Pausar Mixer`
      : `<svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor"><polygon points="3,2 14,8 3,14"/></svg> Tocar 4 Stems Simultâneos`;
  }
}

function handleFaderChange(channel, sliderEl) {
  const val = parseFloat(sliderEl.value) / 100;
  window.soundLab.setVolume(channel, val);
}

function handleMute(channel, btn) {
  const isMuted = window.soundLab.toggleMute(channel);
  btn.classList.toggle("active", isMuted);
}

function handleSolo(channel, btn) {
  const isSolo = window.soundLab.toggleSolo(channel);
  btn.classList.toggle("active", isSolo);
}

// ── Video Subtitles Selection ─────────────────────────
function onSubtitleChange(selectEl) {
  const url = selectEl.value;
  if (url) {
    window.cinemaVideo.loadSubtitles(url);
  } else {
    window.cinemaVideo.currentSubtitles = [];
  }
}

// ── Helpers ───────────────────────────────────────────
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

function showToast(msg) {
  const banner = document.getElementById("global-toast");
  if (!banner) return;
  banner.innerText = msg;
  banner.style.display = "block";
  setTimeout(() => { banner.style.display = "none"; }, 4000);
}
