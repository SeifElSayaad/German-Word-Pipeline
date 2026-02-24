# 🇩🇪 German Word Extraction & Aggregation Pipeline

[![Daily Scrape](https://github.com/YOUR_USERNAME/german-word-pipeline/actions/workflows/daily_scrape.yml/badge.svg)](https://github.com/YOUR_USERNAME/german-word-pipeline/actions/workflows/daily_scrape.yml)

> A fully automated pipeline that scrapes Deutsche Welle daily, extracts advanced German vocabulary (B1–C1), translates it to English, and exports Anki-ready flashcard CSVs — all without touching your computer.

---

## ✨ Features

| Feature           | Details                                             |
| ----------------- | --------------------------------------------------- |
| 🕸️ **Scraper**    | Deutsche Welle "Nachrichten leicht" articles        |
| 🔍 **Filter**     | Removes A1/A2 basic words, keeps B1–C1 vocabulary   |
| 🌐 **Translator** | Free MyMemory API (de → en), no API key needed      |
| 📄 **CSV Export** | Anki-compatible format with context sentences       |
| ⚙️ **CI/CD**      | GitHub Actions — runs every day at 07:00 Cairo time |

---

## 📁 Project Structure

```
german-word-pipeline/
├── .github/workflows/daily_scrape.yml   # GitHub Actions automation
├── src/
│   ├── scraper.py        # Scrape DW articles
│   ├── filter.py         # Filter advanced words
│   ├── translator.py     # Free translation API
│   ├── csv_exporter.py   # Export to Anki CSV
│   └── main.py           # Pipeline orchestrator
├── data/
│   ├── basic_words_a1a2.txt   # A1/A2 wordlist for filtering
│   └── output/                # Generated CSVs live here
├── tests/
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/german-word-pipeline.git
cd german-word-pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python src/main.py
```

The CSV will appear in `data/output/german_words_YYYY-MM-DD.csv`.

---

## 🃏 Importing into Anki

1. Open Anki → `File` → `Import`
2. Select the generated `.csv` file
3. Set **Field Separator** to `Comma`
4. Map fields:
   - Field 1 → **Front** (German word)
   - Field 2 → **Back** (English translation)
   - Field 3 → **Extra** (Context sentence)
5. Click **Import**

---

## ⚙️ GitHub Actions Setup

The pipeline runs automatically every day at **07:00 Cairo time (05:00 UTC)**.

To enable:

1. Push this repo to GitHub
2. Go to **Settings → Actions → General** → enable "Read and write permissions"
3. The workflow will run automatically — check the **Actions** tab

You can also trigger it manually anytime from the Actions tab → **"Run workflow"**.

---

## 🔧 Configuration

Edit `src/main.py` to adjust:

- **Max articles per run** (`MAX_ARTICLES`)
- **Min word length** (`MIN_WORD_LENGTH`)
- **Max words to translate per run** (`MAX_TRANSLATE`)

---

## 📊 Output Format

```csv
German,English,Context,Date
Verantwortung,responsibility,"Die Regierung übernimmt die Verantwortung.",2024-02-24
Bevölkerung,population,"Die Bevölkerung wächst schnell.",2024-02-24
```
