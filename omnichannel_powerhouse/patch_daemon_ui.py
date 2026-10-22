import os
import re

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add 24/7 Autonomous Empire Command Bar inside tab-unlisted
banner_target = """        <!-- Video Cards Grid -->
        <div id="unlistedVideosGrid" class="grid grid-cols-1 lg:grid-cols-2 gap-4">"""

banner_html = """        <!-- 24/7 Autonomous Empire Engine Command Bar -->
        <div class="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-cyan-500/40 shadow-xl space-y-3">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span id="daemonStatusBadge" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                  ⚪ 24/7 AUTONOMOUS ENGINE: IDLE
                </span>
                <span id="daemonCyclesCount" class="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-950/60 text-cyan-300 border border-cyan-800/50">
                  0 Videos Published
                </span>
              </div>
              <div class="text-xs text-slate-300 font-semibold flex items-center gap-1.5">
                <span>⚡ Live Telemetry:</span>
                <span id="daemonStepText" class="text-cyan-300 font-mono">Daemon ready. Click Start to enable 24/7 autonomous production.</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button id="btnToggleDaemon" onclick="togglePerpetualDaemon()" data-running="false" class="py-2.5 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs transition shadow-md shadow-emerald-600/30 flex items-center gap-1.5">
                <span>🚀</span> Start 24/7 Autonomous Engine
              </button>
            </div>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center gap-4 flex-wrap">
            <span>🧠 <strong>Auto-Pipeline:</strong> Niche Select ➔ Gemini Script ➔ Shure SM7B Audio ➔ Locked Outro ➔ Supreme SEO ➔ Studio Auto-Upload ➔ Auto-Pinned Comment</span>
            <span class="text-emerald-400 font-bold">✨ 0% Human Touch · 0% PC Burn</span>
          </div>
        </div>

        <!-- Video Cards Grid -->
        <div id="unlistedVideosGrid" class="grid grid-cols-1 lg:grid-cols-2 gap-4">"""

if banner_target in content:
    content = content.replace(banner_target, banner_html, 1)
    print("SUCCESS: 24/7 Empire banner added!")
else:
    print("ERROR: Banner target not found!")

# 2. Add "Auto-Upload via Playwright Bot Now" button on card
btn_target = """                <div class="grid grid-cols-2 gap-2">
                  <a href="${v.local_video_path || '/output/demo_ai_15min_hindi_100pct_locked_master.mp4'}" download class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>📥</span> Download Master MP4
                  </a>
                  <a href="https://studio.youtube.com/channel/videos/upload?d=ud" target="_blank" class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-cyan-300 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>🚀</span> Direct Studio Upload Pop-up ↗
                  </a>
                </div>"""

btn_replacement = """                <!-- Bot Auto-Upload Action -->
                <button onclick="autoUploadVideoNow('${v.id}', this)" class="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-blue-500 text-white font-extrabold text-xs transition flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/20 border border-cyan-400/40">
                  <span>🤖</span> Auto-Upload via Playwright Bot Now (${isYoutube ? 'YouTube Studio' : 'Rumble'})
                </button>

                <div class="grid grid-cols-2 gap-2">
                  <a href="${v.local_video_path || '/output/demo_ai_15min_hindi_100pct_locked_master.mp4'}" download class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>📥</span> Download Master MP4
                  </a>
                  <a href="https://studio.youtube.com/channel/videos/upload?d=ud" target="_blank" class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-cyan-300 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>🚀</span> Direct Studio Upload Pop-up ↗
                  </a>
                </div>"""

if btn_target in content:
    content = content.replace(btn_target, btn_replacement, 1)
    print("SUCCESS: Auto-upload button added to cards!")
else:
    print("ERROR: Card button target not found!")

# 3. Add JS functions for daemon control and auto-upload
js_target = """    // Auto init
    loadStatus();
    loadChannels();
    loadUnlistedVideos();
    setInterval(loadStatus, 15000);"""

