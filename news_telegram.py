import telegram
import sys
import feedparser
import time
import json
import requests
import datetime

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"

def load_secrets(filename='secrets.json'):
    try:
        with open(filename, 'r') as file:
            secrets = json.load(file)
        return secrets
    except FileNotFoundError:
        print(f"{filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding {filename}. Please check the file format.")
        return None
    except Exception as e:
        print(f"Unexpected error loading secrets: {e}")
        return None

# Create the message body
def formatMessage(entry):
    try: 
        publishedDate   = entry.get('published', 'No Date')
        source          = entry.get('source', {}).get('title', 'No Source')
        articleTitle    = entry.get('title', 'No Title')
        articleURL      = entry.get('link', 'No URL')
    except Exception as e:
        publishedDate   = "No Date"
        source          = "No Source"
        articleTitle    = "No Title"
        articleURL      = "No URL"
        print(f"Error formatting message: {e}")

    message = [
        f"_{publishedDate} - {source}_\n"
        f"{articleTitle}\n"
        f"\n"
        f"[See Link]({articleURL})",
    ]

    message_formated = '\n'.join(message)

    return message_formated

def curlMessage(message):
    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(TELEGRAM_URL, data=payload)

        current_time = datetime.datetime.now().strftime(FORMAT_DATE)

        message = (
            f"{current_time}\n"
            f"{response.status_code} HTTP\n"
        )

        print(message)
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
    except Exception as e:
        print(f"Unexpected error in curlMessage: {e}")

def messaging():
    try:
        curlMessage("=== NEWS CHANNEL SETUP ===")

        # Set control to blank list
        control = []

        # Fetch the feed
        f = feedparser.parse(FEED_URL)

        if not f.entries:
            print("No entries found in the feed.")
            return

        message = formatMessage(f.entries[0])

        curlMessage(message)
        # If there are entries in the feed, add entry guid to the control variable
        if f.entries:
            for entry in f.entries:
                message = formatMessage(entry)
                curlMessage(message)
                control.append(entry.id)

        # Only wait 30 seconds after initial run.
        time.sleep(30)

        while True:
            # Fetch the feed again, and again, and again...
            f = feedparser.parse(FEED_URL)

            # Compare feed entries to control list.
            # If there are new entries, send a message/push
            # and add the new entry to control variable
            for entry in f.entries:
                if entry.id not in control:
                    message = formatMessage(entry)
                    curlMessage(message)

                    # Add entry guid to the control variable
                    control.append(entry.id)

            time.sleep(360)
    except Exception as e:
        print(f"Unexpected error in messaging loop: {e}")

secrets = load_secrets()
if secrets:
    try:
        # Feed URL
        FEED_URL = secrets.get("NEWS_FEED_URL")
        if not FEED_URL:
            raise ValueError("NEWS_FEED_URL not found in secrets.")

        # Telegram settings
        TELEGRAM_BOT_TOKEN = secrets.get("TELEGRAM_NEWS_BOT_TOKEN")
        TELEGRAM_CHAT_ID = secrets.get("TELEGRAM_NEWS_CHAT_ID")

        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            raise ValueError("Telegram settings not properly configured in secrets.")

        TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        messaging()
    except ValueError as ve:
        print(f"Configuration error: {ve}")
    except Exception as e:
        print(f"Unexpected error in initialization: {e}")
else:
    print("Secrets could not be loaded.")
