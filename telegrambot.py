import telegram, sys
import feedparser
import time
import json
import requests


# Feed URL
FEED_URL = '<YOUR_FEED>'

# Telegram settings
TELEGRAM_BOT_TOKEN = '<BOT_TOKEN>'
TELEGRAM_CHAT_ID = '<CHAT_ID>'

TELEGRAM_URL = "https://api.telegram.org/bot"+TELEGRAM_BOT_TOKEN+"/sendMessage"

# Customize the message title
MESSAGE_TITLE = '<TITLE>'

# Create the message body
def formatMessage(entry):
    message = [
        f"**{MESSAGE_TITLE}**",
        f"",
        f"{entry.title}",
        f"",
        f"{entry.link}",
    ]

    message = '\n'.join(message)

    return message


def curlMessage(message):
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(TELEGRAM_URL, data=payload)
    print(response.status_code)
    print(response)

def messaging():
    # Set control to blank list
    control = []

    # Fetch the feed
    f = feedparser.parse(FEED_URL)

    # If there are entries in the feed, add entry guid to the control variable
    if f.entries:
        for entries in f.entries:
            message = formatMessage(entries)
            curlMessage(message)

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

        time.sleep(59)

messaging()
