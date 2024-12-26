import datetime
import requests
from nest_api import NestDevice

from tools import logger
import glocaltokens.client

class GLocalAuthenticationTokensMultiService(glocaltokens.client.GLocalAuthenticationTokens):
    def __init__(self, *args, **kwargs) -> None:
        super(GLocalAuthenticationTokensMultiService, self).__init__(*args, **kwargs)

        self._last_access_token_service = None

    @staticmethod
    def _escape_username(username: str) -> str:
        """Escape plus sign for some exotic accounts."""
        return username.replace("+", "%2B")
    
    def get_access_token(self, service=glocaltokens.client.ACCESS_TOKEN_SERVICE) -> str :
        """Return existing or fetch access_token"""
        try:
            if (
                self.access_token is None
                or self.access_token_date is None
                or self._has_expired(self.access_token_date, glocaltokens.client.ACCESS_TOKEN_DURATION)
                or self._last_access_token_service != service
            ):
                logger.debug("Access token is missing, expired, or not for the requested service. Fetching a new one...")
                master_token = self.get_master_token()
                if master_token is None:
                    logger.error("Unable to obtain master token. Authentication failed.")
                    return None
                if self.username is None:
                    logger.error("Username is not set. Authentication failed.")
                    return None

                res = glocaltokens.client.perform_oauth(
                    self._escape_username(self.username),
                    master_token,
                    self.get_android_id(),
                    app=glocaltokens.client.ACCESS_TOKEN_APP_NAME,
                    service=service,
                    client_sig=glocaltokens.client.ACCESS_TOKEN_CLIENT_SIGNATURE,
                )
                if "Auth" not in res:
                    logger.error("[!] Failed to fetch access token. Response: %s", res)
                    return None

                self.access_token = res["Auth"]
                self.access_token_date = datetime.datetime.now()
                self._last_access_token_service = service

            logger.debug("Access token retrieved successfully. Token timestamp: %s", self.access_token_date)
            return self.access_token
        except Exception as e:
            logger.exception("An error occurred while fetching the access token: %s", e)
            return None


class GoogleConnection:
    NAME = "Google"
    NEST_SCOPE = "oauth2:https://www.googleapis.com/auth/nest-account"

    def __init__(self, master_token, username, password="FAKE_PASSWORD"):
        if not master_token or not username:
            raise ValueError("Master token and username are required.")

        self._google_auth = GLocalAuthenticationTokensMultiService(
            master_token=master_token,
            username=username,
            password=password,
        )

    def make_nest_get_request(self, device_id: str, url: str, params=None):
        """Make a secure GET request to the Nest API."""
        if not device_id or not url:
            raise ValueError("Device ID and URL must be provided.")
        if not url.startswith("https://"):
            raise ValueError("URL must use HTTPS for secure communication.")

        params = params or {}
        url = url.format(device_id=device_id)
        logger.debug("Sending request to: '%s' with params: '%s'", url, params)

        access_token = self._google_auth.get_access_token(service=self.NEST_SCOPE)
        if not access_token:
            raise Exception("Couldn't obtain a valid Nest access token.")

        try:
            response = requests.get(
                url=url,
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
                verify=True,  # Ensures SSL certificate validation
            )
            response.raise_for_status()
            logger.debug("Request successful. Response: %s", response.content)
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", e)
            raise

    def get_nest_camera_devices(self):
        """Retrieve all Nest Camera devices from the user's home graph."""
        try:
            homegraph_response = self._google_auth.get_homegraph()
            if not homegraph_response or not hasattr(homegraph_response, "home"):
                logger.error("Invalid or empty HomeGraph response.")
                return []

            devices = [
                NestDevice(self, device.device_info.agent_info.unique_id, device.device_name)
                for device in homegraph_response.home.devices
                if "action.devices.traits.CameraStream" in device.traits
                and "Nest" in device.hardware.model
            ]
            logger.debug("Found %d Nest Camera devices.", len(devices))
            return devices
        except Exception as e:
            logger.error("Error retrieving Nest Camera devices: %s", e)
            return []
