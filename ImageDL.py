import json
import requests

image_formats = ("image/png", "image/jpeg", "image/jpg")
with open('Markets.json') as json_data:
    d = json.load(json_data)

    for market in d['Markets']:
        code = market['Code']
        url = market['Logo']
        extension = url.split('.')[len(url.split('.')) - 1]

        response = requests.get(url)

        if response.headers["content-type"] in image_formats:
            with open('logos/' + code + '.' + extension, "wb") as file:
                file.write(response.content)
# To convert the jpgs to png
#ls -1 *.jpg | xargs -n 1 bash -c 'convert "$0" "${0%.jpg}.png"'

