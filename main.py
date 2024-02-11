from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from tools import logger
from google_auth_wrapper import GoogleConnection
from telegram_sync import TelegramEventsSync

import os
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


GOOGLE_MASTER_TOKEN = os.getenv("GOOGLE_MASTER_TOKEN")
GOOGLE_USERNAME = os.getenv("GOOGLE_USERNAME")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

assert GOOGLE_MASTER_TOKEN and GOOGLE_USERNAME and TELEGRAM_CHANNEL_ID and TELEGRAM_BOT_TOKEN

REFRESH_EVERY_X_MINUTES=2


def main():

    logger.info("Welcome to the Google Nest Doorbell <-> Telegram Syncer")

    logger.info("Initializing the Google connection using the master_token")
    google_connection = GoogleConnection(GOOGLE_MASTER_TOKEN, GOOGLE_USERNAME)

    logger.info("Getting Camera Devices")
    nest_camera_devices = google_connection.get_nest_camera_devices()
    logger.info(f"Found {len(nest_camera_devices)} Camera Device{'s' if len(nest_camera_devices) > 1 else ''}")

    tes = TelegramEventsSync(
        telegram_bot_token=TELEGRAM_BOT_TOKEN, 
        telegram_channel_id=TELEGRAM_CHANNEL_ID, 
        nest_camera_devices=nest_camera_devices
    )

    logger.info("Initialized a Telegram Syncer")

    # Schedule the job to run every x minutes
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        tes.sync, 
        'interval', 
        minutes=REFRESH_EVERY_X_MINUTES, 
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10)
    )
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

    
if __name__ == "__main__":
    main()