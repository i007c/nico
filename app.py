

import json
import logging
from datetime import datetime
from pathlib import Path

from httpx import Client, NetworkError

from configs import AIR_ATTRS, ATTR_MAP, BASE_DATA, CITIES, TOKEN, WEBHOOKS


BASE_DIR = Path(__file__).resolve().parent

HOST = 'https://api.waqi.info'
PREVIOUS_DB = BASE_DIR / 'previous_air_data.json'
PREVIOUS_DATA = None

GREEN = 56445
RED = 14811960
YELLOW = 16766464


logging.basicConfig(
    filename=BASE_DIR / 'warn.log',
    encoding='utf-8',
    level=logging.WARNING,
    format=(
        ('-' * 50) + '\n%(asctime)s\n'
        '%(levelname)s:%(name)s\n'
        '%(message)s\n'
    )
)
logger = logging.getLogger(__name__)


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def init_previous_data():
    global PREVIOUS_DATA

    if PREVIOUS_DB.is_file():
        with open(PREVIOUS_DB, 'r') as db:
            PREVIOUS_DATA = json.load(db)


def send_webhooks(**kwargs: dict):
    with Client() as client:
        for url in WEBHOOKS:
            response = client.post(url, json={**BASE_DATA, **kwargs})

        if response.is_error:
            logger.error(response.text)


def get_previous_data(city_id: int) -> dict | None:
    if PREVIOUS_DATA is None:
        return None

    for city in PREVIOUS_DATA:
        if city['id'] == city_id:
            return city['data']

    return None


def get_air_data(identities: list[int]) -> dict | None:
    air = {}
    params = {'token': TOKEN}

    with Client(base_url=f'{HOST}/feed/', params=params) as client:
        for identity in identities:
            response = client.get(f'@{identity}')

            if response.is_error:
                logger.error(response.text)
                raise NetworkError(f'Error getting air qualities: @{identity}')

            iaqi = response.json()['data']['iaqi']

            for attr in AIR_ATTRS:
                item = iaqi.get(attr)
                avg = air.get(attr, [0, 0])

                if item:
                    avg[0] = avg[0] + item['v']
                    avg[1] = avg[1] + 1
                    air[attr] = avg
                else:
                    air[attr] = avg

    # get the average
    for key, value in air.items():
        if not value[0] or not value[1]:
            avg = 0
        else:
            avg = round(value[0] / value[1], 2)

        air[key] = avg

    return air


def make_embed(city, air_data: list, color: int = 15921906) -> dict:
    # get field
    def GF(item):
        vary = item[2]
        value = str(item[1]) if item[1] != 0 else '---'
        value_str = value

        if vary:
            value_str = f'{vary} {value}'

        return {
            'name': item[0],
            'value': value_str,
            'inline': True
        }

    fields = list(map(GF, air_data))

    embed = {
        'title': city['name'],
        'color': color,
        'fields': fields,
    }

    thumbnail = city.get('thumbnail')
    if thumbnail:
        embed['thumbnail'] = {
            'url': thumbnail
        }

    return embed


def get_color(score: int) -> int:
    if score < 10:
        return GREEN
    elif score < 20:
        return YELLOW
    else:
        return RED


def handle_city(city) -> tuple[dict, dict]:

    air_data = get_air_data(city['identities'])

    previous_data = get_previous_data(city['id'])
    embed_air_data = []

    # get embed air data
    def GEAD(attr: str):
        current_value = air_data[attr]
        previous_value = previous_data[attr]

        vary = None

        if current_value > previous_value:
            vary = '▲'
        elif current_value < previous_value:
            vary = '▼'

        return (ATTR_MAP[attr], current_value, vary)

    if previous_data is None:
        embed_air_data = list(map(
            lambda attr: (
                ATTR_MAP[attr], air_data[attr], None
            ), AIR_ATTRS
        ))
    else:
        embed_air_data = list(map(GEAD, AIR_ATTRS))

    embed = make_embed(city, embed_air_data, get_color(air_data['so2']))

    return air_data, embed


def main():
    try:
        init_previous_data()

        embeds = []
        cities_datas = []

        for city in CITIES:
            air_data, embed = handle_city(city)
            embeds.append(embed)
            cities_datas.append({
                'id': city['id'],
                'data': air_data
            })

        send_webhooks(
            content=f'**AIR QUALITY REPORT** `{now()}`',
            embeds=embeds
        )

        with open(PREVIOUS_DB, 'w') as db:
            json.dump(cities_datas, db)

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
