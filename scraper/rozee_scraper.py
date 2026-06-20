import asyncio
from playwright.async_api import async_playwright
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

SEEDS = ["python", "sql", "data analyst", "software engineer",
    "machine learning", "devops", "react", "javascript",
    "power bi", "cloud", "cybersecurity", "mobile developer",
    "marketing", "sales", "finance", "accounting", "hr",
    "manager", "engineer", "officer"
]

CUTOFF_DATE = datetime.now() - timedelta(days=90)  # 3 months back

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%b %d, %Y")
    except:
        return None

async def scrape_page(page, keyword):
    job_cards = await page.query_selector_all(".job")
    count = 0
    hit_cutoff = False

    for card in job_cards:
        try:
            title_el = await card.query_selector("h3.s-18 a bdi")
            if not title_el:
                continue

            title = await title_el.inner_text()
            if not title or title == "N/A":
                continue

            company_el = await card.query_selector(".cname bdi a")
            location_els = await card.query_selector_all(".cname bdi a")
            skill_els = await card.query_selector_all("span.label.label-default")
            url_el = await card.query_selector("h3.s-18 a")
            date_el = await card.query_selector(".jfooter .col-md-12 span:first-child")
            exp_el = await card.query_selector(".func-area-drn")
            salary_el = await card.query_selector(".jfooter span span")

            company = await company_el.inner_text() if company_el else "N/A"
            location = await location_els[1].inner_text() if len(location_els) > 1 else "N/A"
            skills = ", ".join([await s.inner_text() for s in skill_els])
            url = await url_el.get_attribute("href") if url_el else "N/A"
            experience = await exp_el.inner_text() if exp_el else "N/A"
            salary = await salary_el.inner_text() if salary_el else "N/A"

            # get posted date
            date_text = ""
            if date_el:
                date_text = await date_el.inner_text()
                date_text = date_text.strip()

            posted_date = parse_date(date_text)

            # stop if older than 3 months
            if posted_date and posted_date < CUTOFF_DATE:
                hit_cutoff = True
                break

            cursor.execute("""
                INSERT INTO jobs (title, company, location, skills, job_url, experience, salary, posted_date, keyword)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_url) DO NOTHING
            """, (title, company.strip(), location.strip(), skills, url, experience, salary, date_text, keyword))
            count += 1

        except Exception as e:
            print(f"Error: {e}")
            continue

    conn.commit()
    return count, hit_cutoff

async def scrape_rozee():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        keyword_queue = list(SEEDS)
        scraped_keywords = set()
        total = 0

        while keyword_queue:
            keyword = keyword_queue.pop(0)
            if keyword in scraped_keywords:
                continue

            scraped_keywords.add(keyword)
            print(f"\nScraping keyword: '{keyword}'")

            for page_num in range(1, 21):  # up to 20 pages per keyword
                url = f"https://www.rozee.pk/job/jsearch/q/{keyword.replace(' ', '+')}/fpn/{page_num}"
                await page.goto(url)
                await page.wait_for_timeout(4000)

                count, hit_cutoff = await scrape_page(page, keyword)
                print(f"  Page {page_num}: {count} jobs saved")

                if hit_cutoff:
                    print(f"  Hit 3-month cutoff, moving to next keyword")
                    break

                if count == 0:
                    print(f"  No jobs found, moving to next keyword")
                    break

        print(f"\nTotal keywords scraped: {len(scraped_keywords)}")
        await browser.close()

asyncio.run(scrape_rozee())