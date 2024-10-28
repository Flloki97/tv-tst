import requests
from bs4 import BeautifulSoup
import re
import time
import os

# Dictionary of channels with page URLs and names
channels = {
    "Channel 1": "https://ok.ru/live/7727145950884",
    "Channel 2": "https://ok.ru/live/7727186386596"
}

# Pattern to identify the .m3u8 link in the page's HTML
m3u8_pattern = re.compile(r"https://vsd\d+\.mycdn\.me/hls/\d+\.m3u8[^\"\']*")

# Path to the .m3u file
m3u_file_path = "playlist.m3u"

# Function to get the latest stream URL for a channel
def get_latest_stream_url(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        html_content = response.text

        # Search for the .m3u8 link in the HTML content
        match = m3u8_pattern.search(html_content)
        if match:
            return match.group(0)
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
    return None

# Function to update the .m3u file
def update_m3u_file(channel_urls):
    with open(m3u_file_path, "w") as file:
        file.write("#EXTM3U\n")
        for channel_name, url in channel_urls.items():
            file.write(f"#EXTINF:-1,{channel_name}\n{url}\n")
    print("M3U file updated with new stream URLs.")

# Main loop to check for updates for all channels and refresh the .m3u file if needed
def monitor_stream():
    last_urls = {name: None for name in channels}

    while True:
        channel_urls = {}
        for name, page_url in channels.items():
            current_url = get_latest_stream_url(page_url)
            if current_url and current_url != last_urls[name]:
                channel_urls[name] = current_url
                last_urls[name] = current_url
            elif last_urls[name]:
                # Keep the last known good URL if there's no update
                channel_urls[name] = last_urls[name]

        if channel_urls:
            update_m3u_file(channel_urls)
        else:
            print("No new stream URLs found or URLs have not changed.")

        # Check every 5 minutes (adjust as needed)
        time.sleep(300)

if __name__ == "__main__":
    # Ensure the .m3u file exists initially
    if not os.path.exists(m3u_file_path):
        with open(m3u_file_path, "w") as file:
            file.write("#EXTM3U\n")
    monitor_stream()
