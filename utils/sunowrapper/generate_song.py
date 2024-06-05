import requests

from utils.sunowrapper.constants import BASE_URL


def generate_music(lyrics, title, style):
    url = f"{BASE_URL}/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": lyrics,
        "mv": "chirp-v3-5",
        "title": title,
        "tags": style
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        clip_ids = [clip["id"] for clip in data.get("clips", [])]
        if len(clip_ids) >= 2:
            return clip_ids[:2]
        else:
            return clip_ids  # Retourner autant de clips que disponibles
    else:
        raise Exception(f"Failed to generate music: {response.status_code}, {response.text}")


def fetch_feed(aid):
    url = f"{BASE_URL}/feed/{aid}"
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data:
            result = {
                "video_url": item.get("video_url"),
                "audio_url": item.get("audio_url"),
                "image_large_url": item.get("image_large_url"),
                "title": item.get("title"),
                "duration": item.get("metadata", {}).get("duration")
            }
            results.append(result)
        return results
    else:
        raise Exception(f"Failed to fetch feed: {response.status_code}, {response.text}")

