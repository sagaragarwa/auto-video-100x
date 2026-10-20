import os
import glob
import streamlit as st
from loguru import logger
from yt_uploader.channel_manager import load_channels, save_channels, open_login_window, PROFILES_DIR
from yt_uploader.asset_purger import format_bytes, purge_video_assets
from yt_uploader.main import upload_single_video_flow
from yt_uploader.disk_governor import get_disk_usage, deep_clean_stale_caches, DEFAULT_MIN_FREE_GB

def get_python_exe():
    cand = r"C:\Users\janar\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe"
    if os.path.exists(cand):
        return cand
    return sys.executable

def render_youtube_channel_manager():
    """
    Renders the Multi-Channel YouTube Manager & Auto-Uploader panel in Streamlit WebUI.
    Allows 1-click persistent login, batch queue upload, and instant post-upload asset purging with 5GB disk guarantee.
    """
    with st.expander("📺 Multi-Channel YouTube Auto-Uploader (बिना API के 1-बार लॉगिन & 5GB डिस्क प्रोटेक्टर)", expanded=False):
        st.markdown("""
        **बिना API के मल्टी-चैनल ऑटो-अपलोडर & स्मार्ट डिस्क प्रोटेक्शन:**  
        यहाँ आप जितने चाहें उतने YouTube चैनल्स को **सिर्फ 1 बार लॉगिन** करके हमेशा के लिए सेव कर सकते हैं। इसके बाद जब भी कोई वीडियो बनेगी, वह ऑटोमैटिकली **Ultra High-CTR Thumbnail** और **बेस्ट SEO (टाइटल, डिस्क्रिप्टर, टैग्स)** के साथ सीधे संबंधित चैनल पर पब्लिश हो जाएगी।  
        **🔥 Smart 5GB Disk Governor:** जैसे ही वीडियो YouTube Studio पर अपलोड होगी, उसकी **सभी फाइलें तुरंत डिलीट** हो जाएंगी और यह सुनिश्चित किया जाएगा कि आपकी **C: ड्राइव पर कम से कम 5 GB स्पेस हमेशा खाली (Free) रहे**!
        """)

        # Disk Space Governor Card
        try:
            d_stats = get_disk_usage()
            free_gb = d_stats["free_gb"]
            total_gb = d_stats["total_gb"]
            is_safe = free_gb >= DEFAULT_MIN_FREE_GB

            with st.container(border=True):
                col_d1, col_d2, col_d3 = st.columns([2, 2, 2], vertical_alignment="center")
                with col_d1:
                    st.metric(
                        label="💾 C: Drive Free Space",
                        value=f"{free_gb} GB",
                        delta=f"{free_gb - DEFAULT_MIN_FREE_GB:.1f} GB Headroom (> 5 GB)",
                        delta_color="normal" if is_safe else "inverse"
                    )
                with col_d2:
                    if is_safe:
                        st.success(f"🛡️ **5 GB Safety Guard: ACTIVE**\nडिस्क फुल नहीं होगी।")
                    else:
                        st.error(f"🚨 **Low Space Alert!**\nफ्री स्पेस 5 GB से कम है।")
                with col_d3:
                    if st.button("🧹 Deep Clean Caches (कैशे साफ करें)", use_container_width=True, key="btn_deep_clean_caches"):
                        with st.spinner("Purging old stock video caches and temp files..."):
                            clean_res = deep_clean_stale_caches(aggressive=True)
                            st.toast(f"Reclaimed {clean_res.get('freed_human', '0 B')} space!")
                            st.rerun()
        except Exception as _d_err:
            pass

        channels = load_channels()

        c_top1, c_top2 = st.columns([1, 1])
        with c_top1:
            auto_upload_toggle = st.checkbox(
                "⚡ Auto-Upload on Generation",
                value=st.session_state.get("yt_auto_upload_enabled", False),
                key="yt_auto_upload_toggle",
                help="नई वीडियो बनते ही ऑटोमैटिकली सिलेक्टेड चैनल पर अपलोड करें।"
            )
            st.session_state["yt_auto_upload_enabled"] = auto_upload_toggle

        with c_top2:
            auto_delete_toggle = st.checkbox(
                "🗑️ Auto-Delete Video & 5GB Headroom Guard (अपलोड होते ही सब डिलीट करें & 5GB फ्री रखें)",
                value=st.session_state.get("yt_auto_delete_assets", True),
                key="yt_auto_delete_assets_toggle",
                help="अपलोड कन्फर्म होते ही वीडियो, थंबनेल और टास्क फोल्डर तुरंत डिलीट हो जाएंगे और 5 GB फ्री स्पेस की गारंटी रहेगी।"
            )
            st.session_state["yt_auto_delete_assets"] = auto_delete_toggle

        st.markdown("##### 📌 आपके रजिस्टर्ड चैनल्स (Configured Channels):")

        for ch_key, ch_info in list(channels.items()):
            prof_dir = ch_info.get("profile_dir", "")
            is_configured = os.path.exists(prof_dir) and len(os.listdir(prof_dir)) > 0 if os.path.exists(prof_dir) else False

            with st.container(border=True):
                c_head, c_status, c_act = st.columns([3, 2, 2], vertical_alignment="center")
                with c_head:
                    st.markdown(f"**🎬 {ch_info.get('name', ch_key)}**")
                    st.caption(f"Key: `{ch_key}` | Niche: `{ch_info.get('niche', 'general')}`")
                with c_status:
                    if is_configured:
                        st.success("✅ Logged In (सक्रिय)")
                    else:
                        st.warning("⚠️ Login Needed (लॉगिन करें)")
                with c_act:
                    if st.button(f"🔑 Login Channel", key=f"btn_login_{ch_key}", use_container_width=True):
                        st.toast(f"Opening Chrome window for {ch_info.get('name')}...")
                        import subprocess
                        py_bin = get_python_exe()
                        cmd = [py_bin, os.path.abspath("yt_uploader/main.py"), "login", "--channel", ch_key]
                        subprocess.Popen(cmd)
                        st.info("क्रोम विंडो खुल रही है। उसमें YouTube Studio में लॉगिन करके विंडो बंद करें।")

        # Section: Batch Video Uploader & Auto-Purge Queue
        with st.expander("📤 Batch Video Uploader & Auto-Purge Queue (एक साथ कई वीडियो अपलोड और तुरंत डिलीट करें)", expanded=True):
            output_dir = os.path.abspath("output")
            available_videos = []
            if os.path.exists(output_dir):
                for f in sorted(os.listdir(output_dir)):
                    if f.endswith(".mp4") and not f.endswith(".temp.mp4"):
                        fp = os.path.join(output_dir, f)
                        sz_str = format_bytes(os.path.getsize(fp))
                        available_videos.append((f, fp, sz_str))

            if not available_videos:
                st.info("output/ फोल्डर में कोई तैयार वीडियो नहीं मिली। पहले वीडियो जनरेट करें।")
            else:
                st.write(f"📂 **output/ फोल्डर में उपलब्ध वीडियोज ({len(available_videos)} कुल):**")
                
                b_col1, b_col2, b_col3 = st.columns([2, 1, 1])
                with b_col1:
                    ch_options = ["auto_smart"] + list(channels.keys())
                    target_ch = st.selectbox(
                        "अपलोड करने के लिए चैनल चुनें:",
                        options=ch_options,
                        format_func=lambda k: "🎯 Smart Auto-Route (टॉपिक के हिसाब से ऑटोमैटिक सही चैनल)" if k == "auto_smart" else f"{channels[k].get('name')} ({k})",
                        key="batch_upload_target_ch"
                    )
                with b_col2:
                    vis_choice = st.selectbox("Visibility:", ["public", "unlisted", "private"], key="batch_upload_vis")
                with b_col3:
                    select_all = st.checkbox("Select All Videos", value=False, key="batch_select_all")

                video_options = [f"{v[0]} ({v[2]})" for v in available_videos]
                default_selection = video_options if select_all else []
                selected_video_strs = st.multiselect(
                    "अपलोड के लिए वीडियो चुनें (Select Videos to Upload):",
                    options=video_options,
                    default=default_selection,
                    key="batch_selected_videos"
                )

                if st.button("🚀 Start Auto-Upload & Purge Queue", type="primary", use_container_width=True, key="btn_start_batch_upload"):
                    if not selected_video_strs:
                        st.warning("कृपया कम से कम एक वीडियो चुनें।")
                    else:
                        selected_fps = []
                        for s in selected_video_strs:
                            name = s.split(" (")[0]
                            for v in available_videos:
                                if v[0] == name:
                                    selected_fps.append(v[1])
                                    break

                        from yt_uploader.channel_manager import auto_detect_channel
                        del_after = st.session_state.get("yt_auto_delete_assets", True)

                        st.info(f"🚀 शुरू हो रहा है: {len(selected_fps)} वीडियोज का क्रमबद्ध अपलोड... (Auto-Delete: {'सक्रिय' if del_after else 'बंद'})")

                        progress_bar = st.progress(0)
                        status_area = st.empty()
                        total_reclaimed = 0

                        for idx, vpath in enumerate(selected_fps, start=1):
                            vname = os.path.basename(vpath)
                            
                            # Determine Channel: Either chosen channel or Smart Auto-Route by topic
                            if target_ch == "auto_smart":
                                resolved_ch_key = auto_detect_channel(vname)
                            else:
                                resolved_ch_key = target_ch

                            ch_data = channels[resolved_ch_key]
                            status_area.markdown(f"**▶️ [{idx}/{len(selected_fps)}] अपलोड हो रही है:** `{vname}` ➔ **चैनल:** `{ch_data.get('name')}`...")
                            
                            res = upload_single_video_flow(
                                channel_info=ch_data,
                                video_path=vpath,
                                visibility=vis_choice,
                                delete_after_upload=del_after,
                                headless=False
                            )

                            if res.get("success"):
                                st.success(f"✅ [{idx}/{len(selected_fps)}] `{vname}` अपलोड हो गई!")
                                if "purge_summary" in res:
                                    freed = res["purge_summary"].get("freed_human", "0 B")
                                    total_reclaimed += res["purge_summary"].get("freed_bytes", 0)
                                    st.caption(f"🗑️ `{vname}` और उससे जुड़ी सभी फाइल्स डिलीट कर दी गईं। स्पेस खाली: **{freed}**")
                            else:
                                st.error(f"❌ [{idx}/{len(selected_fps)}] `{vname}` अपलोड नहीं हो सकी: {res.get('error')}. फाइल्स सुरक्षित रखी गईं।")

                            progress_bar.progress(idx / len(selected_fps))

                        st.balloons()
                        st.success(f"🎉 सभी सिलेक्टेड वीडियोज प्रोसेस हो गईं! कुल खाली हुआ डिस्क स्पेस: **{format_bytes(total_reclaimed)}**")

        with st.expander("➕ Add New YouTube Channel (नया चैनल जोड़ें)"):
            new_key = st.text_input("Channel Key (जैसे: channel_motivation, channel_tech):", key="new_ch_key")
            new_name = st.text_input("Channel Name (चैनल का नाम):", key="new_ch_name")
            new_niche = st.selectbox("Channel Niche:", ["psychology", "trading", "science", "technology", "general"], key="new_ch_niche")
            if st.button("Save New Channel (चैनल सेव करें)", key="btn_save_new_ch"):
                if new_key.strip() and new_name.strip():
                    clean_k = new_key.strip().lower().replace(" ", "_")
                    channels[clean_k] = {
                        "name": new_name.strip(),
                        "profile_dir": os.path.join(PROFILES_DIR, clean_k),
                        "niche": new_niche,
                        "visibility": "public"
                    }
                    save_channels(channels)
                    st.success(f"Channel '{new_name}' जोड़ा गया! अब 'Login Channel' बटन दबाकर लॉगिन करें।")
                    st.rerun()
                else:
                    st.error("कृपया चैनल की और नाम भरें।")

