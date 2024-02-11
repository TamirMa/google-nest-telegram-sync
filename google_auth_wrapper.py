import requests
from nest_api import NestDoorbellDevice 

from tools import logger
import glocaltokens.client

class GLocalAuthenticationTokensMultiService(glocaltokens.client.GLocalAuthenticationTokens):
    def __init__(self, *args, **kwargs) -> None:
        super(GLocalAuthenticationTokensMultiService, self).__init__(*args, **kwargs)

        self._last_access_token_service = None
    
    def get_access_token(self, service=glocaltokens.client.ACCESS_TOKEN_SERVICE) -> str | None:
        temp = glocaltokens.client.ACCESS_TOKEN_SERVICE

        glocaltokens.client.ACCESS_TOKEN_SERVICE = service
        if self._last_access_token_service != service:
            self.access_token_date = None
        res = super(GLocalAuthenticationTokensMultiService, self).get_access_token()
        self._last_access_token_service = service
        
        glocaltokens.client.ACCESS_TOKEN_SERVICE = temp

        return res

class GoogleConnection(object):

    NAME = "Google"

    NEST_SCOPE = "oauth2:https://www.googleapis.com/auth/nest-account"

    def __init__(self, master_token, username, password="FAKE_PASSWORD"):
        self._google_auth = GLocalAuthenticationTokensMultiService(
            master_token=master_token, 
            username=username, 
            password=password,
        )

    def make_nest_get_request(self, device_id : str, url : str, params={}):
        url = url.format(device_id=device_id)
        logger.debug(f"Sending request to: '{url}' with params: '{params}'")

        access_token = self._google_auth.get_access_token(service=GoogleConnection.NEST_SCOPE)
        if not access_token:
            raise Exception("Couldn't get a Nest access token")
        
        res = requests.get(
            url=url, 
            params=params, 
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        res.raise_for_status()
        return res.content

    def get_nest_camera_devices(self):

        homegraph_response = self._google_auth.get_homegraph()

        # This one will list all your home devices
        # One of them would be your Nest Camera, let's find it
        return [
            NestDoorbellDevice(self, device.device_info.agent_info.unique_id, device.device_name)
            for device in homegraph_response.home.devices
            if "action.devices.traits.CameraStream" in device.traits and "Nest" in device.hardware.model
        ]
