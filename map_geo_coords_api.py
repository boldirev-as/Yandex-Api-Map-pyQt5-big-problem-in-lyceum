import requests

STATIC_API_SERVER = "https://static-maps.yandex.ru/1.x/"


def get_map_from_coords(coords, type_in=str, spn=(0.025, 0.025)):
    params = {
        "ll": coords if type_in is str else ",".join(coords),
        "spn": ",".join(map(str, spn)),
        "l": "map"
    }

    response = requests.request(method="GET", url=STATIC_API_SERVER,
                                params=params)
    if response.status_code == 200:
        return response.content
    print(response.status_code)
    return None