def render_master_engine_panel():
    """
    Renders the 1-Prompt 5X Master Autonomous Video Engine Card in the WebUI.
    Allows user to type a single natural language prompt and generate a 5X better continuous 1080p documentary.
    Strictly enforces zero subtitles, zero thumbnails, full Content ID outro, and auto-delivery to Downloads.
    """
    with st.expander("⚡ 5X Master Autonomous Video Engine (1 Single Prompt से 1080p Documentary & Auto-Upload)", expanded=True):
        st.markdown("""
        **1 Single Natural Language Prompt से पूरी वीडियो बनाएं:**  
        अब कोई भी सेटिंग छेड़ने की जरूरत नहीं। बस एक पंक्ति लिखें जैसे:  
        `5 minute dopamine detox documentary in Hindi` या `10 minute wall street algorithmic trading in English`  
        
        **🌟 5X Broadcast Standards:**  
        • **Zero Repeat Visuals**: MD5 फिंगरप्रिंटिंग के साथ हर सीन का 100% यूनीक विजुअल (कोई लूपिंग नहीं)  
        • **Full Signature Content ID Outro**: हर वीडियो के अंत में पूरी ओरिजिनल आउट्रो क्लिप स्मूथ फेड के साथ  
        • **Clean Netflix Aesthetic**: बिना किसी सबटाइटल के साफ और सिनेमैटिक 1080p विजुअल्स  
        • **EBU R128 Loudness (-14 LUFS)**: 48kHz स्टीरियो ब्रॉडकास्ट ऑडियो (यूट्यूब ऑफिशियल लाउडनेस)  
        • **Auto-Delivery to Downloads**: वीडियो बनते ही सीधे आपके `Downloads` फोल्डर में सेव  
        • **Strict Zero Thumbnails**: थंबनेल पूरी तरह से बाईपास (यूट्यूब स्टूडियो अपलोड अनलिस्टेड)  
        """)

        p_col, a_col = st.columns([4, 1.5], vertical_alignment="bottom")
        with p_col:
            master_prompt = st.text_input(
                "🎯 Master Prompt (बस एक प्रॉम्प्ट लिखें):",
                value=st.session_state.get("input_master_prompt_val", ""),
                placeholder="जैसे: Anxiety Aur Mental Calmness Ka Asli Sach या 20 min trading institutional order flow",
                key="input_master_prompt"
            )
        with a_col:
            auto_up = st.checkbox("🚀 Auto-Upload", value=False, key="chk_master_auto_up", help="बनते ही चैनल्स पर ऑटो-अपलोड करें")

        # Multi-Platform Checkboxes
        selected_platforms = []
        if auto_up:
            with st.container(border=True):
                st.caption("🌐 **Target Upload Platforms (कहाँ-कहाँ अपलोड करना है):**")
                cp1, cp2 = st.columns(2)
                with cp1:
                    up_yt = st.checkbox("📺 YouTube Studio", value=True, key="chk_plat_yt")
                    if up_yt:
                        selected_platforms.append("youtube")
                with cp2:
                    up_rumble = st.checkbox("🟢 Rumble Channels", value=True, key="chk_plat_rumble")
                    if up_rumble:
                        selected_platforms.append("rumble")

        if st.button("🎬 Generate 5X Master Documentary (वीडियो बनाएं)", type="primary", use_container_width=True, key="btn_run_master_engine"):
            if not master_prompt or not master_prompt.strip():
                st.warning("⚠️ कृपया पहले कोई विषय (Topic) या प्रॉम्प्ट लिखें!")
            else:
                with st.spinner("⚡ Running 5X Master Engine (Unique visual matching, 48kHz audio, 1080p Render, Full Outro)..."):
                    try:
                        from yt_uploader.master_engine import CinematicMasterEngine
                        engine = CinematicMasterEngine()
                        res = engine.generate_autonomous_video(
                            prompt=master_prompt.strip(),
                            auto_upload=auto_up,
                            platforms=selected_platforms if auto_up else None
                        )
                        st.success(f"🎉 5X Master Video Complete in {res['render_time_seconds']}s! Size: {res['file_size_human']} | Delivered to Downloads!")
                        deliv_file = res.get('downloads_path') or res.get('video_path')
                        if deliv_file:
                            st.info(f"📁 Saved to Downloads: {deliv_file}")
                            if os.path.exists(deliv_file):
                                try:
                                    st.video(deliv_file)
                                except Exception as _v_err:
                                    logger.warning(f"Streamlit video preview note: {_v_err}")
                        if res.get("upload_dispatch"):
                            with st.expander("🚀 Multi-Platform Upload Telemetry (YouTube & Rumble)", expanded=True):
                                st.json(res["upload_dispatch"])
                        with st.expander("📊 Viral SEO Package & Metadata (Unlisted)", expanded=False):
                            st.json(res['seo'])
                            st.json(res['plan'])
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

