# Yahoo Fantasy NBA Stats Scraper

This project fetches MLB player data from the Yahoo Fantasy Sports API for the 2025 season and exports it to a CSV file.

## Prerequisites

- Python 3.x
- A Yahoo account with a registered application to get API credentials.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd yahoo-fantasy-mlb
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    - The `.env` file should already contain your `CLIENT_ID` and `CLIENT_SECRET`.

## Usage

Run the main script to start the data fetching process:

```bash
python src/main.py
```

- The first time you run it, you will be prompted to authorize the application by visiting a URL in your browser.
- After authorization, the script will fetch the data and save it to the `data/` directory.
