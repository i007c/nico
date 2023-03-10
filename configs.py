
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / 'secrets.json', 'r') as f:
    SECRETS = json.load(f)

CITIES = [
    {
        'id': 0,
        'name': ':flag_ir: Arak',
        # https://api.waqi.info/search/?token=your-token&keyword=london
        # in order to find your city uid's
        'identities': [11238, 10788, 11258, 10588],
        # thumbnail is optional
        'thumbnail': '',
    },
    {
        'id': 1,
        'name': ':flag_ro: Bucharest',
        'identities': [7655, 7656, 7657, 8590],
    },
    {
        'id': 2,
        'name': ':flag_ir: Tehran',
        'identities': [10652, 14774, 10653, 7716],
    },
    {
        'id': 3,
        'name': ':flag_ru: Moscow',
        'identities': [13060, 13618, 3330, 13617],
    },
]


BASE_DATA = {
    'username': '000: AIR QUALITY',
    'avatar_url': 'https://cdn.discordapp.com/attachments/731174051170746500/845965980935913482/000.png',
}


AIR_ATTRS = ['h', 'w', 't', 'co', 'no2', 'so2', 'pm25', 'pm10', 'o3']
ATTR_MAP = {
    'h': 'Humidity', 'w': 'Wind ', 't': 'Temperature',
    'co': 'Carbon Monoxide', 'no2': 'Nitrogen Dioxide', 'so2': 'Sulfur Dioxide',
    'pm25': 'PM-2.5', 'pm10': 'PM-10', 'o3': 'Ozone'
}
