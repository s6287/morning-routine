import asyncio
from playwright.async_api import async_playwright
import os
import random
import requests
import time

# ============ YOUR CONFIGURATION ============
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
LINKEDIN_COOKIE = os.environ.get("LINKEDIN_COOKIE") 

# Telegram Configuration
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

LOCATIONS = ["Mumbai", "Remote"]
MAX_APPLICATIONS = 3
EXPERIENCE_LEVELS = "2%2C3" 
DATE_POSTED = "r604800" 

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
    "experience with python": "1",
    "experience with aws": "1",
    "proficiency": "3",
    "rate your": "3",
    "salary": "350000",
    "expected salary": "350000",
    "notice period": "30",
    "how soon": "30",
    "availability": "30",
    "start date": "30",
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

# ============ TELEGRAM HELPER ============

async def notify_user_and_wait(page, question_text):
    """Sends a screenshot to Telegram and waits for your reply"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return None

    try:
        # Take screenshot of the question
        screenshot_path = f"question_{int(time.time())}.png"
        await page.screenshot(path=screenshot_path)

        print(f"📱 Sending question to Telegram: {question_text}")
        
        # Send Photo to Telegram
        with open(screenshot_path, "rb") as photo:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"Question: {question_text}\n\nReply with the answer!"},
                files={"photo": photo}
            )

        # Wait for reply (5 minute timeout)
        last_update_id = 0
        updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates").json()
        if updates["result"]:
            last_update_id = updates["result"][-1]["update_id"]

        start_time = time.time()
        while time.time() - start_time < 300:
            await asyncio.sleep(5)
            updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}").json()
            if updates["result"]:
                for update in updates["result"]:
                    if "message" in update and "text" in update["message"]:
                        return update["message"]["text"]
        return None
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return None

# ============ MAIN CODE ============

async def random_delay(min_sec=1, max_sec=3):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def login_linkedin(page, context):
    print("🔐 Logging into LinkedIn...")
    if LINKEDIN_COOKIE:
        print("🍪 Using cookie authentication...")
        await context.add_cookies([{
            "name": "li_at",
            "value": LINKEDIN_COOKIE,
            "domain": ".linkedin.com",
            "path": "/"
        }])
        await page.goto("https://www.linkedin.com/feed/")
        await random_delay(3, 5)
        if "feed" in page.url or "jobs" in page.url:
            print("✅ LinkedIn login successful!")
            return True
    
    print("🔑 Using password authentication...")
    await page.goto("https://www.linkedin.com/login")
    await page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
    await page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
    await page.click('button[type="submit"]')
    await random_delay(4, 6)
    return "feed" in page.url or "jobs" in page.url

async def fill_screening_questions(page):
    try:
        # Text/Number inputs
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
        for input_field in inputs:
            label = await input_field.get_attribute("aria-label") or ""
            label_lower = label.lower()
            
            found = False
            for key, value in SCREENING_ANSWERS.items():
                if key in label_lower:
                    await input_field.fill(value)
                    found = True
                    break
            
            if not found:
                ans = await notify_user_and_wait(page, label)
                if ans: await input_field.fill(ans)

        # Dropdowns
        selects = await page.query_selector_all('select')
        for select in selects:
            options = await select.query_selector_all('option')
            if len(options) > 1:
                for option in options:
                    if (await option.inner_text()).lower() in ["yes", "1", "true"]:
                        await select.select_option(await option.get_attribute("value"))
                        break

        # Radios
        radios = await page.query_selector_all('input[type="radio"]')
        for radio in radios:
            label = await radio.get_attribute("aria-label") or ""
            if "yes" in label.lower():
                await radio.click()

    except Exception as e:
        print(f"⚠️ Error filling questions: {e}")

async def apply_to_single_job(page, max_steps_allowed=3):
    try:
        await page.wait_for_timeout(2000)
        if await page.query_selector('input[type="file"]'):
            await close_modal(page)
            return None 

        for step in range(max_steps_allowed):
            await fill_screening_questions(page)
            
            submit_btn = await page.query_selector('button:has-text("Submit application")')
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(2000)
                dismiss = await page.query_selector('button[aria-label="Dismiss"]')
                if dismiss: await dismiss.click()
                return True

            next_btn = await page.query_selector('button:has-text("Next"), button:has-text("Review")')
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(1500)
            else:
                break
        await close_modal(page)
        return False
    except:
        await close_modal(page)
        return False

async def close_modal(page):
    try:
        close_btn = await page.query_selector('button[aria-label="Dismiss"], button[aria-label="Discard"]')
        if close_btn:
            await close_btn.click()
            confirm = await page.query_selector('button[data-test-dialog-primary-btn]')
            if confirm: await confirm.click()
    except: pass

async def apply_to_jobs(page, query, location, max_apps=5):
    applied_count = 0
    processed_jobs = 0
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}&location={location}&f_AL=true&f_E={EXPERIENCE_LEVELS}&f_TPR={DATE_POSTED}"

    while applied_count < max_apps and processed_jobs < 15:
        await page.goto(search_url, wait_until='domcontentloaded')
        await page.wait_for_selector('.jobs-search-results-list', timeout=20000)
        
        job_cards = await page.query_selector_all('.job-card-container')
        if processed_jobs >= len(job_cards): break
        
        card = job_cards[processed_jobs]
        processed_jobs += 1
        
        try:
            await card.click()
            await page.wait_for_timeout(2000)
            apply_btn = await page.query_selector('button.jobs-apply-button')
            if apply_btn and "Easy Apply" in (await apply_btn.inner_text()):
                if await apply_to_single_job(page):
                    applied_count += 1
                    print(f"✅ Applied {applied_count}/{max_apps}")
        except: continue
    return applied_count

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        if await login_linkedin(page, context):
            total = 0
            for query in SEARCH_QUERIES:
                for loc in LOCATIONS:
                    if total >= MAX_APPLICATIONS: break
                    total += await apply_to_jobs(page, query, loc, 1)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
