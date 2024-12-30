



import json
import time
import spacy
import multiprocessing
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from geopy.geocoders import Nominatim

# Setting up chrome options to run in headless mode, enabling javascript execution and adding the headers for http reqs.
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument('--enable-javascript')
chrome_options.add_argument('window-size=1920x1080')

# Counter for total locations
total_locations = 0
# Counter for null locations
null_locations = 0

def extract_live_stream_data(url, scroll_increment=20000, num_scroll_iterations=3):
    global total_locations, null_locations  # Accessing global variables

    try:
        live_stream_data = []
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(url)
        time.sleep(1)

        for _ in range(num_scroll_iterations):
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight + {scroll_increment});")
            time.sleep(1)

            video_elements = driver.find_elements_by_css_selector('div#dismissible')

            live_videos_found = False
            for video_element in video_elements:
                try:
                    title_element = video_element.find_element_by_id('video-title')
                    live_indicator = video_element.find_element_by_css_selector(
                        'p.style-scope.ytd-badge-supported-renderer')
                    if live_indicator.text.strip() == "LIVE":
                        description_element = video_element.find_element_by_css_selector(
                            'div.metadata-snippet-container yt-formatted-string.metadata-snippet-text')
                        description = description_element.text.strip()
                        video_url = video_element.find_element_by_css_selector('a#thumbnail').get_attribute('href')
                        video_id = video_url.split("v=")[1].split("&")[0]

                        location, location_coordinates = extract_location_from_title(title_element.text.strip())
                        if not location:
                            null_locations += 1  # Increment null_locations counter
                        else:
                            total_locations += 1  # Increment total_locations counter

                        live_stream_data.append(
                            {"video_id": video_id, "title": title_element.text.strip(), "description": description,
                             "location": location, "location_coordinates": location_coordinates})
                        live_videos_found = True
                except NoSuchElementException:
                    continue

            if not live_videos_found:
                break

        return live_stream_data

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()


def extract_location_coordinates(location):
    geolocator = Nominatim(user_agent="orienternet-yicocc", timeout=10)
    location_data = geolocator.geocode(location)
    if location_data:
        latitude = location_data.latitude
        longitude = location_data.longitude
        return {"latitude": latitude, "longitude": longitude}
    else:
        return None


geolocator = Nominatim(user_agent="orienternet-yicocc", timeout=10)

def extract_location_from_description(description):
    # Load the English language model with NER capabilities
    nlp = spacy.load(
        r"C:\Users\Hamza\AppData\Roaming\Python\Python311\site-packages\en_core_web_sm\en_core_web_sm-3.7.1")
    # Process the description text
    doc = nlp(description)

    # Extract location entities
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"]

    # Geocode each location mentioned in the description
    location_coordinates = []
    for location in locations:
        location_data = geolocator.geocode(location)
        if location_data:
            latitude = location_data.latitude
            longitude = location_data.longitude
            location_coordinates.append({"latitude": latitude, "longitude": longitude})

    return locations, location_coordinates


def extract_location_from_title(title):
    # Load the English language model with NER capabilities
    nlp = spacy.load(
        r"C:\Users\Hamza\AppData\Roaming\Python\Python311\site-packages\en_core_web_sm\en_core_web_sm-3.7.1")
    # Process the title text
    doc = nlp(title)

    # Extract location entities
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"]

    # Combine locations into a single string
    location = ", ".join(locations)

    # Extract coordinates for the combined location
    location_coordinates = extract_location_coordinates(location)

    return location, location_coordinates


# Dictionary mapping URLs to filenames
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


def process_url(url, filename):
    live_stream_data = extract_live_stream_data(url)
    if live_stream_data:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(live_stream_data, json_file, ensure_ascii=False, indent=4)
        print(f"Live streaming data from {url} saved to {filename}")
    else:
        print(f"No live streaming data found on {url}")


if __name__ == "__main__":
    processes = []
    for url, filename in url_filename_mapping.items():
        process = multiprocessing.Process(target=process_url, args=(url, filename))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # Output total and null locations after all processes finish
    print(f"Total locations: {total_locations}")
    print(f"Null locations: {null_locations}")
