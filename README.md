
# Google Nest Camera Videos <--> Telegram Channel

This is a module created after a joyfull project I've researched. 
You can find the full story [here](https://medium.com/@tamirmayer/google-nest-camera-internal-api-fdf9dc3ce167)

If you wan't to download your Google Home Nest Cameras videos locally (And tired of paying the monthly Nest Aware Subscription) - this is the script your are looking for.

I found it no-where else.

Specifically I needed to send the videos to a Telegram Channel, but feel free to do whatever you need with that.

This module is for personal use only. Using it is at your own risk!
## You Will Be Able To:

- Get your **Google Home devices using HomeGraph**
- Retrieve your recent **Google Nest events**
- **Download full-quality Google Nest video clips**
- Send those clips to a Telegram channel you choose


## Usage:

* Start with:
```bash
  pip install -r requirements.txt
```

* Get a Google "Master Token", you may consider to use a Google One-Time Password for that:

```bash
  docker run --rm -it breph/ha-google-home_get-token
```

* Create a .env file in the following format

```dotenv
GOOGLE_MASTER_TOKEN="aas_..."
GOOGLE_USERNAME="youremailaddress@gmail.com"
TELEGRAM_BOT_TOKEN="token..."
TELEGRAM_CHANNEL_ID="-100..."
```

* Then run:

```bash
  python3 main.py
```


## Example:

```javascript
from google_auth_wrapper import GoogleConnection

google_connection = GoogleConnection(
    GOOGLE_MASTER_TOKEN, 
    GOOGLE_USERNAME
)

nest_camera_devices = google_connection.get_nest_camera_devices()

for nest_device in self._nest_camera_devices:
    # Get all the events
    events = nest_device.get_events(
            end_time = pytz.timezone("US/Central").localize(datetime.datetime.now()),
            duration_minutes=3 * 60 # 3 Hours
        )

    for event in events:
        # Returns the bytes of the .mp4 video
        video_data = nest_device.download_camera_event(event)
        
```


## Credits:

Much credits for the authors of the [**glocaltokens**](https://github.com/leikoilja/glocaltokens) module

Thanks also for the authors of the docker [**ha-google-home_get-token**](https://hub.docker.com/r/breph/ha-google-home_get-token)
