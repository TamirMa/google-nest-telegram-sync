from dotenv import load_dotenv
from tools import logger
from google_auth_wrapper import GoogleConnection
import pytz
import os
import datetime

def main(GOOGLE_MASTER_TOKEN, GOOGLE_USERNAME, VIDEO_SAVE_PATH):

    HOURS_TO_CHECK = 5

    logger.info("Initializing the Google connection using the master_token")
    google_connection = GoogleConnection(GOOGLE_MASTER_TOKEN, GOOGLE_USERNAME)

    logger.info("Getting Camera Devices")
    nest_camera_devices = google_connection.get_nest_camera_devices()
    
    for nest_device in nest_camera_devices:
        # Get all the events
        events = nest_device.get_events(
            end_time = pytz.timezone("US/Central").localize(datetime.datetime.now()),
            
            # I THINK THERE'S AN ERROR HERE. TOWARDS THE END OF 3 HOURS, NO EVENTS ARE FOUND.
            duration_minutes= HOURS_TO_CHECK * 60 
        )
        
        for event in events:
            # Returns the bytes of the .mp4 video
            video_data = nest_device.download_camera_event(event)
            
            # Sanitize the filename to remove invalid characters
            safe_filename = f"{nest_device.device_name}-{int(event.start_time.timestamp()*1000)}.mp4"
            
            # Check if file already exists before saving
            safe_filename_with_ext = os.path.join(VIDEO_SAVE_PATH, safe_filename)
            if not os.path.exists(safe_filename_with_ext):
                with open(safe_filename_with_ext, 'wb') as f:
                    print(f"Saving video to {safe_filename_with_ext}")
                    f.write(video_data)

if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    GOOGLE_MASTER_TOKEN = os.getenv("GOOGLE_MASTER_TOKEN")
    GOOGLE_USERNAME = os.getenv("GOOGLE_USERNAME")
    VIDEO_SAVE_PATH = os.getenv("VIDEO_SAVE_PATH")
    assert GOOGLE_MASTER_TOKEN and GOOGLE_USERNAME and VIDEO_SAVE_PATH
    
    main(GOOGLE_MASTER_TOKEN, GOOGLE_USERNAME, VIDEO_SAVE_PATH)