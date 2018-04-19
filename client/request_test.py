import requests

r = requests.get('http://172.25.12.128:8900/list')
print(r.json()['address'])