import os
import time
import json
from loguru import logger
from playwright.sync_api import sync_playwright

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

def upload_video_to_studio(
    channel_profile_dir: str,
    video_file_path: str,
    thumbnail_file_path: str,
    seo_package: dict,
    headless: bool = False
) -> dict:
    """
    Uploads a video to YouTube Studio using persistent browser profile without API quota.
    Injects Title, Description, Thumbnail, Tags, and sets Visibility.
    """
    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Video file not found: {video_file_path}")

    abs_video = os.path.abspath(video_file_path)
    abs_thumb = os.path.abspath(thumbnail_file_path) if thumbnail_file_path and os.path.exists(thumbnail_file_path) else None
    abs_profile = os.path.abspath(channel_profile_dir)

    title = seo_package.get("title", "Cinematic Documentary")
    description = seo_package.get("description", "")
    tags = seo_package.get("tags", "")
    visibility = seo_package.get("visibility", "public") # "public", "private", "unlisted"

    logger.info(f"Starting YouTube Studio Upload via Profile: {abs_profile}")
    logger.info(f"Video: {abs_video}")
    logger.info(f"Title: {title}")

    result = {"success": False, "video_id": None, "url": None, "error": None}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=abs_profile,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=headless,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = context.new_page()

        try:
            logger.info("Navigating to YouTube Studio...")
            page.goto("https://studio.youtube.com", timeout=60000)
            page.wait_for_timeout(5000)

            # Check if login is required
            if "accounts.google.com" in page.url or "signin" in page.url:
                result["error"] = "Channel session not logged in. Run 'login_channel' first to complete one-time login."
                logger.error(result["error"])
                context.close()
                return result

            # Click Create / Upload button
            logger.info("Looking for Create / Upload button...")
            upload_btn = page.query_selector("#create-icon") or page.query_selector("ytcp-button#upload-button") or page.query_selector("ytcp-icon-button#create-icon")
            if upload_btn:
                upload_btn.click()
                page.wait_for_timeout(2000)
                # Click upload videos in dropdown if visible
                opt_upload = page.query_selector("tp-yt-paper-item#text-item-0") or page.query_selector("ytcp-text-menu#menu ytcp-icon-button")
                if opt_upload:
                    opt_upload.click()
            else:
                page.goto("https://studio.youtube.com/channel/upload", timeout=30000)

            page.wait_for_timeout(3000)

            # File input
            logger.info("Injecting video file into uploader...")
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                file_input = page.wait_for_selector('input[type="file"]', timeout=20000)
            file_input.set_input_files(abs_video)
            logger.info("Video file selected. Waiting for metadata editor dialog...")

            # Wait for title box to appear
            page.wait_for_selector("#title-textarea", timeout=45000)
            page.wait_for_timeout(3000)

            # Set Title
            logger.info(f"Writing Title: {title[:50]}...")
            title_input = page.query_selector("#title-textarea #textbox")
            if title_input:
                title_input.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                title_input.fill(title[:100])
                page.wait_for_timeout(1000)

            # Set Description
            logger.info("Writing Description...")
            desc_input = page.query_selector("#description-textarea #textbox")
            if desc_input:
                desc_input.click()
                desc_input.fill(description[:5000])
                page.wait_for_timeout(1000)

            # Upload Thumbnail
            if abs_thumb and os.path.exists(abs_thumb):
                logger.info(f"Uploading Ultra Thumbnail: {abs_thumb}...")
                thumb_input = page.query_selector('input#file-loader') or page.query_selector('input[type="file"][accept*="image"]')
                if thumb_input:
                    thumb_input.set_input_files(abs_thumb)
                    page.wait_for_timeout(3000)

            # Select "No, it's not made for kids"
            logger.info("Setting 'Not made for kids'...")
            not_for_kids_radio = page.query_selector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]') or page.query_selector('tp-yt-paper-radio-button[name="NOT_MFK"]')
            if not_for_kids_radio:
                not_for_kids_radio.click()
                page.wait_for_timeout(1000)

            # Expand "SHOW MORE" for Tags
            show_more = page.query_selector('ytcp-button#toggle-button') or page.query_selector('div#toggle-button')
            if show_more:
                try:
                    show_more.click()
                    page.wait_for_timeout(1500)
                except Exception:
                    pass

            # Fill Tags
            if tags:
                logger.info("Injecting 500-char tags...")
                tags_input = page.query_selector('#tags-container input') or page.query_selector('input[aria-label="Tags"]')
                if tags_input:
                    tags_input.click()
                    tags_input.fill(tags[:500])
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)

            # Step through wizard: Next -> Next -> Next -> Visibility
            logger.info("Stepping through upload wizard...")
            for step in range(3):
                next_btn = page.query_selector('#next-button')
                if next_btn and next_btn.is_enabled():
                    next_btn.click()
                    page.wait_for_timeout(2000)

            # Visibility Step
            logger.info(f"Setting visibility to '{visibility}'...")
            if visibility.lower() == "public":
                pub_radio = page.query_selector('tp-yt-paper-radio-button[name="PUBLIC"]')
                if pub_radio:
                    pub_radio.click()
            elif visibility.lower() == "unlisted":
                unlisted_radio = page.query_selector('tp-yt-paper-radio-button[name="UNLISTED"]')
                if unlisted_radio:
                    unlisted_radio.click()
            else:
                priv_radio = page.query_selector('tp-yt-paper-radio-button[name="PRIVATE"]')
                if priv_radio:
                    priv_radio.click()

            page.wait_for_timeout(2000)

            # Extract generated video link if present
            link_elem = page.query_selector('a.ytcp-video-info') or page.query_selector('span.ytcp-video-info')
            if link_elem:
                result["url"] = link_elem.get_attribute("href") or link_elem.inner_text()

            # Click Done / Publish
            logger.info("Clicking Done / Publish...")
            done_btn = page.query_selector('#done-button')
            if done_btn and done_btn.is_enabled():
                done_btn.click()
                page.wait_for_timeout(5000)

            logger.success("Video successfully published to YouTube Studio!")
            result["success"] = True

        except Exception as e:
            logger.error(f"Upload flow failed: {e}")
            result["error"] = str(e)
        finally:
            context.close()

    return result
