# Bizi Playwright Scraper

Python scraper built with **Playwright** for exporting company search results from **bizi.si** to a CSV file.

The script allows you to manually set search filters on the website and then automatically scrapes all paginated results.

---

## Features

- automated scraping with Playwright
- manual filter setup in browser
- automatic pagination through search results
- CSV export
- duplicate filtering
- session login support

---

## Requirements

- Python 3.10+
- Playwright

Install dependencies:

```bash
pip install -r requirements.txt
playwright install


The advanced search on bizi.si requires login, for that you should have a bizi.si account.
run python create_login_state.py and login with your credentials
the script will save the login session to bizi_state.json
now we can run the scraper:
python bizi_scraper.python
the browser will open and you can configure the advanced search to your liking, but beware, you will have to adjust the variables if you want to use anything other than name, date, address, place and phone. When configured click the search button and go to the terminal, click ENTER and the scraper will begin to run
the scraper can run for a while but in the end it will. You can also alter the MAX companies and sleep between pages variables to your liking.
When the scraper finishes the results will appear in bizi_export.csv. 
