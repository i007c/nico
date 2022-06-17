# Nico

send air qaulity status to discord.

## Installation

install the requirements

```bash
python -m pip install -r requirements.txt
```

next move the services into `/etc/systemd/system/` like this:

```bash
mv services/* /etc/systemd/system/
```

make a `configs.py` file with in app.py dir \
then put your configs in it.

```py

TOKEN = 'your-api.waqi.info-token'

WEBHOOKS = [
    # your webhooks
]

CITIES = [
    {
        'name': 'City Name',
        # use this url https://api.waqi.info/search/?token=your-token&keyword=london
        # in order to find your city uid's
        'identities': [11238, 10788, 11258, 10588],
        # thumbnail is optional
        'thumbnail': 'image url',
    }
]


BASE_DATA = {
    'username': 'Webhooks name',
    'avatar_url': 'url of a picture',
}


AIR_ATTRS = ['p', 'h', 'w', 't', 'co', 'no2', 'so2', 'pm25', 'pm10', 'o3']
ATTR_MAP = {
    'p': 'Pressure 🟩', 'h': 'Humidity 💦', 'w': 'Wind 💨', 't': 'Temperature 🥵',
    'co': 'Carbon Monoxide', 'no2': 'Nitrogen Dioxide', 'so2': 'Sulfur Dioxide',
    'pm25': 'PM-2.5', 'pm10': 'PM-10',
    'o3': 'Ozone'
}

```

modify your **nico.service** file and your are good to go.

```bash
systemctl start nico.timer
systemctl enable nico.timer
```

## Todos

* [ ] making this app in **C** just for fun.
