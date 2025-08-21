"""
This module contains the main PyWaBot class for interacting with the WhatsApp API.
"""
import os
import asyncio
import time
import logging
import base64
import binascii
import inspect
import functools
from typing import Callable, Coroutine, Any, Dict, Optional, List, Tuple, Union

from .internal import api_client, websocket_client
from . import types
from .exceptions import PyWaBotConnectionError

# Type alias for handler functions for better readability
MessageHandler = Callable[..., Coroutine[Any, Any, None]]

logger = logging.getLogger(__name__)

ENCODED_URL = 'GA0DERFVW3ARBAoeAA0sRgQJGVQEBBAZES1eFREdAQE8HwwWHlcCEUwdFTYfEgILSxUvGw=='
XOR_KEY = 'pywabot_secret_key'


def _get_api_url() -> str:
    """
    Decrypts and returns the API URL.

    Returns:
        str: The decrypted API URL.

    Raises:
        ValueError: If the decrypted URL is invalid.
    """
    try:
        encrypted_url_bytes = base64.b64decode(ENCODED_URL)
        key_bytes = XOR_KEY.encode('utf-8')
        decrypted_bytes = bytes(
            [
                b ^ key_bytes[i % len(key_bytes)]
                for i, b in enumerate(encrypted_url_bytes)
            ]
        )
        decrypted_url = decrypted_bytes.decode('utf-8')

        logger.debug("Decryption attempt resulted in URL: '%s'", decrypted_url)

        if not decrypted_url.startswith('http'):
            logger.warning(
                "Decryption resulted in an invalid URL ('%s').", decrypted_url
            )
            raise ValueError("Decrypted URL is not a valid HTTP/S link.")

        return decrypted_url
    except (binascii.Error, ValueError) as e:
        logger.error("Failed to decode or validate the API URL: %s.", e)
        # Re-raise as a more generic error to avoid leaking implementation details
        raise ValueError("Could not determine a valid API URL.") from e


