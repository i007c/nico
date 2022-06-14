

import logging

import httpx

from configs import AIR_ATTRS, ATTR_MAP, BASE_DATA, CITIES, TOKEN, WEBHOOKS


HOST = 'https://api.waqi.info'


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


def send_webhooks(embed: dict):
    try:
        data = {**BASE_DATA, 'embeds': [embed]}

        for url in WEBHOOKS:
            response = httpx.post(url, json=data)

            if response.is_error:
                logger.error(response.text)

    except Exception as e:
        logger.exception(e)


def get_air_data(city: dict) -> dict | None:
    try:

        air = {}
        air_beauty = {}

        for identity in city['identities']:
            url = f'{HOST}/feed/@{identity}/?token={TOKEN}'
            response = httpx.get(url)

            if response.is_error:
                logger.error(response.text)
                return

            response = response.json()
            iaqi = response['data']['iaqi']

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

        E = {
            'title': city,
            'color': 15921906,
            'fields': fields
        }

        return E
    except Exception as e:
        logger.exception(e)


def main():

    for city in CITIES:
        air_data = get_air_data(city)
        if not air_data:
            return

        embed = embed_create(city['name'], air_data[1])

        if embed:
            send_webhooks(embed)


if __name__ == '__main__':
    main()
