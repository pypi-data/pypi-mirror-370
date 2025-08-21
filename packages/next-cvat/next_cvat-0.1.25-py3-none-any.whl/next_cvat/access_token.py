from __future__ import annotations

import base64
import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Dict

from pydantic import BaseModel


class AccessToken(BaseModel):
    """Represents a CVAT access token with session and authentication data."""

    sessionid: str
    csrftoken: str
    api_key: str
    expires_at: datetime

    @classmethod
    def from_client_cookies(cls, cookies: Dict, headers: Dict) -> AccessToken:
        """Create an AccessToken from CVAT client cookies and headers."""
        # For basic auth, there might not be an Authorization header
        # In this case, we'll use the session-based authentication
        api_key = headers.get("Authorization", "session-based-auth")

        # Extract expires from sessionid cookie (Morsel object)
        sessionid_cookie = cookies["sessionid"]
        expires_str = sessionid_cookie.get("expires")
        if expires_str:
            expires_at = parsedate_to_datetime(expires_str)
        else:
            # Fallback to a reasonable default if no expires is set
            from datetime import datetime, timedelta

            expires_at = datetime.now() + timedelta(days=14)

        return cls(
            sessionid=str(sessionid_cookie.value),
            csrftoken=str(cookies["csrftoken"].value),
            api_key=api_key,
            expires_at=expires_at,
        )

    def serialize(self) -> str:
        """Serialize the token to a base64-encoded string."""
        token_data = {
            "sessionid": self.sessionid,
            "csrftoken": self.csrftoken,
            "api_key": self.api_key,
            "expires_at": self.expires_at.isoformat(),
        }
        return base64.b64encode(json.dumps(token_data).encode()).decode()

    @classmethod
    def deserialize(cls, token_string: str) -> AccessToken:
        """Create an AccessToken from a base64-encoded string."""
        try:
            token_data = json.loads(base64.b64decode(token_string).decode())
            return cls(
                sessionid=token_data["sessionid"],
                csrftoken=token_data["csrftoken"],
                api_key=token_data["api_key"],
                expires_at=datetime.fromisoformat(token_data["expires_at"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid token format: {e}") from e

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now() > self.expires_at
