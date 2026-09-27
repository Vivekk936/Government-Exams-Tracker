name: Government Exam Scraper

on:
  schedule:
    - cron: "0 2 * * *"

  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper
        run: python src/scraper.py

      - name: Commit updated CSV
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add data/exams.csv

          git diff --cached --quiet || git commit -m "Update exam data"

          git push