class PyWaBot:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    An asynchronous Python wrapper for the Baileys WhatsApp API.
    """
    def __init__(self, session_name: str, api_key: str):
        """
        Initializes the PyWaBot instance.

        Args:
            session_name (str): The name for the WhatsApp session.
            api_key (str): The API key for authentication.

        Raises:
            ValueError: If `session_name` or `api_key` is not provided.
        """
        if not session_name:
            raise ValueError("A session_name must be provided.")
        if not api_key:
            raise ValueError("An api_key must be provided.")

        self.session_name = session_name
        self.api_key = api_key
        self.api_url = _get_api_url()

        # Create a session context for API calls
        self._session_context = api_client.SessionContext(
            api_url=self.api_url,
            api_key=self.api_key,
            session_name=self.session_name,
        )

        self.websocket_url = self.api_url.replace('https', 'wss')
        self.is_connected = False
        self._command_handlers: Dict[str, MessageHandler] = {}
        self._default_handler: Optional[MessageHandler] = None
        self._user_states: Dict[str, Any] = {}
        self._image_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._video_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._audio_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._document_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._sticker_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._contact_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._location_handlers: List[Tuple[MessageHandler, Optional[Any]]] = []
        self._group_participants_update_handlers: List[Callable] = []
        self.me: Optional[Dict[str, Any]] = None
        self.bot_id: Optional[str] = None
        self.bot_lid: Optional[str] = None

    def set_user_state(self, chat_id: str, state: Any):
        """
        Sets the state for a specific user/chat.

        Args:
            chat_id (str): The chat JID (e.g., '6281234567890@s.whatsapp.net').
            state (Any): The state to set for the user. Can be a string, dict, etc.
        """
        self._user_states[chat_id] = state
        logger.debug("State set for %s: %s", chat_id, state)

    def get_user_state(self, chat_id: str) -> Optional[Any]:
        """
        Retrieves the state for a specific user/chat.

        Args:
            chat_id (str): The chat JID.

        Returns:
            The user's state, or None if no state is set.
        """
        return self._user_states.get(chat_id)

    def clear_user_state(self, chat_id: str) -> bool:
        """
        Clears the state for a specific user/chat.

        Args:
            chat_id (str): The chat JID.

        Returns:
            bool: True if a state was cleared, False otherwise.
        """
        if chat_id in self._user_states:
            del self._user_states[chat_id]
            logger.debug("State cleared for %s.", chat_id)
            return True
        return False

    def handle_msg(self, command: str) -> Callable[[MessageHandler], MessageHandler]:
        """
        A decorator to register a handler for a specific command.
        """
        def decorator(func: MessageHandler) -> MessageHandler:
            sig = inspect.signature(func)
            num_params = len(sig.parameters)

            if num_params not in [1, 2]:
                raise TypeError(
                    f"Handler for command '{command}' must accept 1 or 2 arguments, "
                    f"but it accepts {num_params}."
                )

            @functools.wraps(func)
            async def wrapper(_: Any, message: types.WaMessage) -> None:
                if num_params == 1:
                    await func(message)
                else:
                    await func(_, message)

            self._command_handlers[command] = wrapper
            return func
        return decorator

    def on_message(self, func: MessageHandler) -> MessageHandler:
        """
        A decorator to register a default handler for any incoming message.
        """
        sig = inspect.signature(func)
        num_params = len(sig.parameters)

        if num_params not in [1, 2]:
            raise TypeError(
                f"Default message handler must accept 1 or 2 arguments, "
                f"but it accepts {num_params}."
            )

        @functools.wraps(func)
        async def wrapper(_: Any, message: types.WaMessage) -> None:
            if num_params == 1:
                await func(message)
            else:
                await func(_, message)

        self._default_handler = wrapper
        return func

    def on_location(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for location messages."""
        return self._create_handler_decorator(
            self._location_handlers, "location", user_state
        )

    def _create_handler_decorator(
        self,
        handler_list: List[Tuple[MessageHandler, Optional[Any]]],
        media_type: str,
        user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """A factory to create decorators for media handlers."""
        def wrapper(func: MessageHandler) -> MessageHandler:
            sig = inspect.signature(func)
            num_params = len(sig.parameters)

            if num_params not in [1, 2]:
                raise TypeError(
                    f"Handler for {media_type} must accept 1 or 2 arguments, "
                    f"but it accepts {num_params}."
                )

            @functools.wraps(func)
            async def inner_wrapper(_: Any, message: types.WaMessage) -> None:
                if num_params == 1:
                    await func(message)
                else:
                    await func(_, message)

            handler_list.append((inner_wrapper, user_state))
            return func
        return wrapper

    def on_image(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for image messages."""
        return self._create_handler_decorator(
            self._image_handlers, "image", user_state
        )

    def on_video(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for video messages."""
        return self._create_handler_decorator(
            self._video_handlers, "video", user_state
        )

    def on_audio(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for audio messages."""
        return self._create_handler_decorator(
            self._audio_handlers, "audio", user_state
        )

    def on_document(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for document messages."""
        return self._create_handler_decorator(
            self._document_handlers, "document", user_state
        )

    def on_sticker(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for sticker messages."""
        return self._create_handler_decorator(
            self._sticker_handlers, "sticker", user_state
        )

    def on_contact(
        self, user_state: Optional[Any] = None
    ) -> Callable[[MessageHandler], MessageHandler]:
        """Decorator to register a handler for contact messages."""
        return self._create_handler_decorator(
            self._contact_handlers, "contact", user_state
        )

    def on_group_participants_update(self, handler: Callable) -> Callable:
        """
        Decorator for group participants update events.
        """
        self._group_participants_update_handlers.append(handler)
        return handler

    async def _execute_stateful_handlers(
        self,
        handlers: List[Tuple[MessageHandler, Optional[Any]]],
        message: types.WaMessage
    ) -> bool:
        """
        Executes handlers that match the user's current state.
        Prioritizes handlers with a specific state match. If none match,
        executes handlers with no state requirement.
        """
        user_state = self.get_user_state(message.chat)

        # First, look for a specific state match
        for handler, required_state in handlers:
            if required_state is not None and required_state == user_state:
                await handler(self, message)
                return True  # Specific handler found and executed

        # If no specific state handler was found, run generic handlers
        executed_generic = False
        for handler, required_state in handlers:
            if required_state is None:
                await handler(self, message)
                executed_generic = True

        return executed_generic

    async def _handle_group_participant_update(self, msg_raw: Dict[str, Any]):
        """Handles group participant update events."""
        try:
            jid = msg_raw.get('key', {}).get('remoteJid')
            stub_params = msg_raw.get('messageStubParameters', [])
            participants = []
            if stub_params and isinstance(stub_params[0], str):
                participants = stub_params
            action_type = msg_raw.get('messageStubType')

            action_map = {
                "GROUP_PARTICIPANT_ADD": "add",
                "GROUP_PARTICIPANT_REMOVE": "remove",
                "GROUP_PARTICIPANT_LEAVE": "remove",
                "GROUP_PARTICIPANT_PROMOTE": "promote",
                "GROUP_PARTICIPANT_DEMOTE": "demote"
            }
            action = action_map.get(action_type)

            if jid and action and participants:
                logger.info(
                    "Detected group participant update for JID %s: Action=%s, Participants=%s",
                    jid, action, participants
                )
                for handler in self._group_participants_update_handlers:
                    asyncio.create_task(
                        handler(jid=jid, action=action, participants=participants)
                    )
        except (KeyError, IndexError) as e:
            logger.error("Error processing group participant update stub: %s", e)

    async def _handle_media_message(self, msg: types.WaMessage) -> bool:
        """Handles media messages."""
        media_handlers_map = {
            'image': self._image_handlers,
            'video': self._video_handlers,
            'audio': self._audio_handlers,
            'document': self._document_handlers,
            'sticker': self._sticker_handlers,
            'contact': self._contact_handlers,
            'location': self._location_handlers,
        }
        for media_type, handlers in media_handlers_map.items():
            if getattr(msg, media_type) and handlers:
                if await self._execute_stateful_handlers(handlers, msg):
                    return True
        return False

    async def _handle_text_message(self, msg: types.WaMessage):
        """Handles text messages and commands."""
        if msg.text:
            clean_text = msg.text.strip()
            for command, handler in self._command_handlers.items():
                if clean_text.startswith(command):
                    await handler(self, msg)
                    return

        if self._default_handler and msg.is_pure_text():
            await self._default_handler(self, msg)
            return

        logger.debug("No handler found for message ID %s.", msg.id)

    async def _process_incoming_event(self, event: Dict[str, Any]):
        """
        Processes any incoming event from the WebSocket.
        It can be a message, a group update, etc.
        """
        if 'messages' in event and event.get('type') in ['append', 'notify']:
            for msg_raw in event['messages']:
                if msg_raw.get('message') and 'groupInviteMessage' \
                        in msg_raw['message']:
                    continue

                message_content = msg_raw.get('message', {})
                is_participant_update = 'messageStubType' in msg_raw

                if not message_content and is_participant_update:
                    await self._handle_group_participant_update(msg_raw)
                    continue

                msg = types.WaMessage(event)
                if msg.from_me:
                    return

                if await self._handle_media_message(msg):
                    return

                if msg.is_media():
                    logger.debug("Media message ID %s was not handled.", msg.id)
                    return

                await self._handle_text_message(msg)

        elif event.get('event') == 'group:participants:update':
            data = event.get('data', {})
            jid = data.get('jid')
            action = data.get('action')
            participants = data.get('participants')

            if not (jid and action and participants):
                logger.warning("Received incomplete group update event: %s", data)
                return

            logger.info(
                "Group event received for JID %s: Action=%s, Participants=%s",
                jid, action, participants
            )
            for handler in self._group_participants_update_handlers:
                asyncio.create_task(
                    handler(jid=jid, action=action, participants=participants)
                )

    async def connect(self) -> bool:
        """
        Connects to the Baileys server and establishes a WhatsApp session.
        """
        server_status = await api_client.get_server_status(self._session_context)
        if server_status in ['offline', 'uninitialized']:
            success, _ = await api_client.start_server_session(self._session_context)
            if not success:
                return False
            return await self.wait_for_connection(timeout=15)

        if server_status == 'connected':
            # If already connected, we still need to run the setup to get 'me'
            return await self.wait_for_connection(timeout=5)

        return await self.wait_for_connection(timeout=15)

    async def request_pairing_code(self, phone_number: str) -> Optional[str]:
        """Requests a pairing code for linking a new device."""
        if self.is_connected:
            logger.warning(
                "Cannot request pairing code, bot is already connected."
            )
            return None
        return await api_client.request_pairing_code(
            self._session_context, phone_number
        )

    async def wait_for_connection(self, timeout: int = 60) -> bool:
        """Waits for the WhatsApp connection to be established."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = await api_client.get_server_status(self._session_context)
                if status == 'connected':
                    self.is_connected = True
                    self.me = await api_client.get_me(self._session_context)
                    if not self.me or 'id' not in self.me:
                        logger.error(
                            "Connection successful, but failed to fetch bot's JID from /me "
                            "endpoint. Response: %s", self.me
                        )
                        return False
                    self.bot_id = self.me.get('id')
                    raw_lid = self.me.get('lid')
                    if raw_lid:
                        self.bot_lid = raw_lid.split(
                            ':'
                        )[0] + '@lid' if '@lid' in raw_lid else None
                        logger.info(
                            "Bot connected. JID: %s, Normalized LID: %s",
                            self.bot_id, self.bot_lid
                        )
                    else:
                        self.bot_lid = None
                        logger.info(
                            "Bot connected. JID: %s, LID: Not available", self.bot_id
                        )
                    return True
                if status == 'server_offline':
                    return False
            except PyWaBotConnectionError:
                pass
            await asyncio.sleep(2)
        self.is_connected = False
        return False

    async def send_message(
        self,
        recipient_jid: str,
        text: str,
        reply_chat: Optional[types.WaMessage] = None,
        mentions: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Sends a text message to a specified JID."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        response = await api_client.send_message_to_server(
            self._session_context, recipient_jid, text, reply_chat, mentions
        )
        return response.get('data') if response and response.get('success') else None

    async def send_mention(
        self,
        jid: str,
        text: str,
        mentions: List[str],
        reply_chat: Optional[types.WaMessage] = None
    ) -> Optional[Dict[str, Any]]:
        """A convenience method to send a message with mentions."""
        return await self.send_message(
            jid, text, reply_chat=reply_chat, mentions=mentions
        )

    async def send_message_mention_all(
        self, jid: str, text: str, batch_size: int = 50, delay: int = 2
    ) -> bool:
        """Sends a message mentioning all participants in a group chat."""
        if not self.is_connected or not jid.endswith('@g.us'):
            return False

        metadata = await self.get_group_metadata(jid)
        if not metadata or not metadata.get('participants'):
            return False

        participant_jids = [
            p['id'] for p in metadata.get('participants', []) if p.get('id')
        ]
        if not participant_jids:
            return False

        for i in range(0, len(participant_jids), batch_size):
            batch_jids = participant_jids[i:i + batch_size]
            mention_text = " ".join([f"@{p_jid.split('@')[0]}" for p_jid in batch_jids])
            full_text = f"{text}\n\n{mention_text.strip()}"

            await self.typing(jid, duration=1)
            await self.send_message(jid, full_text, mentions=batch_jids)
            logger.info("Sent mention batch to %d members.", len(batch_jids))

            if i + batch_size < len(participant_jids):
                await asyncio.sleep(delay)
        return True

    async def typing(self, jid: str, duration: float = 1.0) -> None:
        """Simulates 'typing...' presence in a chat for a given duration."""
        if not self.is_connected:
            return
        await api_client.update_presence_on_server(
            self._session_context, jid, 'composing'
        )
        await asyncio.sleep(duration)
        await api_client.update_presence_on_server(
            self._session_context, jid, 'paused'
        )

    async def get_group_metadata(self, jid: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata for a specific group."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.get_group_metadata(self._session_context, jid)

    async def get_contact_info(self, jid: str) -> Optional[Dict[str, Any]]:
        """Retrieves profile information for a specific contact."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.get_contact_info(self._session_context, jid)

    async def is_bot_admin(self, group_id: str) -> bool:
        """
        Checks if the bot is an admin in a specific group using pre-fetched JID and LID.

        This simplified method relies on the bot_id and bot_lid attributes
        populated during the initial connection.

        Args:
            group_id (str): The JID of the group to check.

        Returns:
            bool: True if the bot is an admin, False otherwise.
        """
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        if not self.bot_id or not self.bot_lid:
            logger.error("Cannot check admin status: Bot JID/LID not available.")
            return False

        metadata = await self.get_group_metadata(group_id)
        if not metadata or 'participants' not in metadata:
            logger.warning("Could not get metadata for group %s.", group_id)
            return False

        admin_ids = {
            p['id'] for p in metadata.get('participants', [])
            if p.get('admin') in ('admin', 'superadmin')
        }

        # Check if either the bot's JID or its normalized LID is in the admin list
        if self.bot_id in admin_ids or self.bot_lid in admin_ids:
            logger.debug("Bot is admin in %s (ID match).", group_id)
            return True

        logger.info("Bot is not an admin in group %s.", group_id)
        return False

    async def forward_msg(
        self,
        recipient_jid: str,
        message_to_forward: types.WaMessage
    ) -> bool:
        """Forwards a given message to a recipient."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        if not message_to_forward or not message_to_forward.raw:
            return False
        return await api_client.forward_message_to_server(
            self._session_context,
            recipient_jid,
            message_to_forward.raw['messages'][0],
        )

    async def edit_msg(self, recipient_jid: str, message_id: str, new_text: str) -> bool:
        """Edits a message that was previously sent by the bot."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.edit_message_on_server(
            self._session_context, recipient_jid, message_id, new_text
        )

    async def delete_message(self, message_to_delete: types.WaMessage) -> bool:
        """Deletes a specific message for everyone."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        message_key = message_to_delete.key
        if not message_key:
            logger.error("Cannot delete message: message key is missing.")
            return False
        return await api_client.delete_message_on_server(
            self._session_context, message_to_delete.chat, message_key
        )

    async def mark_chat_as_read(self, message: types.WaMessage) -> bool:
        """Marks a specific message's chat as read."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.update_chat_on_server(
            self._session_context,
            message.chat,
            'read',
            message.raw['messages'][0],
        )

    async def mark_chat_as_unread(self, jid: str) -> bool:
        """Marks a chat as unread."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.update_chat_on_server(
            self._session_context, jid, 'unread'
        )

    async def send_poll(
        self,
        recipient_jid: str,
        name: str,
        values: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Sends a poll message."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        response = await api_client.send_poll_to_server(
            self._session_context, recipient_jid, name, values
        )
        return response.get('data') if response and response.get('success') else None

    async def download_media(self, message: types.WaMessage, path: str = '.') -> Optional[str]:
        """Downloads media (image, video, audio, document) from a message."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        media_message = (
            message.image or message.video or message.audio or message.document
        )
        if not media_message:
            return None

        media_data = await api_client.download_media_from_server(
            self._session_context, message.raw['messages'][0]
        )
        if media_data:
            ext = media_message.get('mimetype').split('/')[1].split(';')[0]
            filename = media_message.get('fileName') or f"{message.id}.{ext}"
            filepath = os.path.join(path, filename)
            with open(filepath, 'wb') as f:
                f.write(media_data)
            return filepath
        return None

    async def send_reaction(self, message: types.WaMessage, emoji: str) -> bool:
        """Sends a reaction to a specific message."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.send_reaction_to_server(
            self._session_context,
            message.chat,
            message.id,
            message.from_me,
            emoji,
        )

    async def update_group_participants(
        self,
        jid: str,
        action: str,
        participants: List[str]
    ) -> bool:
        """Updates group participants (add, remove, promote, demote)."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.update_group_participants(
            self._session_context, jid, action, participants
        )

    async def update_group_settings(self, jid: str, settings: Dict[str, bool]) -> bool:
        """
        Updates a group's settings.

        Args:
            jid (str): The group JID.
            settings (Dict[str, bool]): A dictionary with the setting to change.
                Example: `{"announcement": True}` to make the group announce-only,
                         `{"restrict": False}` to allow anyone to change group info.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")

        # Create the settings payload directly from the input
        # The key can be "announcement" or "restrict"
        valid_settings = {}
        if "announcement" in settings:
            valid_settings["announcement"] = settings["announcement"]
        if "restrict" in settings:
            valid_settings["restrict"] = settings["restrict"]
        # Compatibility for "locked" term used previously
        if "locked" in settings:
            valid_settings["restrict"] = settings["locked"]

        if not valid_settings:
            logger.error("Invalid group setting provided: %s", settings)
            return False

        response = await api_client.update_group_settings(
            self._session_context, jid, valid_settings
        )
        return response is not None and response.get('success', True)

    async def send_link_preview(
        self,
        recipient_jid: str,
        url: str,
        text: str
    ) -> Optional[Dict[str, Any]]:
        """Sends a message with a link preview."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        response = await api_client.send_link_preview_to_server(
            self._session_context, recipient_jid, url, text
        )
        return response.get('data') if response and response.get('success') else None

    async def _send_media(
        self,
        recipient_jid: str,
        message_payload: Dict[str, Any],
        timeout: int,
    ) -> Optional[Dict[str, Any]]:
        """Internal helper to send media messages."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        response = await api_client.send_media_to_server(
            self._session_context,
            recipient_jid,
            message_payload,
            timeout,
        )
        return response.get('data') if response and response.get('success') else None

    async def send_gif(
        self,
        recipient_jid: str,
        url: str,
        caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Sends a GIF message."""
        message_payload = {
            "video": {"url": url},
            "caption": caption,
            "gifPlayback": True,
        }
        return await self._send_media(recipient_jid, message_payload, timeout=30)

    async def send_image(
        self,
        recipient_jid: str,
        url: str,
        caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Sends an image message."""
        message_payload = {"image": {"url": url}, "caption": caption}
        return await self._send_media(recipient_jid, message_payload, timeout=30)

    async def send_sticker(
        self,
        recipient_jid: str,
        media: Union[str, bytes]
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a sticker message from an image URL or raw image bytes.

        Args:
            recipient_jid (str): The JID of the recipient.
            media (Union[str, bytes]): The URL of the image or the raw image bytes.
        """
        if isinstance(media, bytes):
            # Convert bytes to Base64 data URL
            b64_string = base64.b64encode(media).decode('utf-8')
            media_url = f"data:image/jpeg;base64,{b64_string}"
        elif isinstance(media, str) and media.startswith(('http://', 'https://')):
            media_url = media
        else:
            raise ValueError("Media must be a valid URL or a bytes object.")

        message_payload = {"sticker": {"url": media_url}}
        return await self._send_media(recipient_jid, message_payload, timeout=30)

    async def send_audio(
        self,
        recipient_jid: str,
        url: str,
        mimetype: str = 'audio/mp4'
    ) -> Optional[Dict[str, Any]]:
        """
        Sends an audio message with a specific mimetype.
        """
        if not url or not url.startswith(('http://', 'https://')):
            raise ValueError("URL must be a valid and publicly accessible.")
        if not mimetype or not mimetype.startswith('audio/'):
            raise ValueError("Invalid mimetype. Must be an audio type.")

        message_payload = {"audio": {"url": url}, "mimetype": mimetype}
        return await self._send_media(recipient_jid, message_payload, timeout=30)

    async def send_video(
        self,
        recipient_jid: str,
        url: str,
        caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Sends a video message."""
        message_payload = {"video": {"url": url}, "caption": caption}
        return await self._send_media(recipient_jid, message_payload, timeout=60)

    async def pin_chat(self, jid: str) -> bool:
        """Pins a chat to the top of the chat list."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.pin_unpin_chat_on_server(
            self._session_context, jid, True
        )

    async def unpin_chat(self, jid: str) -> bool:
        """Unpins a chat from the top of the chat list."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.pin_unpin_chat_on_server(
            self._session_context, jid, False
        )

    async def create_group(self, title: str, participants: List[str]) -> Optional[Dict[str, Any]]:
        """Creates a new group with the given title and participants."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Bot is not connected.")
        return await api_client.create_group_on_server(
            self._session_context, title, participants
        )

    @staticmethod
    async def list_sessions(api_key: str) -> Optional[Dict[str, Any]]:
        """Lists all available sessions on the Baileys API server."""
        if not api_key:
            raise ValueError("An api_key must be provided.")
        api_url = _get_api_url()
        if not api_url:
            return None
        return await api_client.list_sessions(api_url, api_key)

    @staticmethod
    async def delete_session(session_name: str, api_key: str) -> bool:
        """Deletes a specific session from the server."""
        if not api_key:
            raise ValueError("An api_key must be provided.")
        api_url = _get_api_url()
        if not api_url:
            return False
        logger.info("Requesting deletion of session: %s", session_name)
        return await api_client.delete_session(api_url, api_key, session_name)

    async def start_listening(self) -> None:
        """Starts listening for incoming messages via WebSocket."""
        if not self.is_connected:
            raise PyWaBotConnectionError("Cannot start listening, not connected.")
        # The callback is now _process_incoming_event to handle more than just messages
        await websocket_client.listen_for_messages(
            self.websocket_url,
            self.api_key,
            self.session_name,
            self._process_incoming_event
        )
