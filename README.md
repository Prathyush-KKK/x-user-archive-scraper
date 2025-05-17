# x-user-archive-scraper

> Download and archive a complete Twitter/X user timeline using browser automation — no API key required.

**x-archive-scraper** is a Python script that automates a logged-in browser session to scroll through a user's entire public tweet history on X (formerly Twitter), captures the underlying `SearchTimeline` GraphQL responses, and saves all tweet data in raw JSON format. It uses [Playwright](https://playwright.dev/python/) under the hood.



## 🔍 Why this project?

Twitter/X has:
- Deprecated free and public APIs
- Imposed strict rate limits on 3rd-party tools
- Limited access even for researchers and developers

This project bypasses these limitations by leveraging the browser's **actual network activity** — just like a human would — to download a user's full tweet history.



## ✅ Features

- Uses your logged-in session — **no API keys required**
- Captures **all tweets** (including replies, retweets, and quote tweets)
- Extracts from **`SearchTimeline` GraphQL requests** for maximum accuracy
- Saves each date range's raw response as JSON
- Scrolls the page automatically for reliable capture
- Works across long date ranges (e.g., entire account history)
- Supports persistent session storage (only login once)



## 📦 Requirements

- Python 3.8+
- Playwright

Install dependencies:

```bash
pip install playwright python-dateutil
playwright install
```

## 🚀 Usage

```bash
python twitter_scraper.py
```

When first run:
* A browser window opens
* Login to your X (Twitter) account
* That session is saved for future use

Scraped tweet data will be saved in the captured_tweets/ folder.


## ⚙️ Configuration
in ```twitter_scraper.py``` modify:

```py
USERNAME = "username"      # Twitter username
START_DATE = "2018-11-01"      # Start of scraping period
END_DATE = "2025-05-02"        # End of scraping period
SCROLL_DURATION_SEC = 30       # Scroll time per search, recommended 30s- if user's tweet frequency is high increase this time
```


## 📁 Output Format
Each file corresponds to a 2-month period and contains raw GraphQL responses: (can be modified in code according to tweet frequency of the user)
```
captured_tweets/
  username_2018-11-01_to_2019-01-31.json
  username_2019-02-01_to_2019-04-30.json
  ...
```

Each JSON File contains:
```
[
  {
    "url": "...SearchTimeline...",
    "method": "GET",
    "post_data": null,
    "response": {
      "data": { ... },
      "timeline": { ... }
    }
  }
]
```

## ⚙️ Parser
A parser script is included to compile important fields from the user's tweet data and reduce the total garbage data.
The data retained includes:
```
tweet_id: The unique ID of the tweet (from rest_id).
user_screen_name: The screen name of the tweet author.
user_name: The display name of the tweet author.
user_id: The unique ID of the tweet author.
created_at: The timestamp when the tweet was created.
full_text: The complete text content of the tweet.
language: The language of the tweet (e.g., "en", "hi").
favorite_count: Number of likes the tweet received.
retweet_count: Number of retweets.
reply_count: Number of replies to this tweet.
quote_count: Number of times this tweet has been quoted.
source: The application used to post the tweet (e.g., "Twitter Web App").
is_reply: Boolean, true if this tweet is a reply to another.
reply_to_screen_name: If is_reply is true, the screen name of the user being replied to.
reply_to_tweet_id: If is_reply is true, the ID of the tweet being replied to.
is_quote: Boolean, true if this tweet quotes another tweet.
quoted_tweet_details: If is_quote is true, a dictionary containing:
tweet_id: ID of the quoted tweet.
user_screen_name: Screen name of the quoted tweet's author.
user_name: Display name of the quoted tweet's author.
created_at: Timestamp of the quoted tweet.
full_text: Text content of the quoted tweet.
favorite_count, retweet_count, reply_count, quote_count for the quoted tweet.
entities: A dictionary containing:
hashtags: List of hashtag texts.
user_mentions: List of mentioned user screen names.
urls: List of expanded URLs found in the twee
```
Outputs into:
```data_combined_tweets.json```

## 📌 Limitations
* Private tweets or deleted content will not be accessible.
* To avoid being rate-limited, the script scrolls slowly (~30s per range).
* You must remain logged in, or reauthenticate once when prompted.

## 🛡️ Legal Disclaimer
This tool is intended for personal archiving, research, and compliance purposes only. Use responsibly and in accordance with [Twitter's Terms of Service](https://twitter.com/en/tos).

## 💬 Contributions
PRs welcome! If you hit a snag, feel free to open an issue.


## 📄 License
MIT License
```MIT License

Copyright (c) 2025 Prathyush-KKK

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
