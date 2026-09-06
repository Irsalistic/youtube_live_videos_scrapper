# YouTube Live Stream Collector

Personal scripts that collect titles and descriptions from public YouTube live-search pages, then try to infer a location with spaCy and geocode it.

**Use this only in ways YouTube's terms of service allow.** Automated collection can violate those terms.

There is no `main.py`. The main script is `youtube_live_streams.py`.

## Setup

```bash
git clone https://github.com/Irsalistic/youtube_live_videos_scrapper.git
cd youtube_live_videos_scrapper
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

You need Google Chrome installed.

## Run

```bash
python youtube_live_streams.py
```

`live_videos.py` is an earlier variant. `location_nlp.py` and `location_api.py` are location helpers.

## Output

JSON files per category (`beaches.json`, `city_view.json`, `sport.json`, …) with title, description, and optional lat/long when a place name was found.

## Layout

```
youtube_live_streams.py   # Main collector
live_videos.py            # Older collector
location_nlp.py
location_api.py
*.json                    # Previous output
```
