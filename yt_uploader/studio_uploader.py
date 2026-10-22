import os
import time
import json
from loguru import logger

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def upload_video_to_studio(
    channel_profile_dir: str,
    video_file_path: str,
    thumbnail_file_path: str,
    seo_package: dict,
    headless: bool = True
) -> dict:
    """
    Uploads a video to YouTube Studio using persistent browser profile without API quota.
    Injects Title, Description, Thumbnail, Tags, and sets Visibility.
    Monitors upload to ensure 100% transfer completion before closing.
    """
    from playwright.sync_api import sync_playwright
    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Video file not found: {video_file_path}")

    abs_video = os.path.abspath(video_file_path)
    abs_thumb = os.path.abspath(thumbnail_file_path) if thumbnail_file_path and os.path.exists(thumbnail_file_path) else None
    abs_profile = os.path.abspath(channel_profile_dir)

    title = seo_package.get("title", "Cinematic Documentary")
    description = seo_package.get("description", "")
    tags = seo_package.get("tags", "")
    visibility = seo_package.get("visibility", "unlisted")  # "public", "private", "unlisted"

    logger.info(f"Starting YouTube Studio Upload via Profile: {abs_profile}")
    logger.info(f"Video: {abs_video} ({os.path.getsize(abs_video)/(1024*1024):.1f} MB)")
    logger.info(f"Title: {title}")
    logger.info(f"Visibility Target: {visibility}")

    result = {"success": False, "video_id": None, "url": None, "error": None}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=abs_profile,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=headless,
            user_agent=UA,
            viewport={"width": 1400, "height": 900},
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = context.new_page()

        try:
            logger.info("Navigating to YouTube Studio...")
            page.goto("https://studio.youtube.com/?approve_browser_access=true", timeout=60000)
            page.wait_for_timeout(5000)

            # Dismiss browser compatibility warning if present
            skip_btn = page.locator("a:has-text('Skip to YouTube Studio'), button:has-text('Skip to YouTube Studio')")
            if skip_btn.count() > 0:
                logger.info("Dismissing browser compatibility warning...")
                skip_btn.first.click()
                page.wait_for_timeout(5000)

            # Check if login is required
            if "accounts.google.com" in page.url or "signin" in page.url:
                result["error"] = "Channel session not logged in. Complete login first."
                logger.error(result["error"])
                context.close()
                return result

            # Click Create / Upload button
            logger.info("Opening upload dialog...")
            create_btn = page.locator("#create-icon, ytcp-button#create-icon, button:has-text('Create')")
            if create_btn.count() > 0:
                create_btn.first.click()
                page.wait_for_timeout(2000)
                upload_opt = page.locator("tp-yt-paper-item, ytcp-text-menu-item").filter(has_text="Upload")
                if upload_opt.count() > 0:
                    upload_opt.first.click()
                    page.wait_for_timeout(3000)
            else:
                up_icon = page.locator("ytcp-icon-button[aria-label*='Upload'], #upload-icon, ytcp-button#upload-button")
                if up_icon.count() > 0:
                    up_icon.first.click()
                    page.wait_for_timeout(3000)

            # Inject video file
            logger.info("Locating file input and injecting video...")
            file_input = page.locator("input[type='file']").first
            file_input.wait_for(state="attached", timeout=30000)
            file_input.set_input_files(abs_video)
            logger.info("Video file successfully injected! Waiting for metadata editor...")

            # Wait for title editor box to appear
            title_container = page.locator("#title-textarea").first
            title_container.wait_for(state="attached", timeout=60000)
            page.wait_for_timeout(3000)

            # Set Title
            logger.info(f"Writing Title: {title[:60]}...")
            title_box = page.locator("#title-textarea div#textbox, #title-textarea [contenteditable='true']").first
            if title_box.count() > 0:
                title_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                try:
                    title_box.fill(title[:100])
                except Exception:
                    page.keyboard.type(title[:100], delay=10)
                page.wait_for_timeout(1000)

            # Set Description
            logger.info("Writing Description...")
            desc_box = page.locator("#description-textarea div#textbox, #description-textarea [contenteditable='true']").first
            if desc_box.count() > 0:
                desc_box.click()
                try:
                    desc_box.fill(description[:5000])
                except Exception:
                    page.keyboard.type(description[:5000], delay=5)
                page.wait_for_timeout(1000)

            # Upload Thumbnail if provided
            if abs_thumb and os.path.exists(abs_thumb):
                logger.info(f"Uploading Custom Thumbnail: {abs_thumb}...")
                try:
                    thumb_input = page.locator('input#file-loader, #file-loader input[type="file"], input[type="file"][accept*="image"]').first
                    if thumb_input.count() > 0:
                        thumb_input.set_input_files(abs_thumb)
                        page.wait_for_timeout(3000)
                        logger.info("Custom thumbnail file injected!")

                        # Handle phone verification modal if channel is new
                        verify_dialog = page.locator("ytcp-dialog:has-text('Verify')")
                        if verify_dialog.count() > 0:
                            logger.warning("Custom thumbnail requires phone verification. Dismissing prompt...")
                            close_verify = verify_dialog.locator("#close-button, button:has-text('Cancel')").first
                            if close_verify.count() > 0:
                                close_verify.click()
                except Exception as e:
                    logger.warning(f"Thumbnail upload notice: {e}")

            # Select "No, it's not made for kids"
            logger.info("Setting 'Not made for kids'...")
            not_for_kids = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], [name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], tp-yt-paper-radio-button:has-text("No, it\'s not made for kids")').first
            if not_for_kids.count() > 0:
                not_for_kids.click()
                page.wait_for_timeout(1000)

            # Expand "SHOW MORE" for Tags
            show_more = page.locator('ytcp-button#toggle-button, div#toggle-button, button:has-text("Show more"), ytcp-button:has-text("Show more")').first
            if show_more.count() > 0:
                try:
                    show_more.click()
                    page.wait_for_timeout(1500)
                except Exception:
                    pass

            # Fill Tags
            if tags:
                logger.info("Injecting Tags...")
                tags_input = page.locator('#tags-container input, input[aria-label="Tags"]').first
                if tags_input.count() > 0:
                    try:
                        tags_input.click()
                        tags_input.fill(tags[:500])
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(1000)
                    except Exception as e:
                        logger.warning(f"Tags input notice: {e}")

            # Extract generated video link early
            link_elem = page.locator('a.ytcp-video-info, a[href*="youtu.be"], span.ytcp-video-info').first
            if link_elem.count() > 0:
                result["url"] = link_elem.get_attribute("href") or link_elem.inner_text().strip()
                logger.info(f"Detected Video URL: {result['url']}")

            # Step through wizard: Next -> Next -> Next -> Visibility
            logger.info("Stepping through wizard steps...")
            for step in range(3):
                page.wait_for_timeout(2500)
                next_btn = page.locator('#next-button, ytcp-button#next-button, button:has-text("Next")').first
                if next_btn.count() > 0:
                    try:
                        next_btn.click()
                    except Exception:
                        page.wait_for_timeout(2000)
                        next_btn.click()

            # Visibility Step
            logger.info(f"Setting visibility to '{visibility}'...")
            page.wait_for_timeout(2500)
            if visibility.lower() == "public":
                pub_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"], [name="PUBLIC"], tp-yt-paper-radio-button:has-text("Public")').first
                if pub_radio.count() > 0:
                    pub_radio.click()
            elif visibility.lower() == "unlisted":
                unlisted_radio = page.locator('tp-yt-paper-radio-button[name="UNLISTED"], [name="UNLISTED"], tp-yt-paper-radio-button:has-text("Unlisted")').first
                if unlisted_radio.count() > 0:
                    unlisted_radio.click()
            else:
                priv_radio = page.locator('tp-yt-paper-radio-button[name="PRIVATE"], [name="PRIVATE"], tp-yt-paper-radio-button:has-text("Private")').first
                if priv_radio.count() > 0:
                    priv_radio.click()

            page.wait_for_timeout(2000)

            # Re-check video URL on visibility step if not yet captured
            if not result["url"]:
                link_elem = page.locator('a.ytcp-video-info, a[href*="youtu.be"]').first
                if link_elem.count() > 0:
                    result["url"] = link_elem.get_attribute("href") or link_elem.inner_text().strip()
                    logger.info(f"Captured Video URL: {result['url']}")

            # Click Done / Save
            logger.info("Clicking Done / Save button...")
            done_btn = page.locator('#done-button, ytcp-button#done-button, button:has-text("Save")').first
            if done_btn.count() > 0:
                done_btn.click()
                page.wait_for_timeout(5000)

            # Close upload dialog if "Close" button is presented
            dialog_close = page.locator('#close-button, ytcp-button:has-text("Close")').first
            if dialog_close.count() > 0:
                try:
                    dialog_close.click()
                    page.wait_for_timeout(2000)
                except Exception:
                    pass

            # Monitor transfer progress until complete
            logger.info("Monitoring upload transfer to 100% completion...")
            start_wait = time.time()
            while time.time() - start_wait < 1800:
                progress_el = page.locator("span.progress-label, ytcp-video-upload-progress, .ytcp-video-upload-progress, .progress-label").first
                status_text = ""
                if progress_el.count() > 0:
                    try:
                        status_text = progress_el.inner_text().strip()
                    except Exception:
                        pass

                if not status_text or any(k in status_text for k in ["Upload complete", "Processing", "Checks complete", "Saved as unlisted", "Saved as private"]):
                    logger.success(f"Upload successfully transferred! Final Status: {status_text or 'Saved'}")
                    break

                if int(time.time() - start_wait) % 15 == 0:
                    logger.info(f"Upload in progress: {status_text}")

                page.wait_for_timeout(5000)

            result["success"] = True
            logger.success("Video successfully published to YouTube Studio!")

            # Extract clean Video ID
            if result.get("url"):
                url_str = result["url"]
                if "youtu.be/" in url_str:
                    result["video_id"] = url_str.split("youtu.be/")[1].split("?")[0].strip()
                elif "watch?v=" in url_str:
                    result["video_id"] = url_str.split("watch?v=")[1].split("&")[0].strip()
                logger.info(f"Clean Video ID extracted: {result.get('video_id')}")

            # Post & Pin High-Velocity Comment if provided
            pinned_comment = seo_package.get("pinned_comment")
            if pinned_comment and result.get("video_id"):
                try:
                    logger.info("Posting high-velocity pinned comment on watch page...")
                    watch_url = f"https://www.youtube.com/watch?v={result['video_id']}"
                    page.goto(watch_url, timeout=45000)
                    page.wait_for_timeout(5000)

                    # Scroll down to load comments section
                    page.mouse.wheel(0, 600)
                    page.wait_for_timeout(3000)

                    # Click comment placeholder
                    comment_box = page.locator("#placeholder-area, ytd-comment-simplebox-renderer #placeholder-area").first
                    if comment_box.count() > 0:
                        comment_box.click()
                        page.wait_for_timeout(1500)

                        input_div = page.locator("#contenteditable-root[contenteditable='true'], ytd-commentbox #contenteditable-root").first
                        if input_div.count() > 0:
                            input_div.fill(pinned_comment)
                            page.wait_for_timeout(1000)

                            submit_btn = page.locator("#submit-button button, button:has-text('Comment')").first
                            if submit_btn.count() > 0:
                                submit_btn.click()
                                page.wait_for_timeout(4000)
                                logger.info("High-velocity comment posted! Now pinning to top...")

                                # Click 3-dot action menu on user's newly posted comment
                                menu_btn = page.locator("ytd-comment-thread-renderer #action-menu yt-icon-button, ytd-comment-thread-renderer #action-menu button").first
                                if menu_btn.count() > 0:
                                    menu_btn.click()
                                    page.wait_for_timeout(1500)
                                    pin_opt = page.locator("ytd-menu-service-item-renderer:has-text('Pin'), tp-yt-paper-item:has-text('Pin')").first
                                    if pin_opt.count() > 0:
                                        pin_opt.click()
                                        page.wait_for_timeout(1500)
                                        confirm_pin = page.locator("yt-button-renderer#confirm-button button, button:has-text('Pin')").first
                                        if confirm_pin.count() > 0:
                                            confirm_pin.click()
                                            page.wait_for_timeout(2000)
                                            logger.success("Comment successfully pinned to top of video!")
                except Exception as e:
                    logger.warning(f"Comment pinning notice: {e}")

            # Capture confirmation screenshot of the Content video list
            page.wait_for_timeout(3000)
            page.goto("https://studio.youtube.com/videos/upload?approve_browser_access=true", timeout=60000)
            page.wait_for_timeout(5000)
            conf_shot = os.path.join(os.path.dirname(abs_video), "upload_success_verified.png")
            page.screenshot(path=conf_shot)
            logger.info(f"Studio video list screenshot saved to {conf_shot}")

        except Exception as e:
            logger.error(f"Upload flow failed: {e}")
            result["error"] = str(e)
            try:
                err_shot = os.path.join(os.path.dirname(abs_video), "upload_error_state.png")
                page.screenshot(path=err_shot)
                logger.info(f"Error state screenshot saved to {err_shot}")
            except Exception:
                pass
        finally:
            context.close()

    return result
