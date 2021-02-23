import requests
import math

STATIC_API_SERVER = "https://static-maps.yandex.ru/1.x/"
GEOCODE_API_SERVER = "https://geocode-maps.yandex.ru/1.x"


def get_size_toponym(toponym):
    toponym_upper_lower = toponym["boundedBy"]["Envelope"]
    toponym_upper, toponym_lower = toponym_upper_lower["lowerCorner"].split(" ")
    toponym_upper_2, toponym_lower_2 = toponym_upper_lower["upperCorner"].split(" ")

    delta_1 = round(abs(float(toponym_lower) - float(toponym_lower_2)) / 2, 6)
    delta_2 = round(abs(float(toponym_upper) - float(toponym_upper_2)) / 2, 6)
    return [delta_1, delta_2]


def get_postal_number_toponym(toponym):
    try:
        components = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]
        city = ""
        for comp in components:
            if "locality" == comp["kind"]:
                city = comp["name"]
        name = toponym["name"]

        json_data = {"query": f"{city}, {name}", "limit": 5, "fromBound": "CITY"}
        resp = requests.post('https://www.pochta.ru/suggestions/v2/suggestion.find-addresses', json=json_data)
        print("-->", city, name)
        return resp.json()[0]['postalCode']
    except Exception as e:
        print("Ошибка выполнения запроса:", e)
        return None


def get_map(coords, spn, type_map, pts):
    params = {
        "ll": ",".join(map(str, coords)),
        "spn": ",".join(map(str, spn)),
        "l": type_map
    }
    if pts is not None:
        params["pt"] = pts

    response = requests.request(method="GET", url=STATIC_API_SERVER,
                                params=params)
    print(requests.request(method="GET", url=STATIC_API_SERVER,
                           params=params).url)

    return response.content


def get_map_if_text(text, type_map):
    params = {
        "geocode": text,
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json"
    }

    response = requests.request(method="GET", url=GEOCODE_API_SERVER,
                                params=params)
    print(requests.request(method="GET", url=GEOCODE_API_SERVER,
                           params=params).url, "toponym")

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    toponym_coodrinates = list(map(float, toponym["Point"]["pos"].split()))
    spn = get_size_toponym(toponym)
    return {"image": get_map(toponym_coodrinates, spn, type_map, f"{','.join(map(str, toponym_coodrinates))},pm2rdm1"),
            "spn": spn, "coords": toponym_coodrinates, "toponym": toponym}


def get_toponym(coords):
    params = {
        "geocode": ",".join(map(str, coords)),
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json"
    }

    response = requests.request(method="GET", url=GEOCODE_API_SERVER,
                                params=params)
    print(requests.request(method="GET", url=GEOCODE_API_SERVER,
                           params=params).url, "toponym")

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return toponym


def get_all_inf(toponym):
    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

    return {"address": toponym_address,
            "postal_code": get_postal_number_toponym(toponym)}


def get_organizations(coords):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    address_ll = f"{coords[0]},{coords[1]}"

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    print(requests.get(search_api_server, params=search_params).url)
    if not response:
        print("error business")
    json_response = response.json()

    # Получаем первую найденную организацию.
    for organization in json_response["features"]:
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        # Адрес организации.
        org_address = organization["properties"]["CompanyMetaData"]["address"]

        # Получаем координаты ответа.
        point = organization["geometry"]["coordinates"]
        if lonlat_distance(point, coords) <= 50:
            print(org_name)
            return {"name": org_name, "address": org_address,
                    "coords": list(map(float, point))}


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance
