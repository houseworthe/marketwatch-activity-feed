# Cron Job Setup for MarketWatch Activity Feed

## Prerequisites

1. **Copy firebase-credentials.json** to your work laptop in the same directory as `competition_scraper.py`
2. **Install firebase-admin**: `pip3 install --user --break-system-packages firebase-admin`

## Setting up the Cron Job

1. Open your terminal and run:
   ```bash
   crontab -e
   ```

2. Add this line to run the scraper every 10 minutes:
   ```bash
   */10 * * * * cd /Users/ethanhouseworth/Documents/baird/marketwatch-activity-feed && /usr/bin/python3 competition_scraper.py >> scraper.log 2>&1
   ```

3. Save and exit the editor (`:wq` in vim)

## Manual Test

Test the scraper manually first:
```bash
cd /Users/ethanhouseworth/Documents/baird/marketwatch-activity-feed
python3 competition_scraper.py
```

## Monitoring

Check the logs:
```bash
tail -f /Users/ethanhouseworth/Documents/baird/marketwatch-activity-feed/scraper.log
```

## Important Notes

- The cookie is already hardcoded in the script (line 430)
- The script will scrape all 19 competitors
- Data is pushed to Firebase Realtime Database under `latest_data`
- A backup is always saved to `competition_data.json`
- If firebase-credentials.json is missing, it will only save locally

## Troubleshooting

If the cron job isn't working:
1. Check that Python path is correct: `which python3`
2. Check cron logs: `grep CRON /var/log/system.log`
3. Make sure firebase-credentials.json exists
4. Check scraper.log for errors