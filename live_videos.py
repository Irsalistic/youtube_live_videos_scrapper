import json
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def extract_live_stream_data(url, scroll_increment=20000, num_scroll_iterations=3):
    # Set up Selenium WebDriver
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)

    # Wait for the page to load
    time.sleep(1)  # You may need to adjust the sleep time based on your internet speed

    try:
        live_stream_data = []

        for _ in range(num_scroll_iterations):
            # Scroll down to load more videos
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight + {scroll_increment});")
            time.sleep(1)  # Wait for the newly loaded videos to appear

            # Find all video elements
            video_elements = driver.find_elements_by_css_selector('div.style-scope.ytd-rich-grid-media')

            # Flag to determine if there are still live videos in the new content
            live_videos_found = False

            # Extract data of live streaming videos
            for video_element in video_elements:
                try:
                    title_element = video_element.find_element_by_css_selector('h3.style-scope.ytd-rich-grid-media')
                    live_indicator = video_element.find_element_by_css_selector(
                        'div#time-status span.style-scope.ytd-thumbnail-overlay-time-status-renderer')
                    if live_indicator.text.strip() == "LIVE":
                        video_url = video_element.find_element_by_css_selector('a#thumbnail').get_attribute('href')
                        video_id = video_url.split("v=")[1].split("&")[0]  # Extracting video ID from the URL

                        # Extracting video description
                        driver.get(video_url)
                        time.sleep(2)  # Wait for the video page to load
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        meta_description = soup.find('meta', property='og:description')['content']
                        first_sentence = meta_description.split('.')[0] + '.'

                        live_stream_data.append(
                            {"video_id": video_id, "title": title_element.text.strip(), "description": first_sentence})

                        live_videos_found = True  # Set flag to true if live video is found
                except NoSuchElementException:
                    # If the title element, live indicator, or video URL is not found, skip to the next video
                    continue

            # If no live videos are found in the newly loaded content, break the loop
            if not live_videos_found:
                break

        return live_stream_data

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        # Close the browser
        driver.quit()


# List of URLs to extract live streaming data from
urls = [
    "https://www.youtube.com/@WebcamGreece/streams",
    "https://www.youtube.com/@BostonAndMaineLive/streams",
    "https://www.youtube.com/@TheRealSamuiWebcam/streams"

]

all_live_stream_data = []

for index, url in enumerate(urls, start=1):
    print(f"Extracting data from URL {index}/{len(urls)}: {url}")
    live_stream_data = extract_live_stream_data(url)
    if live_stream_data:
        all_live_stream_data.extend(live_stream_data)
        print(f"Data extracted successfully from {url}")
    else:
        print(f"Failed to extract data from the URL {url}")

# Save all data to a single JSON file with proper encoding
filename = "all_live_stream_data.json"
with open(filename, 'w', encoding='utf-8') as json_file:
    json.dump(all_live_stream_data, json_file, ensure_ascii=False, indent=4)

print(f"All live streaming data saved to {filename}")
