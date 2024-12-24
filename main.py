from dotenv import load_dotenv
from tools import logger
from google_auth_wrapper import GoogleConnection
import pytz
import os
import datetime
import secrets
import string

load_dotenv()  # take environment variables from .env.
GOOGLE_MASTER_TOKEN = os.getenv("GOOGLE_MASTER_TOKEN")
GOOGLE_USERNAME = os.getenv("GOOGLE_USERNAME")
assert GOOGLE_MASTER_TOKEN and GOOGLE_USERNAME

def generate_random_string(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    logger.info("Initializing the Google connection using the master_token")
    google_connection = GoogleConnection(GOOGLE_MASTER_TOKEN, GOOGLE_USERNAME)

    logger.info("Getting Camera Devices")
    nest_camera_devices = google_connection.get_nest_camera_devices()
    
    for nest_device in nest_camera_devices:
        # Get all the events
        events = nest_device.get_events(
            end_time = pytz.timezone("US/Central").localize(datetime.datetime.now()),
            duration_minutes= 4*60 # 3 Hours
        )
        
        print(events)
        for event in events:
            # Returns the bytes of the .mp4 video
            video_data = nest_device.download_camera_event(event)
            rand_str = generate_random_string()

            # Create a directory called 'Videos' if it doesn't exist
            videos_dir_path = os.path.join(os.getcwd(), 'Videos')
            os.makedirs(videos_dir_path, exist_ok=True)

            # Save the video data to a file in the 'Videos' directory
            with open(os.path.join(videos_dir_path, f"{rand_str}.mp4"), 'wb') as f:
                print(os.path.join(videos_dir_path, f"{rand_str}.mp4"))
                f.write(video_data)
    
if __name__ == "__main__":
    main()