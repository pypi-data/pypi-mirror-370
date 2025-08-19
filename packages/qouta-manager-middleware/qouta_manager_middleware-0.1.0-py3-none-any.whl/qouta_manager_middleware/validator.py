import jwt
import requests
from requests.exceptions import RequestException
import logging
from .constants import LOG_MESSAGES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LamehQoutaManagerMiddleware:

    def __init__(self, base_url, x_api_key):
        self.base_url = base_url
        self.x_api_key = x_api_key

    def _decode_jwt(self, token):
        try:
            payload = jwt.decode(
                token, options={"verify_signature": False}, algorithms=["RS256"]
            )
            print(payload)
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(LOG_MESSAGES["token_expired"] + f" Token: {token}")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(
                LOG_MESSAGES["invalid_token"] + f" Error: {str(e)} Token: {token}"
            )
            return None

    def _check_limit(self, sub, base_url):
        try:
            response = requests.get(
                f"{base_url}/subscriptions/{sub}/remaining_quota",
                params={"client_id": sub},
                headers={"X-API-Key": self.x_api_key},
            )
            response.raise_for_status()
            is_quota_available = response.json().get("is_quota_available", False)
            if is_quota_available:
                increase_quota_response = requests.post(
                    f"{base_url}/subscriptions/{sub}/increase_quota",
                    headers={"X-API-Key": self.x_api_key},
                )
                increase_quota_response.raise_for_status()
                return True
            return is_quota_available
        except RequestException as e:
            logger.error(
                LOG_MESSAGES["error_checking_limit"].format(e)
                + f" Client ID: {sub} Base URL: {base_url}"
            )
            return False

    def process_token(self, request):
        token = request.headers.get("Authorization")
        if token:
            token = token.replace("Bearer ", "")
            payload = self._decode_jwt(token)
            if payload and "sub" in payload:
                sub = payload["sub"]
                return self._check_limit(sub, self.base_url)
        return False
