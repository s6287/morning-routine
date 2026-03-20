import asyncio
import os
import random
import logging
import time
import requests
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ YOUR CONFIGURATION ============
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
LINKEDIN_COOKIE = os.environ.get("LINKEDIN_COOKIE")

# Telegram Configuration (for Human-in-the-loop)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEARCH_QUERIES = [
    "react developer",
    "frontend developer",
    "full stack developer",
    "junior frontend developer",
    "mern developer",
    "mern stack developer"
]

LOCATIONS = ["India", "Remote"]
MAX_APPLICATIONS = 15
EXPERIENCE_LEVELS = "2%2C3"
DATE_POSTED = "r86400"

# ============ SCREENING QUESTION ANSWERS ============
SCREENING_ANSWERS = {
    "years of experience": "2",
    "total experience": "2",
    "how many years": "2",
    "experience with react": "2",
    "experience with javascript": "2",
    "experience with node": "2",
    "experience with frontend": "2",
    "experience with mern": "2",
    "experience with html": "2",
    "experience with css": "2",
    "experience with typescript": "2",
    "experience with redux": "1",
    "experience with next": "1",
    "experience with tailwind": "2",
    "experience with git": "2",
    "experience with mongodb": "2",
    "experience with express": "2",
    "experience with sql": "1",
    "proficiency": "3",
    "rate your": "3",
    "salary": "400000",
    "expected salary": "400000",
    "notice period": "15",
    "how soon": "15",
    "availability": "15",
    "start date": "15",
    "willing to relocate": "Yes",
    "relocate": "Yes",
    "work remotely": "Yes",
    "remote": "Yes",
    "authorized to work": "Yes",
    "work authorization": "Yes",
    "sponsorship": "No",
    "visa sponsorship": "No",
    "phone": "6287183433",
    "mobile": "6287183433",
    "degree": "Yes",
    "bachelor": "Yes",
    "graduation": "Yes",
    "comfortable": "Yes",
    "willing": "Yes",
    "able to": "Yes",
    "do you have": "Yes",
    "are you": "Yes",
}

async def random_delay(min_sec=2, max_sec=5):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def notify_user_and_wait(page, question_text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured. Skipping unknown question.")
        return None

    try:
        # Take a screenshot of the question
        screenshot_path = f"question_{int(time.time())}.png"
        await page.screenshot(path=screenshot_path)

        # Send to Telegram
        logger.info(f"Sending unknown question to Telegram: {question_text}")
        
        # Send photo first
        with open(screenshot_path, "rb") as photo:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"Unknown Question: {question_text}\n\nPlease reply with the answer."},
                files={"photo": photo}
            )

        # Poll for response (wait up to 5 minutes)
        last_update_id = 0
        # Get initial updates to clear old messages
        updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates").json()
        if updates["result"]:
            last_update_id = updates["result"][-1]["update_id"]

        logger.info("Waiting for user response via Telegram (5 min timeout)...")
        start_time = time.time()
        while time.time() - start_time < 300:
            await asyncio.sleep(5)
            updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}").json()
            if updates["result"]:
                for update in updates["result"]:
                    if "message" in update and "text" in update["message"]:
                        user_answer = update["message"]["text"]
                        logger.info(f"Received answer from Telegram: {user_answer}")
                        return user_answer
        
        logger.warning("Timeout waiting for user response.")
        return None
    except Exception as e:
        logger.error(f"Error in Telegram notification: {e}")
        return None

async def login_linkedin(page, context):
    logger.info("🔐 Logging into LinkedIn...")
    if LINKEDIN_COOKIE:
        logger.info("🍪 Using cookie authentication...")
        await context.add_cookies([{
            "name": "li_at",
            "value": LINKEDIN_COOKIE,
            "domain": ".linkedin.com",
            "path": "/"
        }])
        try:
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
            await random_delay(3, 5)
            if "feed" in page.url or "jobs" in page.url:
                logger.info("✅ LinkedIn login successful (via cookie)!")
                return True
        except Exception as e:
            logger.error(f"Cookie login failed: {e}")
    
    if LINKEDIN_EMAIL and LINKEDIN_PASSWORD:
        logger.info("🔑 Using password authentication...")
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        await page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        await page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
        await page.click('button[type="submit"]')
        await random_delay(5, 8)
        if "feed" in page.url or "jobs" in page.url:
            logger.info("✅ LinkedIn login successful!")
            return True
    
    logger.error("❌ Login failed. Check your credentials or cookie.")
    await page.screenshot(path="login_failed.png")
    return False

