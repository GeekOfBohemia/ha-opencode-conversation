"""Conversation agent that talks to an opencode server."""

from __future__ import annotations

import logging
from typing import Literal

import aiohttp

from homeassistant.components import conversation
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationEntityFeature,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er, intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    API_MESSAGE,
    API_SESSION,
    CONF_AGENT,
    CONF_MODEL,
    CONF_SYSTEM_PROMPT,
    DEFAULT_AGENT,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    DOMAIN,
    TIMEOUT_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the OpenCode Conversation entities."""
    async_add_entities([OpenCodeConversationEntity(hass, config_entry)])


class OpenCodeConversationEntity(
    ConversationEntity, conversation.AbstractConversationAgent
):
    """OpenCode conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = ConversationEntityFeature.CONTROL

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = entry.entry_id

        self._base_url: str = entry.data["url"].rstrip("/")
        self._username: str = entry.data.get("username", "opencode")
        self._password: str = entry.data.get("password", "")
        self._model: str = entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        self._agent: str = entry.data.get(CONF_AGENT, DEFAULT_AGENT)
        self._system_prompt: str = entry.data.get(
            CONF_SYSTEM_PROMPT, DEFAULT_SYSTEM_PROMPT
        )

        self._session_ids: dict[str, str] = {}

        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="OpenCode server",
            manufacturer="OpenCode",
            model="opencode serve",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return MATCH_ALL

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a conversation by calling the opencode server."""
        language = user_input.language or self.hass.config.language
        conversation_id = user_input.conversation_id
        session_id = None

        try:
            session_id = await self._async_get_or_create_session(conversation_id)
            text = await self._async_send_message(session_id, user_input.text)
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.error("OpenCode conversation failed: %s", err)
            response = intent.IntentResponse(language=language)
            response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Sorry, I had a problem talking to OpenCode.",
            )
            return conversation.ConversationResult(
                response=response, conversation_id=conversation_id
            )

        response = intent.IntentResponse(language=language)
        response.async_set_speech(text)
        return conversation.ConversationResult(
            response=response, conversation_id=conversation_id
        )

    def _auth(self) -> aiohttp.BasicAuth | None:
        """Return basic auth for the opencode server."""
        if self._password:
            return aiohttp.BasicAuth(self._username, self._password)
        return None

    async def _async_get_or_create_session(self, conversation_id: str | None) -> str:
        """Reuse an opencode session for a HA conversation or create a new one."""
        if conversation_id and conversation_id in self._session_ids:
            return self._session_ids[conversation_id]

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}{API_SESSION}",
                json={"title": "home-assistant"},
                auth=self._auth(),
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
        session_id = data.get("id")
        if not session_id:
            raise RuntimeError("No session id returned by opencode server")

        if conversation_id:
            self._session_ids[conversation_id] = session_id
        return session_id

    async def _async_send_message(self, session_id: str, text: str) -> str:
        """Send a message to an opencode session and return the text reply."""
        payload: dict = {"parts": [{"type": "text", "text": text}]}
        if self._model:
            payload["model"] = {
                "providerID": self._model.split("/", 1)[0],
                "modelID": self._model.split("/", 1)[1],
            }
        if self._agent:
            payload["agent"] = self._agent
        if self._system_prompt:
            payload["system"] = self._system_prompt
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}{API_MESSAGE.format(session_id=session_id)}",
                json=payload,
                auth=self._auth(),
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        texts = [
            part.get("text")
            for part in data.get("parts", [])
            if part.get("type") == "text" and part.get("text")
        ]
        if not texts:
            return ""
        return "\n".join(texts).strip()
