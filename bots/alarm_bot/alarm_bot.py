import time
import json
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# Point exactly to where the JSON file lives in your new folder structure
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "alarm_config.json")

def read_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {"time": "07:00", "active": False}

def get_news_headlines():
    # Fetching the top news via Google's RSS feed
    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        # Grab the top 3 headlines
        headlines = []
        for item in root.findall('./channel/item')[:3]:
            # Clean up the title (Google appends the publisher at the end)
            raw_title = item.find('title').text
            clean_title = raw_title.rsplit(' - ', 1)[0]
            headlines.append(clean_title)
            
        return headlines
    except Exception as e:
        print(f"News fetch error: {e}")
        return ["I could not retrieve the news at this time."]

def trigger_alarm():
    print("ALARM TRIGGERED!")
    
    # 1. The Wake-Up Sequence
    subprocess.run(['termux-tts-speak', "Alarm triggered. Alarm triggered."])
    time.sleep(1) 
    
    # 2. The Greeting
    now = datetime.now()
    subprocess.run(['termux-tts-speak', f"Good morning. It is {now.strftime('%I:%M %p')}."])
    time.sleep(1)
    
    # 3. The News
    subprocess.run(['termux-tts-speak', "Here are the top headlines for today."])
    headlines = get_news_headlines()
    
    for headline in headlines:
        subprocess.run(['termux-tts-speak', headline])
        time.sleep(1) # Brief pause between each headline

def main():
    print("🤖 Synapse Alarm Daemon Started...")
    has_triggered_today = False
    last_trigger_date = None

    while True:
        now = datetime.now()
        current_date = now.date()
        current_time_str = now.strftime("%H:%M")
        
        # Reset the trigger lock at midnight so it fires again the next day
        if last_trigger_date != current_date:
            has_triggered_today = False
            last_trigger_date = current_date

        config = read_config()

        if config.get("active") and not has_triggered_today:
            if current_time_str == config.get("time"):
                trigger_alarm()
                has_triggered_today = True

        # Check every 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    main()