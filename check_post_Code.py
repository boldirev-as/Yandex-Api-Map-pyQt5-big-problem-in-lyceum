import requests
json_data = {"query": "Екатеринбург, Родонитововая 28", "limit": 5, "fromBound": "CITY"}
resp = requests.post('https://www.pochta.ru/suggestions/v2/suggestion.find-addresses', json=json_data)
print(resp.json()[0]['postalCode'])

# spn[0] - долгота - place[0] - x
# spn[1] - широта - place[0] - y
