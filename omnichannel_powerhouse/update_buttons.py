import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """              <!-- Studio Direct Action Button -->
              <div>
                <a href="${v.studio_edit_url}" target="_blank" class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 text-white font-extrabold text-xs md:text-sm transition text-center flex items-center justify-center gap-2 shadow-lg shadow-red-600/30 border border-red-400/30">
                  <span>🔗</span> Open in ${isYoutube ? 'YouTube Studio' : 'Rumble'} to Upload Thumbnail & Paste SEO ↗
                </a>
                <div class="text-[10px] text-slate-400 mt-1.5 text-center">
                  ⚡ <strong>1-Click Workflow:</strong> 1. Download thumbnail ➔ 2. Click button to open Studio ➔ 3. Paste SEO with buttons below!
                </div>
              </div>"""

replacement = """              <!-- Studio Direct Action Button & Smart Router -->
              <div class="space-y-2">
                <a href="${v.studio_edit_url || 'https://studio.youtube.com/videos'}" target="_blank" class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 text-white font-extrabold text-xs md:text-sm transition text-center flex items-center justify-center gap-2 shadow-lg shadow-red-600/30 border border-red-400/30">
                  <span>🔗</span> Open ${isYoutube ? 'YouTube Studio Content Manager' : 'Rumble'} & Upload ↗
                </a>
                <div class="grid grid-cols-2 gap-2">
                  <a href="${v.local_video_path || '/output/demo_ai_15min_hindi_100pct_locked_master.mp4'}" download class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>📥</span> Download Master MP4
                  </a>
                  <a href="https://studio.youtube.com/channel/videos/upload?d=ud" target="_blank" class="py-2 px-3 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-cyan-300 text-xs font-semibold transition text-center flex items-center justify-center gap-1.5 border border-slate-700">
                    <span>🚀</span> Direct Studio Upload Pop-up ↗
                  </a>
                </div>
                <div class="text-[10px] text-slate-400 mt-1 text-center leading-tight">
                  ⚡ <strong>1-Click Workflow:</strong> 1. Download Master MP4 & Thumbnail ➔ 2. Click Studio button ➔ 3. Paste SEO with buttons below!
                </div>
              </div>"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Studio buttons updated!")
else:
    print("ERROR: Target not found in index.html!")
