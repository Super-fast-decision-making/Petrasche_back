import requests, json

def image_type(img):
    mr_url = "http://49.247.25.171:8000/uploadfiles/"
    img_file = {'files': img}
    response = requests.post(mr_url, files=img_file)
        
    return response.json()