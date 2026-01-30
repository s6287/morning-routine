import asyncio
from playwright.async_api import async_playwright
import os
import random

# ============ NAUKRI CONFIGURATION ============
NAUKRI_SID = os.environ.get("NAUKRI_SID")
NAUKRI_NKWAP = os.environ.get("NAUKRI_NKWAP")

# Job search keywords
SEARCH_QUERIES = [
    "react developer",
    "frontend developer",
    "full stack developer",
    "mern developer",
]

# Location
LOCATION = "mumbai"

# Max applications per run
MAX_APPLICATIONS = 10

# Experience filter (0-2 years)
EXPERIENCE = "0-2"


async def random_delay(min_sec=1, max_sec=3):
    """Human-like random delay"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def login_naukri(page, context):
    """Login to Naukri using cookies"""
    print("🔐 Logging into Naukri...")

    if not NAUKRI_SID:
        print("❌ NAUKRI_SID cookie not found")
        return False

    # Set cookies
    cookies = [
        {
            "name": "nauk_sid",
            "value": NAUKRI_SID,
            "domain": ".naukri.com",
            "path": "/"
        }
    ]

    if NAUKRI_NKWAP:
        cookies.append({
            "name": "NKWAP",
            "value": NAUKRI_NKWAP,
            "domain": ".naukri.com",
            "path": "/"
        })

    await context.add_cookies(cookies)

    # Go to Naukri homepage to verify login
    await page.goto("https://www.naukri.com/mnjuser/homepage")
    await random_delay(3, 5)

    # Check if logged in
    current_url = page.url
    if "homepage" in current_url or "profile" in current_url:
        print("✅ Naukri login successful!")
        return True
    elif "login" in current_url or "register" in current_url:
        print("❌ Naukri cookie expired. Please update cookies.")
        return False
    else:
        # Try to find user element
        user_elem = await page.query_selector('.nI-gNb-drawer__bars, .view-profile-wrapper')
        if user_elem:
            print("✅ Naukri login successful!")
            return True
        print(f"⚠️ Unclear login status. URL: {current_url}")
        return True  # Proceed anyway


async def apply_to_naukri_job(page):
    """Apply to a single Naukri job"""
    try:
        await page.wait_for_timeout(2000)

        # Look for Apply button (not external apply)
        apply_selectors = [
            'button:has-text("Apply")',
            'button.apply-button',
            'button[class*="apply"]',
            'a:has-text("Apply on company site")'  # Skip these
        ]

        # Check if it's "Apply on company site" - skip these
        external_btn = await page.query_selector('button:has-text("Apply on company site"), a:has-text("Apply on company site")')
        if external_btn:
            return None  # External application

        # Find regular Apply button
        apply_btn = await page.query_selector('button:has-text("Apply"), button.apply-button')
        if not apply_btn:
            return None

        # Check if already applied
        applied_text = await page.query_selector('text="Already Applied"')
        if applied_text:
            return None

        await apply_btn.click()
        await page.wait_for_timeout(2000)

        # Check for success
        success_selectors = [
            'text="Application Sent"',
            'text="Successfully Applied"',
            'text="applied successfully"',
            '.apply-success'
        ]

        for selector in success_selectors:
            success = await page.query_selector(selector)
            if success:
                return True

        # Check if there's a form/questionnaire
        form = await page.query_selector('form, .questionnaire, .apply-form')
        if form:
            # Complex application with form
            close_btn = await page.query_selector('button:has-text("Close"), button.close, .close-btn')
            if close_btn:
                await close_btn.click()
            return None

        return True  # Assume success if no error

    except Exception as e:
        print(f"⚠️ Error applying: {e}")
        return False


async def apply_to_jobs(page, query, max_apps=5):
    """Search and apply to jobs on Naukri"""
    applied_count = 0
    processed_jobs = 0

    # Build search URL
    search_query = query.replace(' ', '-')
    search_url = f"https://www.naukri.com/{search_query}-jobs-in-{LOCATION}?experience={EXPERIENCE}"

    print(f"\n🔍 Searching: '{query}' in {LOCATION}")

    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
    await page.wait_for_timeout(3000)

    # Scroll to load jobs
    for _ in range(3):
        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(500)

    # Find job cards
    job_cards = await page.query_selector_all('.jobTuple, .srp-jobtuple, article.jobTuple')
    print(f"   Found {len(job_cards)} job listings")

    for job_card in job_cards:
        if applied_count >= max_apps:
            break

        processed_jobs += 1

        try:
            # Get job title
            title_elem = await job_card.query_selector('.title, .jobTitle, a.title')
            job_title = await title_elem.inner_text() if title_elem else f"Job {processed_jobs}"

            # Click on job to see details
            await job_card.click()
            await page.wait_for_timeout(2000)

            print(f"   📝 Checking: {job_title[:40]}...")

            # Try to apply
            result = await apply_to_naukri_job(page)

            if result is True:
                applied_count += 1
                print(f"   ✅ Applied! ({applied_count}/{max_apps})")
            elif result is None:
                print(f"   ⏭️ Skipped (external/already applied)")
            else:
                print(f"   ⏭️ Skipped (couldn't apply)")

            await random_delay(2, 4)

        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:40]}")
            continue

    print(f"   📊 Progress: {applied_count}/{max_apps} applications")
    return applied_count


async def main():
    """Main function"""
    print("=" * 50)
    print("🚀 Naukri Auto Apply Bot")
    print("=" * 50)
    print(f"🎯 Max Applications: {MAX_APPLICATIONS}")
    print(f"🔍 Keywords: {', '.join(SEARCH_QUERIES)}")
    print(f"📍 Location: {LOCATION}")
    print("=" * 50)

    page = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.set_default_timeout(15000)

        page = await context.new_page()

        try:
            # Login to Naukri
            logged_in = await login_naukri(page, context)

            if not logged_in:
                print("\n❌ Could not login to Naukri. Exiting.")
                await browser.close()
                return

            apps_per_query = max(1, MAX_APPLICATIONS // len(SEARCH_QUERIES))
            total_applied = 0

            for query in SEARCH_QUERIES:
                if total_applied >= MAX_APPLICATIONS:
                    break

                remaining = MAX_APPLICATIONS - total_applied
                to_apply = min(apps_per_query, remaining)

                applied = await apply_to_jobs(page, query, to_apply)
                total_applied += applied

                print(f"   📊 Total: {total_applied}/{MAX_APPLICATIONS}")
                await random_delay(5, 10)

            print("\n" + "=" * 50)
            print(f"🎉 DONE! Total Naukri applications: {total_applied}")
            print("=" * 50)

        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            if page:
                await page.screenshot(path="naukri_error.png", full_page=True)
                print("📸 Screenshot saved: naukri_error.png")
            raise

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
