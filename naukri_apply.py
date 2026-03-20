import asyncio
import os
import random
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("naukri_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ NAUKRI CONFIGURATION ============
NAUKRI_SID = os.environ.get("NAUKRI_SID")
NAUKRI_NKWAP = os.environ.get("NAUKRI_NKWAP")

SEARCH_QUERIES = ["react developer", "frontend developer", "full stack developer"]
LOCATION = "mumbai"
MAX_APPLICATIONS = 10
EXPERIENCE = "0-2"

async def random_delay(min_sec=2, max_sec=5):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def login_naukri(page, context):
    logger.info("🔐 Logging into Naukri...")
    if not NAUKRI_SID:
        logger.error("NAUKRI_SID not found in environment variables.")
        return False
        
    cookies = [{"name": "nauk_sid", "value": NAUKRI_SID, "domain": ".naukri.com", "path": "/"}]
    if NAUKRI_NKWAP:
        cookies.append({"name": "NKWAP", "value": NAUKRI_NKWAP, "domain": ".naukri.com", "path": "/"})
    
    await context.add_cookies(cookies)
    try:
        await page.goto("https://www.naukri.com/mnjuser/homepage", wait_until="domcontentloaded", timeout=60000)
        await random_delay(3, 5)
        if "homepage" in page.url or "profile" in page.url:
            logger.info("✅ Naukri login successful!")
            return True
        else:
            logger.warning(f"Naukri login might have failed. Current URL: {page.url}")
            await page.screenshot(path="naukri_login_failed.png")
            return False
    except Exception as e:
        logger.error(f"Naukri login error: {e}")
        return False

async def apply_to_naukri_job(page):
    try:
        await random_delay(2, 3)
        # Check if it's an external site application
        external_btn = await page.query_selector('button:has-text("Apply on company site")')
        if external_btn:
            logger.info("   ⏩ External site application. Skipping.")
            return False
            
        # Look for Apply button
        apply_btn = await page.query_selector('button:has-text("Apply"), button.apply-button')
        if not apply_btn:
            # Check if already applied
            if await page.query_selector('text=Applied'):
                logger.info("   ⏩ Already applied.")
                return False
            logger.info("   ⏩ Apply button not found.")
            return False
            
        await apply_btn.click()
        await random_delay(3, 5)
        
        # Check for success message
        if await page.query_selector('text=Applied successfully, text=Success'):
            return True
            
        return True # Assume success if no error
    except Exception as e:
        logger.error(f"   ❌ Error applying to Naukri job: {e}")
        return False

async def apply_to_jobs(page, query, max_apps=5):
    applied_count = 0
    search_url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs-in-{LOCATION}?experience={EXPERIENCE}"
    logger.info(f"🔍 Searching: '{query}'")
    
    try:
        await page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector('.jobTuple, .srp-jobtuple', timeout=30000)
    except Exception as e:
        logger.error(f"Naukri search page failed: {e}")
        return 0
        
    job_cards = await page.query_selector_all('.jobTuple, .srp-jobtuple')
    logger.info(f"Found {len(job_cards)} jobs on Naukri.")
    
    for i, job_card in enumerate(job_cards):
        if applied_count >= max_apps: break
        try:
            # Open job in new tab or click to view
            # Naukri often opens in a new tab, so we need to handle that
            async with page.expect_popup() as popup_info:
                await job_card.click()
            job_page = await popup_info.value
            await stealth_async(job_page)
            
            if await apply_to_naukri_job(job_page):
                applied_count += 1
                logger.info(f"   ✅ Applied! ({applied_count}/{max_apps})")
            
            await job_page.close()
            await random_delay(3, 6)
        except Exception as e:
            logger.warning(f"   ⚠️ Error with job {i+1}: {e}")
            continue
            
    return applied_count

async def main():
    logger.info("🚀 Naukri Auto Apply Bot")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        try:
            if await login_naukri(page, context):
                total_applied = 0
                for query in SEARCH_QUERIES:
                    if total_applied >= MAX_APPLICATIONS: break
                    applied = await apply_to_jobs(page, query, 3)
                    total_applied += applied
                    await random_delay(5, 10)
                logger.info(f"🎉 Naukri DONE! Total applied: {total_applied}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
