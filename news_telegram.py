import telegram, sys
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

# Create the message body
def formatMessage(entry):
    try: 
        publishedDate   = entry.published
        source          = entry.source.title
        articleTitle    = entry.title
        articleURL      = entry.link
    except Exception as e:
        publishedDate   = "No Date"
        source          = "No Source"
        articleTitle    = "No Title"
        articleURL      = "No URL"

    message = [
        f"_{publishedDate} - {source}_\n"
        f"{articleTitle}\n"
        f"\n"
        f"[See Link]({articleURL})",
    ]

    message_formated = '\n'.join(message)

    return message_formated

def curlMessage(message):
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

def messaging():
    curlMessage("=== NEWS CHANNEL SETUP ===")

    # Set control to blank list
    control = []

    # Fetch the feed
    f = feedparser.parse(FEED_URL)

    message = formatMessage(f.entries[0])

    curlMessage(message)
    # If there are entries in the feed, add entry guid to the control variable
    if f.entries:
        for entries in f.entries:
            message = formatMessage(entries)
            control.append(entries.id)

    #Only wait 30 seconds after initial run.
    time.sleep(30)

    while True:
        # Fetch the feed again, and again, and again...
        f = feedparser.parse(FEED_URL)

        # Compare feed entries to control list.
        # If there are new entries, send a message/push
        # and add the new entry to control variable
        for entries in f.entries:
            if entries.id not in control:

                message = formatMessage(entries)
                curlMessage(message)

                # Add entry guid to the control variable
                control.append(entries.id)

        time.sleep(360)

secrets = load_secrets()
if secrets:
    # Feed URL
    FEED_URL = secrets.get("NEWS_FEED_URL")

    # Telegram settings
    TELEGRAM_BOT_TOKEN = secrets.get("TELEGRAM_NEWS_BOT_TOKEN")
    TELEGRAM_CHAT_ID = secrets.get("TELEGRAM_NEWS_CHAT_ID")

    TELEGRAM_URL = "https://api.telegram.org/bot"+TELEGRAM_BOT_TOKEN+"/sendMessage"

    messaging()
else:
    print("Secrets could not be loaded.")
