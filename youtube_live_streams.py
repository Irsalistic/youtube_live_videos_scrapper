import json
import multiprocessing
import time

import spacy
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument("window-size=1920x1080")

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_live_stream_data(url, scroll_increment=20000, num_scroll_iterations=3, total_locations=None,
                             null_locations=None):
    driver = None
    try:
        if total_locations is None:
            total_locations = multiprocessing.Value("i", 0)
        if null_locations is None:
            null_locations = multiprocessing.Value("i", 0)

        live_stream_data = []
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(1)

        if url == "https://www.youtube.com/results?search_query=live+broadcast+cams&sp=CAMSAkAB":
            num_scroll_iterations = 8

        for _ in range(num_scroll_iterations):
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight + {scroll_increment});")
            time.sleep(1)

            video_elements = driver.find_elements(By.CSS_SELECTOR, "div#dismissible")

            live_videos_found = False
            for video_element in video_elements:
                try:
                    title_element = video_element.find_element(By.ID, "video-title")
                    live_indicator = video_element.find_element(
                        By.CSS_SELECTOR, "p.style-scope.ytd-badge-supported-renderer"
                    )
                    if live_indicator.text.strip() == "LIVE":
                        description_element = video_element.find_element(
                            By.CSS_SELECTOR,
                            "div.metadata-snippet-container yt-formatted-string.metadata-snippet-text",
                        )
                        description = description_element.text.strip()
                        video_url = video_element.find_element(By.CSS_SELECTOR, "a#thumbnail").get_attribute("href")
                        video_id = video_url.split("v=")[1].split("&")[0]

                        location, latitude, longitude = extract_location_from_title(title_element.text.strip())
                        if not location:
                            location, latitude, longitude = extract_location_from_description(description)
                            if not location:
                                null_locations.value += 1
                            else:
                                total_locations.value += 1
                        else:
                            total_locations.value += 1

                        live_stream_data.append(
                            {
                                "video_id": video_id,
                                "title": title_element.text.strip(),
                                "description": description,
                                "location": location,
                                "latitude": latitude,
                                "longitude": longitude,
                            }
                        )
                        live_videos_found = True
                except NoSuchElementException:
                    continue

            if not live_videos_found:
                break

        return live_stream_data

    except Exception as exc:
        print(f"Error occurred: {exc}")
        return None
    finally:
        if driver is not None:
            driver.quit()


def extract_location_coordinates(location):
    geolocator = Nominatim(user_agent="orienternet-yicocc", timeout=10)
    location_data = geolocator.geocode(location)
    if location_data:
        return location_data.latitude, location_data.longitude
    return 0.0, 0.0


def extract_location_from_title(title):
    doc = get_nlp()(title)
    locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
    location = ", ".join(locations)
    latitude, longitude = extract_location_coordinates(location)
    return location, latitude, longitude


def extract_location_from_description(description):
    doc = get_nlp()(description)
    locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "ORG", "FAC")]
    location = ", ".join(locations)
    latitude, longitude = extract_location_coordinates(location)
    return location, latitude, longitude


url_filename_mapping = {
    "https://www.youtube.com/results?search_query=beaches&sp=CAMSAkAB": "beaches.json",
    "https://www.youtube.com/results?search_query=spaces&sp=CAMSAkAB": "spaces.json",
    "https://www.youtube.com/results?search_query=city_view&sp=CAMSAkAB": "city_view.json",
    "https://www.youtube.com/results?search_query=sport&sp=CAMSAkAB": "sport.json",
    "https://www.youtube.com/results?search_query=concerts&sp=CAMSAkAB": "concerts.json",
    "https://www.youtube.com/results?search_query=animals&sp=CAMSAkAB": "animals.json",
    "https://www.youtube.com/results?search_query=landscapes&sp=CAMSAkAB": "landscapes.json",
    "https://www.youtube.com/results?search_query=ski_slopes&sp=CAMSAkAB": "ski_slopes.json",
    "https://www.youtube.com/results?search_query=live+broadcast+cams&sp=CAMSAkAB": "random_streams.json",
}


def process_url(url, filename, total_locations, null_locations):
    live_stream_data = extract_live_stream_data(url, total_locations=total_locations, null_locations=null_locations)
    if live_stream_data:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(live_stream_data, json_file, ensure_ascii=False, indent=4)
        print(f"Live streaming data from {url} saved to {filename}")
    else:
        print(f"No live streaming data found on {url}")


if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        total_locations = manager.Value("i", 0)
        null_locations = manager.Value("i", 0)

        processes = []
        for url, filename in url_filename_mapping.items():
            process = multiprocessing.Process(target=process_url, args=(url, filename, total_locations, null_locations))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
        print(f"Total videos: {total_locations.value + null_locations.value}")
        print(f"locations founded: {total_locations.value}")
        print(f"locations not founded: {null_locations.value}")
