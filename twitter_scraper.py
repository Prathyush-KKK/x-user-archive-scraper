import asyncio
import json
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from playwright.async_api import async_playwright

# -----------------------
# CONFIGURATION
# -----------------------
USERNAME = "username"  # Change to any Twitter/X handle
START_DATE = "2018-11-01"
END_DATE = "2025-05-02"
SCROLL_DURATION_SEC = 30
BROWSER_PROFILE_DIR = "chrome_profile"  # Persistent login session
OUTPUT_DIR = "captured_tweets"

# -----------------------
# CORE SCRAPER
# -----------------------

async def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")
    step = relativedelta(months=2)

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = await browser.new_page()

        while start < end:
            range_start = start.strftime("%Y-%m-%d")
            range_end = (start + step).strftime("%Y-%m-%d")
            print(f"\n▶ Scraping from {range_start} to {range_end}...")

            search_query = f"from:{USERNAME} since:{range_start} until:{range_end}"
            collected_data = []

            async def handle_request_finished(request):
                if "SearchTimeline" in request.url and "/graphql/" in request.url:
                    try:
                        response = await request.response()
                        if response and "application/json" in response.headers.get("content-type", ""):
                            json_data = await response.json()
                            collected_data.append({
                                "url": request.url,
                                "method": request.method,
                                "post_data": request.post_data,
                                "response": json_data
                            })
                    except Exception as e:
                        print(f"  [!] Request capture error: {e}")

            page.on("requestfinished", handle_request_finished)

            await page.goto("https://x.com/explore")

            # Wait for search bar and type new query
            await page.wait_for_selector('input[data-testid="SearchBox_Search_Input"]', timeout=15000)
            search_input = await page.query_selector('input[data-testid="SearchBox_Search_Input"]')

            await search_input.fill("")  # Clear existing
            await search_input.type(search_query, delay=50)
            await search_input.press("Enter")

            # Wait for page to load
            await page.wait_for_timeout(5000)

            # Click "Latest"
            await page.click("//span[text()='Latest']")
            await page.wait_for_timeout(3000)


            # Scroll for SCROLL_DURATION_SEC
            print("  ↘ Scrolling...")
            end_time = datetime.now().timestamp() + SCROLL_DURATION_SEC
            while datetime.now().timestamp() < end_time:
                await page.mouse.wheel(0, 2000)
                await page.wait_for_timeout(1000)

            await page.wait_for_timeout(5000)  # Allow trailing requests

            # Save captured data
            filename = f"{USERNAME}_{range_start}_to_{range_end}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(collected_data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ Saved {len(collected_data)} requests to {filepath}")

            # Move to next date range
            start += step

        print("\n✅ All ranges complete.")
        await browser.close()

# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    asyncio.run(run())