async def fill_screening_questions(page):
    try:
        # Handle text and number inputs
        inputs = await page.query_selector_all('input[type="text"], input[type="number"], textarea')
        for input_field in inputs:
            label = await page.evaluate('(el) => { const label = document.querySelector(`label[for="${el.id}"]`); return label ? label.innerText : el.getAttribute("aria-label") || ""; }', input_field)
            label_lower = label.lower()
            
            # Check if we already have an answer
            found_answer = False
            for key, value in SCREENING_ANSWERS.items():
                if key in label_lower:
                    await input_field.fill(value)
                    await random_delay(0.5, 1)
                    found_answer = True
                    break
            
            # If no answer found, ask the user
            if not found_answer:
                user_answer = await notify_user_and_wait(page, label)
                if user_answer:
                    await input_field.fill(user_answer)
                    await random_delay(0.5, 1)

        # Handle select dropdowns
        selects = await page.query_selector_all('select')
        for select in selects:
            label = await page.evaluate('(el) => { const label = document.querySelector(`label[for="${el.id}"]`); return label ? label.innerText : el.getAttribute("aria-label") || ""; }', select)
            options = await select.query_selector_all('option')
            if len(options) > 1:
                # Try to find "Yes" or first positive option
                found_option = False
                for option in options:
                    text = (await option.inner_text()).lower()
                    if text in ["yes", "1", "true", "full-time"]:
                        val = await option.get_attribute("value")
                        await select.select_option(val)
                        found_option = True
                        break
                
                # If no obvious option, ask user
                if not found_option:
                    user_answer = await notify_user_and_wait(page, f"Dropdown: {label}. Options: {[await o.inner_text() for o in options]}")
                    if user_answer:
                        for option in options:
                            if user_answer.lower() in (await option.inner_text()).lower():
                                val = await option.get_attribute("value")
                                await select.select_option(val)
                                break

        # Handle radio buttons
        radios = await page.query_selector_all('fieldset')
        for fieldset in radios:
            legend = await fieldset.query_selector('legend')
            legend_text = (await legend.inner_text()).lower() if legend else ""
            
            # Find "Yes" radio button
            yes_radio = await fieldset.query_selector('label:has-text("Yes"), label:has-text("Confirm")')
            if yes_radio:
                await yes_radio.click()
                await random_delay(0.5, 1)
            else:
                # Ask user for radio button choice
                user_answer = await notify_user_and_wait(page, f"Radio Choice: {legend_text}")
                if user_answer:
                    choice = await fieldset.query_selector(f'label:has-text("{user_answer}")')
                    if choice:
                        await choice.click()
                        await random_delay(0.5, 1)

    except Exception as e:
        logger.warning(f"⚠️ Error filling screening questions: {e}")

async def close_modal(page):
    try:
        close_btn = await page.query_selector('button[aria-label="Dismiss"], button[aria-label="Discard"]')
        if close_btn:
            await close_btn.click()
            await random_delay(1, 2)
            confirm_btn = await page.query_selector('button:has-text("Discard"), button[data-test-dialog-primary-btn]')
            if confirm_btn:
                await confirm_btn.click()
    except:
        pass

async def apply_to_single_job(page):
    try:
        if await page.query_selector('text=Upload resume'):
            logger.info("   📎 Resume upload required. Skipping to avoid errors.")
            await close_modal(page)
            return False

        for step in range(10): 
            await fill_screening_questions(page)
            
            submit_btn = await page.query_selector('button:has-text("Submit application")')
            if submit_btn:
                await submit_btn.click()
                logger.info("   ✅ Application submitted!")
                await random_delay(3, 5)
                done_btn = await page.query_selector('button:has-text("Done")')
                if done_btn: await done_btn.click()
                return True

            next_btn = await page.query_selector('button:has-text("Next"), button:has-text("Review")')
            if next_btn:
                await next_btn.click()
                await random_delay(2, 3)
            else:
                break
        
        await close_modal(page)
        return False
    except Exception as e:
        logger.error(f"   ❌ Error in apply flow: {e}")
        await close_modal(page)
        return False

async def run_automation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        if not await login_linkedin(page, context):
            return

        applied_count = 0
        for query in SEARCH_QUERIES:
            for location in LOCATIONS:
                if applied_count >= MAX_APPLICATIONS: break
                
                logger.info(f"🔍 Searching: '{query}' in {location}")
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_AL=true&f_E={EXPERIENCE_LEVELS}&f_TPR={DATE_POSTED}"
                
                try:
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_selector('.jobs-search-results-list', timeout=30000)
                except Exception as e:
                    logger.error(f"Search page failed to load: {e}")
                    continue

                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 500)")
                    await random_delay(1, 2)

                job_cards = await page.query_selector_all('.job-card-container')
                logger.info(f"Found {len(job_cards)} jobs on this page.")

                for i, card in enumerate(job_cards):
                    if applied_count >= MAX_APPLICATIONS: break
                    
                    try:
                        await card.click()
                        await random_delay(2, 4)
                        
                        apply_btn = await page.query_selector('button.jobs-apply-button')
                        if apply_btn:
                            btn_text = await apply_btn.inner_text()
                            if "Easy Apply" in btn_text:
                                logger.info(f"📝 Applying to job {i+1}...")
                                await apply_btn.click()
                                if await apply_to_single_job(page):
                                    applied_count += 1
                                    logger.info(f"📊 Progress: {applied_count}/{MAX_APPLICATIONS}")
                                    await random_delay(5, 10)
                        else:
                            if await page.query_selector('text=Applied'):
                                logger.info(f"   ⏩ Job {i+1} already applied.")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Error processing job {i+1}: {e}")
                        continue

        logger.info(f"🎉 Automation finished. Total applied: {applied_count}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
