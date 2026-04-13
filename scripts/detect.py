from urllib import response

import requests, json, time, os, base64
from datetime import datetime
import pandas as pd

HIVE_API_KEY = os.getenv("HIVE_API_KEY")  # Set API key ENV variable or replace with your own API key
HIVE_ENDPOINT = "https://api.thehive.ai/api/v3/hive/ai-generated-and-deepfake-content-detection"

AIORNOT_API_KEY=os.getenv("AIORNOT_API_KEY")
AIORNOT_ENDPOINT = "https://api.aiornot.com/v2/image/sync"

WINSTON_API_KEY=os.getenv("WINSTON_API_KEY")
WINSTON_ENDPOINT = "https://api.gowinston.ai/v2/image-detection"

def get_image_paths(base_dir='../images/'):
  image_paths = []
  for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.png'):
            __path__ = os.path.join(root, file)
            image_paths.append({"path": __path__, "file": file})
  return image_paths

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Read the image file and encode it
        encoded_string = base64.b64encode(image_file.read())
        
        # Convert bytes to string (removes the b' prefix)
        base64_string = encoded_string.decode('utf-8')
    return base64_string

def output_results(scores, summary, prefix="hive"):
    ts = datetime.now().timestamp()

    with open(f"../output/{prefix}-raw-{ts}.json", 'w') as f:
        json.dump(scores, f, indent=2)
        ts = datetime.now().timestamp()

    df = pd.DataFrame.from_dict(summary, orient='index')
    df.to_csv(f'../output/{prefix}-summary-{ts}.csv', header=True)


def call_hive_api():
  images = get_image_paths()
  scores = {}
  summary = {}
  
  for image in images:
    time.sleep(.5) # To avoid hitting rate limits
    image_base64 = encode_image_to_base64(image["path"])
    payload = {
      "media_metadata": True,
      "input": [
        { "media_base64": "data:<mime>;base64," +  image_base64}
      ]
    }

    res = requests.post(
      HIVE_ENDPOINT,
      headers={"Authorization": f"Bearer {HIVE_API_KEY}", "Content-Type": "application/json"},
      data=json.dumps(payload),
      timeout=60
    )
  
    scores[image["file"]] = res.json()
    classes = scores[image["file"]]["output"][0]["classes"]
    class_map = {item["class"]: item["value"] for item in classes}

    ai_score = class_map.get("ai_generated", 0)
    human_score = class_map.get("not_ai_generated", 0)
    verdict = "ai" if ai_score > human_score else "human"

    summary[image["file"]] = {
      "verdict": verdict,
      "ai_score": ai_score,
      "human_score": human_score
    }

  output_results(scores, summary, prefix="hive")

def call_aiornot_api():
  images = get_image_paths()
  scores = {}
  summary = {}
  
  for image in images:
    time.sleep(.5) # To avoid hitting rate limits
    with open(image["path"], "rb") as f:
      resp = requests.post(
          AIORNOT_ENDPOINT,
          headers={"Authorization": f"Bearer {AIORNOT_API_KEY}"},
          files={"image": f},
          params={
              "external_id": image["file"],  # Optional
              # Example: only run reverse_search:
              # "only": ["reverse_search"]
              # Example: run all defaults except deepfake:
              "excluding": ["deepfake", "nsfw", "quality"]
          })
      resp.raise_for_status()
      scores[image["file"]] = resp.json()
      summary[image["file"]] = {
          "verdict": scores[image["file"]]["report"]["ai_generated"]["verdict"],
          "ai_score": scores[image["file"]]["report"]["ai_generated"]["ai"]["confidence"],
          "human_score": scores[image["file"]]["report"]["ai_generated"]["human"]["confidence"]
      }

  output_results(scores, summary, prefix="airornot")

def call_winston_api():
  images = get_image_paths()
  scores = {}
  summary = {}
  print(WINSTON_API_KEY)
  resp = requests.post(
    WINSTON_ENDPOINT,
    files={
      "url": "https://raw.githubusercontent.com/sfs-code/ai-image-dataset/main/images/img-001/A-img-001-x-nm.png"},
    headers={"Authorization": f"Bearer {WINSTON_API_KEY}",
              "Content-Type": "application/json"},
)
  print(resp.json())

def call_winston_api2():
  url = WINSTON_ENDPOINT

  payload = {
      "url": "https://raw.githubusercontent.com/sfs-code/ai-image-dataset/main/images/img-001/A-img-001-x-nm.png"
  }
  headers = {
      "Authorization": f"Bearer {WINSTON_API_KEY}",
      "Content-Type": "application/json"
  }

  response = requests.post(url, json=payload, headers=headers)
  print(response.text)

#call_aiornot_api()
#call_hive_api()
call_winston_api2()
