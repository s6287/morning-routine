import asyncio
from playwright.async_api import async_playwright
import os
import random

# ============ YOUR CONFIGURATION ============
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
LINKEDIN_COOKIE = os.environ.get("LINKEDIN_COOKIE")  # li_at cookie for session auth

# Your job search keywords (reduced for testing - uncomment others after test passes)
SEARCH_QUERIES = [
    "react developer",
    # "frontend developer",
    # "full stack developer",
    # "junior frontend developer",
    # "mern developer",
    # "mern stack developer"
]

# Locations to search (reduced for testing)
LOCATIONS = ["Mumbai"]  # Add "Remote" after test passes

# Max total applications (set to 3 for testing, increase to 20-40 after confirmed working)
MAX_APPLICATIONS = 3

# Filters
EXPERIENCE_LEVELS = "2%2C3"  # 2=Entry, 3=Associate/Mid
DATE_POSTED = "r604800"  # Last week (604800 seconds = 7 days)

# ============ SCREENING QUESTION ANSWERS ============
# These answers are used to auto-fill LinkedIn Easy Apply forms
SCREENING_ANSWERS = {
    # Experience questions
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
    "proficiency": "3",  # Scale 1-5, 3 = intermediate
    "rate your": "3",

    # Salary questions
    "salary": "350000",
    "expected salary": "350000",
    "desired salary": "350000",
    "annual salary": "350000",
    "expected ctc": "3.5",
    "desired ctc": "3.5",
    "current ctc": "0",
    "current salary": "0",

    # Notice period / Availability
    "notice period": "30",
    "how soon": "30",
    "availability": "30",
    "start date": "30",
    "days notice": "30",
    "weeks notice": "4",

    # Location / Relocation
    "willing to relocate": "Yes",
    "relocate": "Yes",
    "work remotely": "Yes",
    "remote": "Yes",
    "hybrid": "Yes",
    "on-site": "Yes",
    "onsite": "Yes",
    "work from office": "Yes",
    "mumbai": "Yes",
    "location": "Yes",

    # Work authorization
    "authorized to work": "Yes",
    "work authorization": "Yes",
    "legally authorized": "Yes",
    "eligible to work": "Yes",
    "sponsorship": "No",
    "visa sponsorship": "No",
    "require sponsorship": "No",
    "need sponsorship": "No",

    # Contact details
    "phone": "6287183433",
    "mobile": "6287183433",
    "contact": "6287183433",
    "number": "6287183433",

    # Education
    "degree": "Yes",
    "bachelor": "Yes",
    "graduation": "Yes",
    "graduate": "Yes",

    # General Yes/No
    "comfortable": "Yes",
    "willing": "Yes",
    "able to": "Yes",
    "do you have": "Yes",
    "are you": "Yes",
}

# ============ MAIN CODE ============