js_replacement = """    // 24/7 Autonomous Daemon & Auto-Upload Functions
    async function autoUploadVideoNow(vidId, btnElement) {
      if (!confirm(`Launch autonomous Playwright background upload for video '${vidId}'?`)) return;
      const originalHtml = btnElement.innerHTML;
      btnElement.innerHTML = `<span>⏳</span> Launching Genuine Chrome Uploader...`;
      btnElement.disabled = true;
      btnElement.classList.add('opacity-75');

      try {
        const res = await fetch('/api/unlisted-videos/auto-upload-now', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({video_id: vidId})
        });
        const data = await res.json();
        if (data.success) {
          btnElement.innerHTML = `<span>🚀</span> Uploading in Background Chrome...`;
          alert('Playwright Chrome session started! Bot is injecting video, title, tags, thumbnail, and pinning comment.');
          setTimeout(loadUnlistedVideos, 4000);
          setInterval(loadUnlistedVideos, 10000);
        } else {
          alert(`Upload notice: ${data.detail || data.error}`);
          btnElement.innerHTML = originalHtml;
          btnElement.disabled = false;
          btnElement.classList.remove('opacity-75');
        }
      } catch (e) {
        alert(`Error: ${e}`);
        btnElement.innerHTML = originalHtml;
        btnElement.disabled = false;
        btnElement.classList.remove('opacity-75');
      }
    }

    async function togglePerpetualDaemon() {
      const btn = document.getElementById('btnToggleDaemon');
      const isCurrentlyRunning = btn.getAttribute('data-running') === 'true';
      const endpoint = isCurrentlyRunning ? '/api/daemon/stop' : '/api/daemon/start';
      btn.disabled = true;
      btn.innerText = 'Updating...';

      try {
        const res = await fetch(endpoint, {method: 'POST'});
        const data = await res.json();
        loadDaemonStatus();
      } catch (e) {
        console.error(e);
      } finally {
        btn.disabled = false;
      }
    }

    async function loadDaemonStatus() {
      try {
        const res = await fetch('/api/daemon/status');
        const data = await res.json();
        const isRunning = data.is_running;
        const state = data.state || {};

        const btn = document.getElementById('btnToggleDaemon');
        const badge = document.getElementById('daemonStatusBadge');
        const stepText = document.getElementById('daemonStepText');
        const cyclesCount = document.getElementById('daemonCyclesCount');

        if (btn) {
          btn.setAttribute('data-running', isRunning ? 'true' : 'false');
          btn.innerHTML = isRunning 
            ? `<span>⏸️</span> Pause 24/7 Engine` 
            : `<span>🚀</span> Start 24/7 Autonomous Engine`;
          btn.className = isRunning
            ? 'py-2.5 px-5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-extrabold text-xs transition shadow-md shadow-amber-600/30 flex items-center gap-1.5'
            : 'py-2.5 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs transition shadow-md shadow-emerald-600/30 flex items-center gap-1.5 animate-pulse';
        }

        if (badge) {
          badge.innerHTML = isRunning
            ? `<span class=\"w-2 h-2 rounded-full bg-emerald-400 animate-ping\"></span> 🟢 24/7 AUTONOMOUS ENGINE: ACTIVE`
            : `⚪ 24/7 AUTONOMOUS ENGINE: IDLE`;
          badge.className = isRunning
            ? 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
            : 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700';
        }

        if (stepText) {
          stepText.innerText = state.current_step || state.current_status || 'Daemon ready. Click Start to enable 24/7 autonomous production.';
        }
        if (cyclesCount) {
          cyclesCount.innerText = `${state.total_cycles_completed || 0} Videos Published`;
        }
      } catch (e) {
        console.error(e);
      }
    }

    // Auto init
    loadStatus();
    loadChannels();
    loadUnlistedVideos();
    loadDaemonStatus();
    setInterval(loadStatus, 15000);
    setInterval(loadDaemonStatus, 5000);"""

if js_target in content:
    content = content.replace(js_target, js_replacement, 1)
    print("SUCCESS: Daemon JS functions added!")
else:
    print("ERROR: JS target not found!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.html successfully!")
