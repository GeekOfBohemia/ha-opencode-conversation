"""Config flow for OpenCode Conversation."""

from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME

from .const import (
    API_HEALTH,
    CONF_AGENT,
    CONF_MODEL,
    CONF_SYSTEM_PROMPT,
    DEFAULT_AGENT,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default="http://localhost:4096"): str,
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
        vol.Optional(CONF_AGENT, default=DEFAULT_AGENT): str,
        vol.Optional(CONF_SYSTEM_PROMPT, default=DEFAULT_SYSTEM_PROMPT): str,
    }
)


class OpenCodeConversationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenCode Conversation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            user_input[CONF_URL] = url
            try:
                await self._async_validate(url, user_input)
            except aiohttp.ClientError as err:
                _LOGGER.warning("OpenCode server unreachable: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - config flow reports any failure
                _LOGGER.exception("Unexpected error checking OpenCode server")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="OpenCode", data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _async_validate(self, url: str, data: dict) -> None:
        """Validate the server is reachable and healthy."""
        auth = None
        if data.get(CONF_PASSWORD):
            auth = aiohttp.BasicAuth(
                data.get(CONF_USERNAME, DEFAULT_USERNAME),
                data[CONF_PASSWORD],
            )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{url}{API_HEALTH}", auth=auth, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                health = await resp.json()
                if not health.get("healthy"):
                    raise aiohttp.ClientError("Server reported unhealthy")