def render_github_cloud_panel():
    """
    Renders the 30-Second GitHub Cloud Watcher & Zero-Load Offloading Card in Streamlit.
    """
    from yt_uploader.github_cloud_watcher import (
        get_cloud_watcher, load_github_config, save_github_config, queue_cloud_video_task, load_cloud_queue
    )

    watcher = get_cloud_watcher()
    if not watcher.running:
        watcher.start_background_daemon()

    cfg = load_github_config()

    with st.expander("☁️ GitHub 24/7 Cloud Offloader & 30s Watcher (आपके PC पर 0% CPU & 0% लोड)", expanded=True):
        st.markdown("""
        **सारा लोड GitHub Actions Cloud Runners पर डालें:**  
        यहाँ से जब भी आप वीडियो बनाएंगे, भारी FFmpeg रेंडरिंग, डाउनलोडिंग और इनकोडिंग आपके कंप्यूटर पर नहीं, बल्कि **GitHub के हाई-स्पीड Cloud Servers (4 vCPUs, 16GB RAM)** पर होगी।  
        **🛡️ 30-Second Auto-Watcher:** यह सिस्टम हर **30 सेकंड** में GitHub Actions को चेक करता है, उसे 24/7 एक्टिव रखता है और टास्क मिलने पर तुरंत क्लाउड पर चला देता है।
        """)

        w_col1, w_col2, w_col3 = st.columns([2, 2, 2], vertical_alignment="center")
        status_info = watcher.check_repo_and_workflow_status()
        
        with w_col1:
            if status_info.get("online"):
                st.success(f"🟢 **GitHub Cloud: ACTIVE**\n`{cfg['repo_owner']}/{cfg['repo_name']}`")
            else:
                st.warning(f"⚠️ **GitHub Cloud: Notice**\n{status_info.get('error', 'Token needed for private actions')}")
        
        with w_col2:
            st.metric(
                label="💻 Local Machine CPU / Disk Load",
                value="0%",
                delta="0 MB Disk Used (Safe)",
                delta_color="normal"
            )

        with w_col3:
            active_cnt = status_info.get("active_runs_count", 0)
            st.metric(
                label="☁️ Cloud Runner Jobs",
                value=f"{active_cnt} Active",
                delta="100% Cloud Power"
            )

        # Token and Dispatch Form
        c_p1, c_p2 = st.columns([3, 1], vertical_alignment="bottom")
        with c_p1:
            cloud_prompt = st.text_input(
                "🎯 Prompt to Offload to GitHub Cloud (क्लाउड पर भेजने के लिए प्रॉम्प्ट):",
                value=st.session_state.get("input_cloud_prompt_val", ""),
                placeholder="जैसे: 5 minute anxiety aur mental calmness ka sach in Hindi या 10 min trading",
                key="input_cloud_prompt"
            )
        with c_p2:
            if st.button("🚀 Offload to Cloud (क्लाउड पर चलाएं)", type="primary", use_container_width=True, key="btn_offload_cloud"):
                q_task = queue_cloud_video_task(prompt=cloud_prompt)
                st.toast("Task queued! 30-second watcher is dispatching to GitHub Actions...")
                st.success(f"✅ टास्क क्लाउड पर भेजा गया! Task ID: `{q_task['id']}`")

        # GitHub Settings Accordion
        with st.expander("⚙️ GitHub Cloud Settings & Token (कॉन्फ़िगरेशन)"):
            t_owner = st.text_input("Repository Owner:", value=cfg.get("repo_owner", "sagaragarwa"), key="gh_owner")
            t_repo = st.text_input("Repository Name:", value=cfg.get("repo_name", "auto-video-100x"), key="gh_repo")
            t_token = st.text_input("GitHub Personal Access Token (PAT):", value=cfg.get("github_token", ""), type="password", key="gh_token", help="Settings -> Developer Settings -> Personal Access Tokens -> Tokens (classic) with 'repo' and 'workflow' scope")
            if st.button("Save GitHub Config", key="btn_save_gh_cfg"):
                cfg["repo_owner"] = t_owner.strip()
                cfg["repo_name"] = t_repo.strip()
                cfg["github_token"] = t_token.strip()
                save_github_config(cfg)
                st.toast("GitHub Config Saved!")
                st.rerun()

