from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import csv
import time

STATE_FILE = "bizi_state.json"
START_URL = "https://www.bizi.si/napredno-iskanje/"
OUT_CSV = "bizi_export.csv"

MAX_COMPANIES = 100000
SLEEP_BETWEEN_PAGES = 0.1

ROW_SEL = "div.row.b-table-row"

NAME_SEL = "div.b-table-cell-title"
NASLOV_SEL = "div.col.b-table-cell:nth-child(3)"
KRAJ_SEL = "div.col.b-table-cell:nth-child(4)"
PHONE_SEL = "div.col.b-table-cell:nth-child(5)"
DATE_SEL = "div.col.b-table-cell:nth-child(6)"
ABOUT_SEL = "div.col.b-table-cell:nth-child(7)"

ACTIVE_PAGE_SEL = "a.b-page-link.b-active"


def clean(s: str) -> str:
    return " ".join((s or "").split())


def safe_text(locator) -> str:
    try:
        if locator.count() == 0:
            return ""
        return clean(locator.first.inner_text())
    except Exception:
        return ""


def wait_results(page):
    # počakaj, da se vrstice pokažejo (po postbacku)
    page.wait_for_timeout(200)
    page.wait_for_selector(ROW_SEL, timeout=20000)


def click_next(page) -> bool:

    active = page.locator(ACTIVE_PAGE_SEL)
    if active.count() == 0:
        return False

    cur_txt = clean(active.first.inner_text())
    if not cur_txt.isdigit():
        return False

    cur = int(cur_txt)
    nxt = cur + 1

    target = page.locator(f"a.b-page-link:has-text('{nxt}')")
    if target.count() > 0:
        target.first.click()
        page.wait_for_load_state("networkidle")
        wait_results(page)
        return True

    dots = page.locator("a.b-page-link:has-text('...')")
    if dots.count() > 0:
        dots.last.click()
        page.wait_for_load_state("networkidle")
        wait_results(page)

        target2 = page.locator(f"a.b-page-link:has-text('{nxt}')")
        if target2.count() > 0:
            target2.first.click()
            page.wait_for_load_state("networkidle")
            wait_results(page)
            return True

    return False


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # za debug: False
    context = browser.new_context(
        storage_state=STATE_FILE,
        viewport={"width": 1600, "height": 1000},
        user_agent="Mozilla/5.0",
    )
    page = context.new_page()
    page.goto("https://www.bizi.si/", wait_until="networkidle")

    print("\nset the filters and click poišči'.")
    print("Ko vidiš tabelo rezultatov, pritisni Enter...\n")
    input()

    try:
        wait_results(page)
    except PWTimeout:
        print("No results found, check if you are on the page 8832 with the results")
        browser.close()
        raise SystemExit(1)

    seen = set()
    total = 0
    page_no = 1

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ime",
                "naslov",
                "kraj_posta",
                "telefon",
                "datum_vpisa",
                "dejavnost",
            ],
        )
        writer.writeheader()

        while total < MAX_COMPANIES:
            rows = page.locator(ROW_SEL)
            count = rows.count()

            if count == 0:
                print(
                    "No more results (0 rows). Possible: pagination failed or you got a block/redirect."
                )
                print("Current URLL:", page.url)
                break

            added = 0
            for i in range(count):
                if total >= MAX_COMPANIES:
                    break

                row = rows.nth(i)

                ime = safe_text(row.locator(NAME_SEL))
                naslov = safe_text(row.locator(NASLOV_SEL))
                kraj = safe_text(row.locator(KRAJ_SEL))
                telefon = safe_text(row.locator(PHONE_SEL))
                datum = safe_text(row.locator(DATE_SEL))
                dejavnost = safe_text(row.locator(ABOUT_SEL))

                if not ime:
                    continue

                key = (ime, naslov, kraj, telefon, datum, dejavnost)
                if key in seen:
                    continue
                seen.add(key)

                writer.writerow(
                    {
                        "ime": ime,
                        "naslov": naslov,
                        "kraj_posta": kraj,
                        "telefon": telefon,
                        "datum_vpisa": datum,
                        "dejavnost": dejavnost,
                    }
                )

                total += 1
                added += 1

            print(f"Stran {page_no}: dodano {added}, skupaj {total}")

            if total >= MAX_COMPANIES:
                break

            time.sleep(SLEEP_BETWEEN_PAGES)

            # --- paginacija naprej ---
            moved = click_next(page)
            if not moved:
                print("End of pagination (can't find the next page).")
                break

            page_no += 1

    browser.close()

print(f"\nFinished, added to: {OUT_CSV}")
