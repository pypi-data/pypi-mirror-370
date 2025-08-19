import os
import json
import time
import sys
from datetime import datetime, timedelta
from dateutil.tz import tzutc
from aiwb.utils.console import console, err_console

import logging
from aiwb.utils import CACHE_DIR, can_launch_browser, open_page_in_browser

logger = logging.getLogger(__name__)


def _utc_now():
    return datetime.now(tzutc())


class AIWBTokenProvider:
    METHOD = "aiwb"

    def __init__(self, client, time_fetcher=_utc_now):
        self._client = client
        self._now = time_fetcher
        self._cache_dir = CACHE_DIR
        self._oidc_url = os.getenv(
            "AIWB_OIDC_URL",
            self._client.url,
        )

    @property
    def _client_id(self):
        return os.getenv(
            "AIWB_OIDC_CLIENT_ID",
            "aiwb_workbench",
        )

    @property
    def _cache_key(self):
        return os.path.join(self._cache_dir, "token.json")

    def _save_token(self, res):
        try:
            file_content = json.dumps(res)
        except (TypeError, ValueError):
            logger.exception(
                "Value cannot be cached, must be JSON serializable: %s", res
            )
            raise

        if not os.path.isdir(self._cache_dir):
            os.makedirs(self._cache_dir)

        with os.fdopen(
            os.open(self._cache_key, os.O_WRONLY | os.O_CREAT, 0o600), "w"
        ) as f:
            f.truncate()
            f.write(file_content)

    def _wait_for_token(self, device_code):
        now = _utc_now()
        while True:
            if now < _utc_now() - timedelta(seconds=180):
                logger.error("timeout for waiting device token...")
                return

            logger.debug("waiting for device token...")
            data = {
                "client_id": self._client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }

            res, err = self._client.request(
                f"{self._oidc_url}/api/auth/token", "POST", json=data, timeout=300
            )
            if not err:
                self._save_token(res)
                console.out("Successfully retrieve device token.")
                sys.exit(0)
            logger.debug("Error in retrieve token {}".format(res.get("message")))
            time.sleep(3)

        err_console.out(res.get("message"))
        sys.exit(1)

    def revoke_token(self, token=None):
        if token is None:
            token = self.load_token().get("access_token")

        data = {"client_id": self._client_id, "token": token}
        res, err = self._client.request(
            f"{self._oidc_url}/api/auth/revoke_token", "POST", json=data, timeout=300
        )
        if not err:
            with os.fdopen(
                os.open(self._cache_key, os.O_WRONLY | os.O_CREAT, 0o600), "w"
            ) as f:
                f.truncate()
            console.out("Successfully revoke device token.")
            sys.exit(0)
        err_console.out(res.get("message"))
        sys.exit(1)
        
    def get_user_info(self):
        token = self._client.load_auth_token()
        res, err = self._client.request(
            f"{self._oidc_url}/api/auth/userinfo", headers={"Authorization": f"Bearer {token.get('access_token')}"}, timeout=300
        )
        return res, err

    def user_info(self):
        res, err = self.get_user_info()
        if not err:
            console.print_json(json.dumps(res))
            sys.exit(0)
        err_console.out(res.get("message"))
        sys.exit(1)

    def generate_token(self):
        data = {"client_id": self._client_id, "scopes": "openid email profile"}
        res, err = self._client.request(
            f"{self._oidc_url}/api/auth/device/code", "POST", json=data, timeout=300
        )
        if not err:
            device_code = res.get("device_code")
            user_code = res.get("user_code")
            url = f"{self._oidc_url}/device-activate?user-code={user_code}"
            console.out(
                "Attempting to automatically open the workbench authorization page in your default browser."
            )
            console.out(
                f"If the browser does not popup, you can open the following URL: {url}"
            )
            if can_launch_browser():
                open_page_in_browser(url)
            self._wait_for_token(device_code)
        err_console.out(res.get("message"))
        sys.exit(1)

    def load_token(self):
        """Loads token from local cache file."""
        if os.path.isdir(self._cache_dir):
            f = open(self._cache_key, encoding="utf-8")
            try:
                token = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return {}
            if token:
                return token
            f.close()

        return {}