async def random_delay(min_sec=1, max_sec=3):
    """Human-like random delay"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def login_linkedin(page, context):
    """Login to LinkedIn using cookie"""
    print("🔐 Logging into LinkedIn...")

    # Use cookie-based authentication (bypasses login security)
    if LINKEDIN_COOKIE:
        print("🍪 Using cookie authentication...")
        await context.add_cookies([{
            "name": "li_at",
            "value": LINKEDIN_COOKIE,
            "domain": ".linkedin.com",
            "path": "/"
        }])

        # Go to LinkedIn feed to verify login
        await page.goto("https://www.linkedin.com/feed/")
        await random_delay(3, 5)

        # Check if logged in
        current_url = page.url
        if "feed" in current_url or "jobs" in current_url or "mynetwork" in current_url:
            print("✅ LinkedIn login successful (via cookie)!")
            return True
        elif "login" in current_url or "authwall" in current_url:
            print("❌ Cookie expired or invalid. Please update LINKEDIN_COOKIE.")
            return False
        else:
            print(f"✅ Logged in! Current URL: {current_url}")
            return True

    # Fallback to password login
    print("🔑 Using password authentication...")
    await page.goto("https://www.linkedin.com/login")
    await random_delay(2, 4)

    await page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
    await random_delay(0.5, 1)
    await page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
    await random_delay(0.5, 1)

    await page.click('button[type="submit"]')
    await random_delay(4, 6)

    current_url = page.url
    if "feed" in current_url or "jobs" in current_url or "mynetwork" in current_url:
        print("✅ LinkedIn login successful!")
        return True
    elif "checkpoint" in current_url or "challenge" in current_url:
        print("❌ LinkedIn security checkpoint detected. Manual verification needed.")
        return False
    else:
        print(f"❌ Login may have failed. Current URL: {current_url}")
        return False


async def fill_screening_questions(page):
    """Fill common screening questions in the Easy Apply modal"""
    try:
        # Find all input fields and try to fill them
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')

        for input_field in inputs:
            try:
                label = await input_field.get_attribute("aria-label") or ""
                label_lower = label.lower()

                # Match and fill based on label
                for key, value in SCREENING_ANSWERS.items():
                    if key in label_lower and value:
                        await input_field.fill(value)
                        await random_delay(0.3, 0.7)
                        break
            except:
                continue

        # Handle dropdown selects
        selects = await page.query_selector_all('select')
        for select in selects:
            try:
                options = await select.query_selector_all('option')
                if len(options) > 1:
                    # Select first non-empty option or "Yes" if available
                    for option in options:
                        text = await option.inner_text()
                        if text.lower() in ["yes", "1", "true"]:
                            value = await option.get_attribute("value")
                            await select.select_option(value)
                            break
            except:
                continue

        # Handle radio buttons (usually Yes/No questions)
        radios = await page.query_selector_all('input[type="radio"]')
        for radio in radios:
            try:
                label = await radio.get_attribute("aria-label") or ""
                if "yes" in label.lower():
                    await radio.click()
                    await random_delay(0.2, 0.5)
            except:
                continue

    except Exception as e:
        print(f"⚠️ Error filling screening questions: {e}")


async def apply_to_single_job(page):
    """Handle the Easy Apply modal and submit application"""
    try:
        await page.wait_for_timeout(2000)

        max_steps = 8
        for step in range(max_steps):
            # Fill any screening questions on this step
            await fill_screening_questions(page)
            await page.wait_for_timeout(500)

            # Try multiple submit button selectors
            submit_selectors = [
                'button[aria-label="Submit application"]',
                'button[aria-label="Submit"]',
                'button:has-text("Submit application")',
                'button:has-text("Submit")'
            ]

            for selector in submit_selectors:
                try:
                    submit_btn = await page.query_selector(selector)
                    if submit_btn and await submit_btn.is_visible():
                        await submit_btn.click()
                        await page.wait_for_timeout(2000)

                        # Close success modal
                        dismiss_btn = await page.query_selector('button[aria-label="Dismiss"]')
                        if dismiss_btn:
                            await dismiss_btn.click()
                        return True
                except:
                    continue

            # Try Review button
            review_btn = await page.query_selector('button[aria-label="Review your application"]')
            if review_btn and await review_btn.is_visible():
                await review_btn.click()
                await page.wait_for_timeout(1500)
                continue

            # Try Next button
            next_selectors = [
                'button[aria-label="Continue to next step"]',
                'button:has-text("Next")',
                'button:has-text("Continue")'
            ]

            clicked_next = False
            for selector in next_selectors:
                try:
                    next_btn = await page.query_selector(selector)
                    if next_btn and await next_btn.is_visible():
                        await next_btn.click()
                        await page.wait_for_timeout(1500)
                        clicked_next = True
                        break
                except:
                    continue

            if clicked_next:
                continue

            # No button found, maybe need to close
            break

        # If we get here, something went wrong - close the modal
        close_selectors = [
            'button[aria-label="Dismiss"]',
            'button[aria-label="Discard"]',
            'button:has-text("Discard")'
        ]
        for selector in close_selectors:
            try:
                close_btn = await page.query_selector(selector)
                if close_btn:
                    await close_btn.click()
                    break
            except:
                continue

        return False

    except Exception as e:
        print(f"⚠️ Error in apply flow: {e}")
        try:
            close_btn = await page.query_selector('button[aria-label="Dismiss"]')
            if close_btn:
                await close_btn.click()
        except:
            pass
        return False


async def apply_to_jobs(page, query, location, max_apps=5):
    """Search and apply to jobs for a specific query and location"""
    applied_count = 0
    processed_jobs = 0

    # Build search URL with all filters
    search_url = (
        f"https://www.linkedin.com/jobs/search/?"
        f"keywords={query.replace(' ', '%20')}"
        f"&location={location}"
        f"&f_AL=true"  # Easy Apply only
        f"&f_E={EXPERIENCE_LEVELS}"  # Experience level
        f"&f_TPR={DATE_POSTED}"  # Posted this week
    )

    print(f"\n🔍 Searching: '{query}' in {location}")

    # Main loop - re-fetch DOM every iteration to avoid stale references
    while applied_count < max_apps and processed_jobs < 20:  # Safety limit of 20 jobs
        # Reload the search page to get fresh DOM (use domcontentloaded for faster/reliable load)
        await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(4000)  # Extra wait for dynamic content

        # Scroll to load jobs
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 300)")
            await page.wait_for_timeout(500)

        # Re-fetch job cards every time (CRITICAL - avoids stale references)
        job_cards = await page.query_selector_all('.job-card-container, .jobs-search-results__list-item')

        if processed_jobs == 0:
            print(f"   Found {len(job_cards)} job listings")

        if processed_jobs >= len(job_cards):
            print(f"   No more jobs to process")
            break

        # Get the specific job card for this iteration
        try:
            job_card = job_cards[processed_jobs]
        except IndexError:
            break

        processed_jobs += 1

        try:
            # Scroll job card into view
            await job_card.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)

            # Click on job to see details
            try:
                await job_card.click(timeout=5000)
            except:
                print(f"   ⏭️ Job {processed_jobs}: Click failed, skipping")
                continue

            await page.wait_for_timeout(2000)

            # Find Easy Apply button
            try:
                easy_apply_btn = await page.wait_for_selector('button.jobs-apply-button', timeout=5000)
            except:
                print(f"   ⏭️ Job {processed_jobs}: No apply button found")
                continue

            if easy_apply_btn:
                button_text = await easy_apply_btn.inner_text()

                if "Easy Apply" in button_text:
                    # Get job title
                    try:
                        title_elem = await page.query_selector('.job-details-jobs-unified-top-card__job-title')
                        job_title = await title_elem.inner_text() if title_elem else f"Job {processed_jobs}"
                    except:
                        job_title = f"Job {processed_jobs}"

                    print(f"   📝 Applying to: {job_title[:50]}...")

                    try:
                        await easy_apply_btn.click(timeout=5000)
                    except:
                        print(f"   ⏭️ Easy Apply click failed, skipping")
                        continue

                    await page.wait_for_timeout(1500)

                    # Complete the application
                    success = await apply_to_single_job(page)

                    if success:
                        applied_count += 1
                        print(f"   ✅ Applied! ({applied_count}/{max_apps})")
                    else:
                        print(f"   ⏭️ Skipped (complex application)")

                    await random_delay(2, 4)

        except Exception as e:
            print(f"   ⚠️ Error with job {processed_jobs}: {str(e)[:50]}")
            continue

    print(f"   📊 Progress: {applied_count}/{max_apps} applications submitted")
    return applied_count


async def main():
    """Main function"""
    print("=" * 50)
    print("🚀 LinkedIn Auto Apply Bot")
    print("=" * 50)
    print(f"📧 Email: {LINKEDIN_EMAIL}")
    print(f"🎯 Max Applications: {MAX_APPLICATIONS}")
    print(f"🔍 Keywords: {', '.join(SEARCH_QUERIES)}")
    print(f"📍 Locations: {', '.join(LOCATIONS)}")
    print("=" * 50)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.set_default_timeout(10000)  # 10 second timeout

        page = await context.new_page()

        # Login to LinkedIn
        logged_in = await login_linkedin(page, context)

        if not logged_in:
            print("\n❌ Could not login to LinkedIn. Exiting.")
            await browser.close()
            return

        # Calculate apps per search combination
        total_searches = len(SEARCH_QUERIES) * len(LOCATIONS)
        apps_per_search = max(1, MAX_APPLICATIONS // total_searches)

        total_applied = 0

        # Apply for each keyword + location combination
        for query in SEARCH_QUERIES:
            for location in LOCATIONS:
                if total_applied >= MAX_APPLICATIONS:
                    break

                remaining = MAX_APPLICATIONS - total_applied
                to_apply = min(apps_per_search, remaining)

                applied = await apply_to_jobs(page, query, location, to_apply)
                total_applied += applied

                print(f"   📊 Progress: {total_applied}/{MAX_APPLICATIONS} total applications")

                # Random delay between searches
                await random_delay(5, 10)

        print("\n" + "=" * 50)
        print(f"🎉 DONE! Total applications submitted: {total_applied}")
        print("=" * 50)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
