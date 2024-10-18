# Coursebook Scraper

This script will scrape coursebook and grab all the course data. You will be asked to log in with your netID and password (this only works per 100 requests, so you may need to refresh the token halfway through scraping).

## Setup

Go to https://googlechromelabs.github.io/chrome-for-testing/#stable to download the latest version of ChromeDriver. Copy the executable to the root folder of this project. You may also need the latest version of Chrome; make sure your chrome is updated.

Then, run the code with:

```
python main.py <semester>
```

Replace `<semester>` with the term in the format specified by Coursebook. It should be a 2-digit year number followed by either 'f' or 's', for "fall" or "spring".
