# Nico

send air qaulity status to discord.

## Installation

install the requirements

```bash
python -m pip install -r requirements.txt
```

make a `secrets.json` file with in main.py dir \
then put your configs in it.

```json
{
    "TOKEN": "your-api.waqi.info-token",
    "WEBHOOKS": []
}
```

next move the services into `/etc/systemd/system/` like this:

```bash
mv services/* /etc/systemd/system/
```

modify your **nico.service** file and your are good to go.

```bash
systemctl start nico.timer
systemctl enable nico.timer
```
