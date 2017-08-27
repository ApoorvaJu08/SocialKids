'''import clarifai.rest as cr

app = cr.ClarifaiApp(api_key='a482d25e34214265817cf5de20498fa3')
model = app.models.get('nsfw-v1.0')
response = model.predict_by_url('http://media.indiatimes.in/media/content/2015/Sep/8_1441875089.jpg')
print response


# this is parallel dots

import requests
import json
apikey = 'm1zlSpU2Gb0MrRMLPoGtGUsdFcVBNTAKxDyljfJkjkU'
url = 'http://apis.paralleldots.com/abuse'
text = 'chutiya'
r = requests.post(url, paramas={"apikey": apikey, 'text': text})
print r.text

'''