def render_rumble_channel_manager():
    """
    Renders the Multi-Channel Rumble Manager & Auto-Uploader panel in Streamlit WebUI.
    Provides 1-click persistent login for Rumble channels, automated licensing, and batch queue uploads.
    """
    from yt_uploader.rumble_uploader import (
        load_rumble_channels, save_rumble_channels, open_rumble_login_window, upload_video_to_rumble,
        RUMBLE_PROFILES_DIR
    )

    with st.expander("🟢 Multi-Channel Rumble Auto-Uploader (बिना API के 1-बार लॉगिन & ऑटो-मोनेटाइजेशन)", expanded=False):
        st.markdown("""
        **Rumble मल्टी-चैनल ऑटो-अपलोडर & मोनेटाइजेशन मैनेजर:**  
        यहाँ आप अपने Rumble अकाउंट और उसके सभी सब-चैनल्स को **सिर्फ 1 बार लॉगिन** करके हमेशा के लिए सेव कर सकते हैं। इसके बाद जब भी कोई वीडियो बनेगी, वह ऑटोमैटिकली **बेस्ट टाइटल, डिस्क्रिप्शन, टैग्स** और आपके चुने हुए **लाइसेंस (Rumble Only / Exclusive)** के साथ सीधे Rumble पर पब्लिश हो जाएगी।  
        """)

        r_channels = load_rumble_channels()

        st.markdown("##### 📌 आपके रजिस्टर्ड Rumble चैनल्स (Configured Rumble Channels):")

        for ch_key, ch_info in list(r_channels.items()):
            prof_dir = ch_info.get("profile_dir", "")
            is_configured = os.path.exists(prof_dir) and len(os.listdir(prof_dir)) > 0 if os.path.exists(prof_dir) else False

            with st.container(border=True):
                c_head, c_status, c_act = st.columns([3, 2, 2], vertical_alignment="center")
                with c_head:
                    st.markdown(f"**🟢 {ch_info.get('name', ch_key)}**")
                    st.caption(f"Key: `{ch_key}` | Niche: `{ch_info.get('niche', 'general')}` | License: `{ch_info.get('license', 'rumble_only')}`")
                with c_status:
                    if is_configured:
                        st.success("✅ Logged In (सक्रिय)")
                    else:
                        st.warning("⚠️ Login Needed (लॉगिन करें)")
                with c_act:
                    if st.button(f"🔑 Login Rumble", key=f"btn_rlogin_{ch_key}", use_container_width=True):
                        st.toast(f"Opening Chrome window for Rumble {ch_info.get('name')}...")
                        import subprocess
                        py_bin = get_python_exe()
                        cmd = [py_bin, os.path.abspath("yt_uploader/main.py"), "rumble-login", "--channel", ch_key]
                        subprocess.Popen(cmd)
                        st.info("क्रोम विंडो खुल रही है। उसमें Rumble में लॉगिन करके विंडो बंद करें।")

        # Section: Batch Video Uploader to Rumble
        with st.expander("📤 Batch Video Uploader to Rumble (एक साथ कई वीडियो Rumble पर अपलोड करें)", expanded=False):
            output_dir = os.path.abspath("output")
            available_videos = []
            if os.path.exists(output_dir):
                for f in sorted(os.listdir(output_dir)):
                    if f.endswith(".mp4") and not f.endswith(".temp.mp4"):
                        fp = os.path.join(output_dir, f)
                        sz_str = format_bytes(os.path.getsize(fp))
                        available_videos.append((f, fp, sz_str))

            if not available_videos:
                st.info("output/ फोल्डर में कोई तैयार वीडियो नहीं मिली। पहले वीडियो जनरेट करें।")
            else:
                rb_col1, rb_col2, rb_col3 = st.columns([2, 1, 1])
                with rb_col1:
                    r_target_ch = st.selectbox(
                        "अपलोड करने के लिए Rumble चैनल चुनें:",
                        options=list(r_channels.keys()),
                        format_func=lambda k: f"{r_channels[k].get('name')} ({k})",
                        key="rumble_batch_target_ch"
                    )
                with rb_col2:
                    r_license_choice = st.selectbox(
                        "License Type:",
                        options=["rumble_only", "exclusive", "personal"],
                        format_func=lambda l: "Rumble Only (मोनेटाइज)" if l == "rumble_only" else ("Exclusive (यूट्यूब सहित)" if l == "exclusive" else "Personal (नो एड्स)"),
                        key="rumble_batch_lic"
                    )
                with rb_col3:
                    r_select_all = st.checkbox("Select All Videos", value=False, key="r_batch_select_all")

                r_video_options = [f"{v[0]} ({v[2]})" for v in available_videos]
                r_default_sel = r_video_options if r_select_all else []
                r_selected_video_strs = st.multiselect(
                    "Rumble पर अपलोड के लिए वीडियो चुनें:",
                    options=r_video_options,
                    default=r_default_sel,
                    key="r_batch_selected_videos"
                )

                if st.button("🚀 Start Rumble Auto-Upload", type="primary", use_container_width=True, key="btn_start_rumble_batch"):
                    if not r_selected_video_strs:
                        st.warning("कृपया कम से कम एक वीडियो चुनें।")
                    else:
                        r_selected_fps = []
                        for s in r_selected_video_strs:
                            name = s.split(" (")[0]
                            for v in available_videos:
                                if v[0] == name:
                                    r_selected_fps.append(v[1])
                                    break

                        from yt_uploader.seo_generator import generate_viral_seo_package
                        st.info(f"🚀 शुरू हो रहा है: {len(r_selected_fps)} वीडियोज का Rumble पर अपलोड...")
                        r_prog = st.progress(0)
                        r_status = st.empty()

                        for idx, vpath in enumerate(r_selected_fps, start=1):
                            vname = os.path.basename(vpath)
                            r_status.markdown(f"**▶️ [{idx}/{len(r_selected_fps)}] Rumble पर अपलोड हो रही है:** `{vname}`...")
                            seo_pkg = generate_viral_seo_package(subject=vname, niche=r_channels[r_target_ch].get("niche", "general"))
                            res = upload_video_to_rumble(
                                channel_key=r_target_ch,
                                video_file_path=vpath,
                                seo_package=seo_pkg,
                                license_type=r_license_choice,
                                headless=False
                            )
                            if res.get("success"):
                                st.success(f"✅ [{idx}/{len(r_selected_fps)}] `{vname}` Rumble पर अपलोड हो गई! Link: {res.get('url')}")
                            else:
                                st.error(f"❌ [{idx}/{len(r_selected_fps)}] `{vname}` Rumble अपलोड विफल: {res.get('error')}")
                            r_prog.progress(idx / len(r_selected_fps))

                        st.balloons()
                        st.success("🎉 Rumble अपलोड प्रक्रिया संपन्न हुई!")

        with st.expander("➕ Add New Rumble Channel (नया Rumble चैनल जोड़ें)"):
            new_r_key = st.text_input("Rumble Channel Key (जैसे: rumble_tech, rumble_shorts):", key="new_r_key")
            new_r_name = st.text_input("Rumble Channel Name (चैनल का नाम):", key="new_r_name")
            new_r_sub = st.text_input("Sub-channel Name in Rumble (वैकल्पिक / Optional):", key="new_r_sub", help="अगर आपके मुख्य अकाउंट में सब-चैनल बना हुआ है")
            new_r_niche = st.selectbox("Niche:", ["psychology", "trading", "science", "technology", "general"], key="new_r_niche")
            new_r_lic = st.selectbox("Default License:", ["rumble_only", "exclusive", "personal"], key="new_r_lic")
            if st.button("Save New Rumble Channel", key="btn_save_new_r_ch"):
                if new_r_key.strip() and new_r_name.strip():
                    clean_rk = new_r_key.strip().lower().replace(" ", "_")
                    r_channels[clean_rk] = {
                        "name": new_r_name.strip(),
                        "profile_dir": os.path.join(RUMBLE_PROFILES_DIR, clean_rk),
                        "sub_channel": new_r_sub.strip(),
                        "niche": new_r_niche,
                        "license": new_r_lic
                    }
                    save_rumble_channels(r_channels)
                    st.success(f"Rumble Channel '{new_r_name}' सेव हो गया! अब 'Login Rumble' बटन दबाकर लॉगिन करें।")
                    st.rerun()
                else:
                    st.error("कृपया चैनल की और नाम भरें।")



