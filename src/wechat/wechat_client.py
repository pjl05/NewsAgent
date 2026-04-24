"""WeChat API client for sending messages and managing access tokens."""

import logging
import time
from typing import Any, Dict, Optional

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class WeChatAPIError(Exception):
    """Raised when a WeChat API call fails."""

    def __init__(self, message: str, errcode: Optional[int] = None, errmsg: Optional[str] = None):
        super().__init__(message)
        self.errcode = errcode
        self.errmsg = errmsg


class WeChatClient:
    """Client for interacting with the WeChat API.

    Provides methods for obtaining access tokens and sending
    customer service messages to WeChat users.
    """

    TOKEN_EXPIRY_SECONDS: int = 7200  # WeChat access tokens expire after ~2 hours

    def __init__(self) -> None:
        """Initialize the WeChat client.

        Reads credentials from application settings.
        """
        settings = get_settings()
        self._app_id: str = settings.wechat_app_id
        self._app_secret: str = settings.wechat_app_secret
        self._base_url: str = "https://api.weixin.qq.com/cgi-bin"
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def get_access_token(self) -> str:
        """Obtain a WeChat API access token, using the cached value if still valid.

        WeChat access tokens expire after approximately 2 hours. This method
        returns the cached token if it has not yet expired, otherwise it
        fetches a fresh token from the WeChat API and caches it.

        Returns:
            str: A valid WeChat API access token.

        Raises:
            WeChatAPIError: If the token request fails or the API returns an error.
        """
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = f"{self._base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self._app_id,
            "secret": self._app_secret,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data: Dict[str, Any] = response.json()

            errcode = data.get("errcode")
            if errcode and errcode != 0:
                errmsg = data.get("errmsg", "Unknown error")
                logger.error("WeChat token request failed: errcode=%s, errmsg=%s", errcode, errmsg)
                raise WeChatAPIError(
                    f"Failed to obtain access token: {errmsg}",
                    errcode=errcode,
                    errmsg=errmsg,
                )

            token = data.get("access_token")
            if not token:
                logger.error("WeChat token response missing access_token field: %s", data)
                raise WeChatAPIError("Access token missing in API response")

            expires_in = data.get("expires_in", self.TOKEN_EXPIRY_SECONDS)
            self._access_token = token
            self._token_expires_at = time.time() + expires_in - 60  # Refresh 60s early

            logger.info("Obtained new WeChat access token, expires in %s seconds", expires_in)
            return self._access_token

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error during WeChat token request: %s", e)
            raise WeChatAPIError(f"HTTP error during token request: {e}") from e
        except httpx.RequestError as e:
            logger.error("Request error during WeChat token request: %s", e)
            raise WeChatAPIError(f"Request error during token request: {e}") from e

    def send_message(self, openid: str, content: str) -> Dict[str, Any]:
        """Send a text message to a WeChat user.

        Args:
            openid: The WeChat OpenID of the recipient user.
            content: The text content of the message to send.

        Returns:
            Dict containing the API response. Typically includes an 'errcode' field
            where 0 indicates success.

        Raises:
            WeChatAPIError: If the message send fails or the API returns an error.
        """
        token = self.get_access_token()
        url = f"{self._base_url}/message/custom/send?access_token={token}"
        payload: Dict[str, Any] = {
            "touser": openid,
            "msgtype": "text",
            "text": {"content": content},
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                result: Dict[str, Any] = response.json()

            errcode = result.get("errcode")
            if errcode and errcode != 0:
                errmsg = result.get("errmsg", "Unknown error")
                logger.error(
                    "WeChat send_message failed: openid=%s, errcode=%s, errmsg=%s",
                    openid,
                    errcode,
                    errmsg,
                )
                raise WeChatAPIError(
                    f"Failed to send message: {errmsg}",
                    errcode=errcode,
                    errmsg=errmsg,
                )

            logger.info("Successfully sent WeChat message to openid=%s", openid)
            return result

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error sending WeChat message: %s", e)
            raise WeChatAPIError(f"HTTP error sending message: {e}") from e
        except httpx.RequestError as e:
            logger.error("Request error sending WeChat message: %s", e)
            raise WeChatAPIError(f"Request error sending message: {e}") from e
