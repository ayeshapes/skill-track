import asyncio
from playwright.async_api import async_playwright
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

async def scrape_rozee():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.rozee.pk/job/jsearch/q/technology")
        await page.wait_for_timeout(5000)

        job_cards = await page.query_selector_all(".job")
        print(f"Found {len(job_cards)} jobs")

        for card in job_cards:
            try:
                title_el = await card.query_selector("h3.s-18 a bdi")
                company_el = await card.query_selector(".cname bdi a")
                location_els = await card.query_selector_all(".cname bdi a")
                skill_els = await card.query_selector_all("span.label.label-default")
                url_el = await card.query_selector("h3.s-18 a")

                title = await title_el.inner_text() if title_el else "N/A"
                if title == "N/A":
                    continue

                company = await company_el.inner_text() if company_el else "N/A"
                location = await location_els[1].inner_text() if len(location_els) > 1 else "N/A"
                skills = ", ".join([await s.inner_text() for s in skill_els])
                url = await url_el.get_attribute("href") if url_el else "N/A"

                print(f"{title} | {company} | {location}")

                cursor.execute("""
                    INSERT INTO jobs (title, company, location, skills, job_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (job_url) DO NOTHING
                """, (title, company, location, skills, url))

            except Exception as e:
                print(f"Error: {e}")
                continue

        conn.commit()
        print("Done! All jobs saved.")
        await browser.close()

asyncio.run(scrape_rozee())