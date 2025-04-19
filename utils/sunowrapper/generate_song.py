import requests
import json
from utils.sunowrapper.constants import BASE_URL
import http.client


def generate_music(lyrics, title, style):

    url = f"{BASE_URL}/api/custom_generate"

    conn = http.client.HTTPSConnection("apibox.erweima.ai")

    # headers = {
    #     "Content-Type": "application/json"
    # }

    # payload = {
    #     "prompt": lyrics,
    #     "mv": "chirp-v3-5",
    #     "title": title,
    #     "tags": style
    # }

    # Model: "chirp-v3-5|chirp-v3-0" (chirp-v3-5 is the default model, chirp-v3-0 is the model for the instrumental)
    # payload = {
    #     "prompt": lyrics,
    #     "model": "chirp-v3-5|chirp-v3-0",
    #     "title": title,
    #     "tags": style,
    #     "make_instrumental": False,
    #     "wait_audio": False
    # }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer cad1dab497c8d5c64df38b1ddcfdeae1',
    }

    payload_new = json.dumps({
        "prompt": lyrics, # ...
        "style": style, # ...
        "title": title, # ...
        "customMode": True, # ...
        "instrumental": False, # ...
        "model": "V4", # V3_5
        # "negativeTags": "Relaxing Piano",
        "callBackUrl": "https://879b-137-255-33-47.ngrok-free.app/generation/callback"
        })

    print("\n")
    print(payload_new)
    print("\n")

    # {
    #     "prompt": "[Verse 1]\nCruel flames of war engulf this land\nBattlefields filled with death and dread\nInnocent souls in darkness, they rest\nMy heart trembles in this silent test\n\n[Verse 2]\nPeople weep for loved ones lost\nBattered bodies bear the cost\nSeeking peace and hope once known\nOur grief transforms to hearts of stone\n\n[Chorus]\nSilent battlegrounds, no birds' song\nShadows of war, where we don't belong\nMay flowers of peace bloom in this place\nLet's guard this precious dream with grace\n\n[Bridge]\nThrough the ashes, we will rise\nHand in hand, towards peaceful skies\nNo more sorrow, no more pain\nTogether, we'll break these chains\n\n[Chorus]\nSilent battlegrounds, no birds' song\nShadows of war, where we don't belong\nMay flowers of peace bloom in this place\nLet's guard this precious dream with grace\n\n[Outro]\nIn unity, our strength will grow\nA brighter future, we'll soon know\nFrom the ruins, hope will spring\nA new dawn, we'll together bring",
    #     "tags": "pop metal male melancholic",
    #     "title": "Silent Battlefield",
    #     "make_instrumental": false,
    #     "model": "chirp-v3-5|chirp-v3-0",
    #     "wait_audio": false
    # }

    # {
    #     "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.",
    #     "make_instrumental": false,
    #     "model": "chirp-v3-5|chirp-v3-0",
    #     "wait_audio": false
    # }

    # {
    #   "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.",
    #   "make_instrumental": false,
    #   "model": "chirp-v3-5|chirp-v3-0",
    #   "wait_audio": false
    # }

    conn.request("POST", "/api/v1/generate", payload_new, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    # raise Exception(f"Failed to generate music: {res.status}, {data}")

    return data.decode("utf-8")


    # Here to end the first part of the code of generation of music
    # response = requests.post(url, json=payload, headers=headers)

    # if response.status_code == 200:
    #     data = response.json()
    #     print("\n")
    #     print(data)
    #     print("\n")
    #     print(data)
    #     clip_ids = [clip["id"] for clip in data] # .get("clips", [])
    #     print(clip_ids)
    #     if len(clip_ids) >= 2:
    #         return clip_ids[:2]
    #     else:
    #         return clip_ids  # Retourner autant de clips que disponibles
    # else:
    #     raise Exception(f"Failed to generate music: {response.status_code}, {response.text}")


# fetch_feed function is used to fetch the generated music clips
def fetch_feed(aid):
    
    url = f"{BASE_URL}/api/get?ids={aid}" # aid = clip_id
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("data")
        print(data)
        print("data")
        results = []
        for item in data:
            result = {
                "video_url": item.get("video_url"),
                "audio_url": item.get("audio_url"),
                "image_large_url": item.get("image_url"),
                "title": item.get("title"),
                "duration": item.get("duration")
            }
            results.append(result)
        return results
    else:
        raise Exception(f"Failed to fetch feed: {response.status_code}, {response.text}")