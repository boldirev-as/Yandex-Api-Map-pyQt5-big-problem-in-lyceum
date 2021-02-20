import requests

STATIC_API_SERVER = "https://static-maps.yandex.ru/1.x/"
GEOCODE_API_SERVER = "https://geocode-maps.yandex.ru/1.x"


def get_size_toponym(toponym, static=True):
    toponym_upper_lower = toponym["boundedBy"]["Envelope"]
    toponym_upper, toponym_lower = toponym_upper_lower["lowerCorner"].split(" ")
    toponym_upper_2, toponym_lower_2 = toponym_upper_lower["upperCorner"].split(" ")

    delta_1 = round(abs(float(toponym_lower) - float(toponym_lower_2)) / 2, 6)
    delta_2 = round(abs(float(toponym_upper) - float(toponym_upper_2)) / 2, 6)
    return [delta_1, delta_2]


def get_map_from_coords(coords, spn=(0.025, 0.025), l="map", pt=None):
    print("static", pt)
    params = {
        "ll": ",".join(map(str, coords)),
        "spn": ",".join(map(str, spn)),
        "l": l
    }
    if pt is not None:
        params["pt"] = "~".join(pt)

    response = requests.request(method="GET", url=STATIC_API_SERVER,
                                params=params)
    print(requests.request(method="GET", url=STATIC_API_SERVER,
                                params=params).url)
    return response.content


def get_map_from_text(text, l="map", pt=None):
    params = {
        "geocode": text,
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json"
    }

    response = requests.request(method="GET", url=GEOCODE_API_SERVER,
                                params=params)
    print(requests.request(method="GET", url=GEOCODE_API_SERVER,
                                params=params).url)

    if response.status_code:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        print("text 1", pt)
        if pt is not None:
            pt = pt + [f"{toponym_coodrinates.replace(' ', ',')},pm2rdm{len(pt) + 1}"]
        else:
            pt = [f"{toponym_coodrinates.replace(' ', ',')},pm2rdm1"]
        print("text 2", pt)
        image = get_map_from_coords(toponym_coodrinates.split(" "), spn=get_size_toponym(toponym), l=l, pt=pt)
        return image, toponym, list(map(float, toponym_coodrinates.split()))
    else:
        print(response.text)
        return None
