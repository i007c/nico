

import logging
from datetime import datetime
from threading import Thread

from httpx import Client, NetworkError

from configs import AIR_ATTRS, ATTR_MAP, BASE_DATA, CITIES, TOKEN, WEBHOOKS


HOST = 'https://api.waqi.info'
embeds = []


logging.basicConfig(
    filename='warn.log',
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


def send_webhooks(**kwargs: dict):
    try:
        with Client() as client:
            for url in WEBHOOKS:
                response = client.post(url, json={**BASE_DATA, **kwargs})

            if response.is_error:
                logger.error(response.text)

    except Exception as e:
        logger.exception(e)


def get_air_data(city: dict) -> dict | None:
    air = {}
    params = {'token': TOKEN}

    with Client(base_url=f'{HOST}/feed/', params=params) as client:
        for identity in city['identities']:
            response = client.get(f'@{identity}')

            if response.is_error:
                logger.error(response.text)
                raise NetworkError(f'Error getting air qualities: @{identity}')

            response = response.json()['data']
            iaqi = response['iaqi']

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

    # sort to a list
    return list(map(lambda attr: (ATTR_MAP[attr], air[attr]), AIR_ATTRS))


def embed_create(city, air_data: list) -> dict:
    # get field
    def GF(item):
        value = str(item[1]) if item[1] != 0 else '---'

        return {
            'name': item[0],
            'value': value,
            'inline': True
        }

    fields = list(map(GF, air_data))

    embed = {
        'title': city['name'],
        'color': 15921906,
        'fields': fields,
    }

    thumbnail = city.get('thumbnail')
    if thumbnail:
        embed['thumbnail'] = {
            'url': thumbnail
        }

    return embed


def handle_city(city):
    try:
        air_data = get_air_data(city)

        embed = embed_create(city, air_data)

        if embed:
            embeds.append(embed)

    except Exception as e:
        logger.exception(e)


def main():
    threads = []

    for city in CITIES:
        thread = Thread(target=handle_city, args=(city, ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    send_webhooks(
        content=f'**AIR QUALITY REPORT** `{now()}`\n' + '-' * 53,
        embeds=embeds
    )


if __name__ == '__main__':
    main()
