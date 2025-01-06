# YouTube Live Stream Data Extractor

A Python-based tool that extracts information from YouTube live streams, including titles, descriptions, and geographic locations. The tool uses natural language processing to identify locations from stream titles and descriptions, and converts them to geographic coordinates.

## Features

- Extracts data from multiple YouTube live stream categories simultaneously
- Identifies geographic locations from stream titles and descriptions using SpaCy NLP
- Converts location names to geographic coordinates
- Supports parallel processing for faster data collection
- Saves extracted data in JSON format
- Handles various stream categories (beaches, spaces, city views, sports, etc.)

## Prerequisites

```bash
pip install -r requirements.txt
```

Required Python packages:
- selenium
- webdriver-manager
- spacy
- geopy
- json
- multiprocessing

You'll also need to download the English language model for SpaCy:
```bash
python -m spacy download en_core_web_sm
```

## Installation

1. Clone this repository
2. Install the required packages
3. Download the SpaCy language model
4. Update the SpaCy model path in the code to match your system:
   ```python
   nlp = spacy.load("en_core_web_sm")
   ```

## Usage

Run the script using:
```bash
python main.py
```

The script will:
1. Search YouTube for live streams in different categories
2. Extract stream information including titles and descriptions
3. Identify locations using natural language processing
4. Convert locations to geographic coordinates
5. Save the data in separate JSON files for each category

## Output

The script generates JSON files for each category with the following information:
- video_id: YouTube video identifier
- title: Stream title
- description: Stream description
- location: Extracted location name
- latitude: Geographic latitude
- longitude: Geographic longitude

Example output structure:
```json
[
    {
        "video_id": "abc123xyz",
        "title": "Live Beach Cam - Miami Beach",
        "description": "24/7 live stream of Miami Beach, Florida",
        "location": "Miami Beach, Florida",
        "latitude": 25.7907,
        "longitude": -80.1300
    }
]
```

## Categories

The tool currently supports the following categories:
- Beaches
- Spaces
- City Views
- Sports
- Concerts
- Animals
- Landscapes
- Ski Slopes
- Random Live Broadcast Cameras

## Performance Metrics

The script provides metrics on location extraction:
- Total number of videos processed
- Number of successful location extractions
- Number of failed location extractions

## Configuration

You can modify the following parameters in the code:
- `scroll_increment`: Controls how far the page scrolls (default: 20000)
- `num_scroll_iterations`: Number of scroll attempts (default: 3, 8 for random streams)
- Chrome options for the web driver
- URL to filename mappings in `url_filename_mapping`

## Notes

- The script uses headless Chrome browser for web scraping
- Location extraction may not be successful for all streams
- Geographic coordinate conversion depends on the Nominatim service
- Rate limiting may apply when using the geocoding service

## Error Handling

The script includes error handling for:
- Browser automation issues
- Missing elements on the page
- Geocoding failures
- File operations

## Contributing

Feel free to submit issues and enhancement requests!
