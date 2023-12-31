from urllib import response
import requests
import json
import time

API_KEY = "26e2379f-ec2c-49e2-b727-0a5594a9ab19"

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

IMAGES = [
    "https://i.natgeofe.com/k/271050d8-1821-49b8-bf0b-3a4a72b6384a/obama-portrait__3x2.jpg",
    "https://d3hjzzsa8cr26l.cloudfront.net/516e6836-d278-11ea-a709-979a0378f022.jpg",
    "https://hips.hearstapps.com/hmg-prod/images/gettyimages-1239961811.jpg"
]
def create_model(title):
    url = "https://api.tryleap.ai/api/v1/images/models"

    payload = {
        "title": title,
        "subjectKeyword": "@me"
    }
    
    response = requests.post(url, json=payload, headers=HEADERS)
    print(response.text)         
    model_id = json.loads(response.text)["id"]
   # print(response.text)
    return model_id


def upload_image_samples(model_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/samples/url"

    payload = {"images": IMAGES}
    response = requests.post(url, json=payload, headers=HEADERS)


def queue_training_job(model_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/queue"
    response = requests.post(url, headers=HEADERS)
    data = json.loads(response.text)

    print(response.text)

    version_id = data["id"]
    status = data["status"]

    print(f"Version ID: {version_id}. Status: {status}")

    return version_id, status


def get_model_version(model_id, version_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/versions/{version_id}"
    response = requests.get(url, headers=HEADERS)
    data = json.loads(response.text)

    version_id = data["id"]
    status = data["status"]

    print(f"Version ID: {version_id}. Status: {status}")

    return version_id, status


def generate_image(model_id, prompt):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences"

    payload = {
        "prompt": prompt,
        "steps": 50,
        "width": 512,
        "height": 512,
        "numberOfImages": 1,
        "seed": 4523184
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    data = json.loads(response.text)

    inference_id = data["id"]
    status = data["status"]

    print(f"Inference ID: {inference_id}. Status: {status}")

    return inference_id, status


def get_inference_job(model_id, inference_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences/{inference_id}"

    response = requests.get(url, headers=HEADERS)
    data = json.loads(response.text)

    inference_id = data["id"]
    state = data["state"]
    image = None

    if len(data["images"]):
        image = data["images"][0]["uri"]

    print(f"Inference ID: {inference_id}. State: {state}")

    return inference_id, state, image
model_id = create_model("Sample")
upload_image_samples(model_id)
version_id, status = queue_training_job(model_id)
while status != "finished":
    time.sleep(10)
    version_id, status = get_model_version(model_id, version_id)
inference_id, status = generate_image(
    model_id, 
    prompt="8k detailed portrait of @me, futuristic sci-fi style, low-emission-neon, bladerunner movie scene style"
)
while status != "finished":
    time.sleep(10)
    inference_id, status, image = get_inference_job(model_id, inference_id)

print(image)