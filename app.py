

import logging
from datetime import datetime
from threading import Thread

import httpx

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
        for url in WEBHOOKS:
            response = httpx.post(url, json={**BASE_DATA, **kwargs})

            if response.is_error:
                logger.error(response.text)

    except Exception as e:
        logger.exception(e)


def get_air_data(city: dict) -> dict | None:
    try:
        air = {}
        air_beauty = {}
        params = {'token': TOKEN}

        with httpx.Client(base_url=f'{HOST}/feed/', params=params) as client:
            for identity in city['identities']:
                response = client.get(f'@{identity}')

                if response.is_error:
                    logger.error(response.text)
                    return

                response = response.json()['data']
                iaqi = response['iaqi']

                for attr in AIR_ATTRS:
                    item = iaqi.get(attr)

                    if item:
                        avg = air.get(attr, [0, 0])
                        avg[0] = avg[0] + item['v']
                        avg[1] = avg[1] + 1
                        air[attr] = avg

        # get the average
        for key, value in air.items():
            avg = round(value[0] / value[1], 2)

            air[key] = avg
            air_beauty[ATTR_MAP[key]] = avg

        return air, air_beauty

    except Exception as e:
        logger.exception(e)


def embed_create(city, air: dict) -> dict:
    try:

        # get field
        def GF(item):
            return {
                'name': str(item[0]),
                'value': str(item[1]),
                'inline': True
            }

        fields = list(map(GF, air.items()))
        date = date.strftime('%Y-%m-%d %H:%M')

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
    except Exception as e:
        logger.exception(e)


def handle_city(city):
    air_data = get_air_data(city)

    if not air_data:
        return

    embed = embed_create(city, air_data[1])

    if embed:
        embeds.append(embed)


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
