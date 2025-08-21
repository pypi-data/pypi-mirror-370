"""Data classes and type definitions for the PyWaBot library."""
# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class WaMessage:
    """
    A class representing a single WhatsApp message.
    This class needs many attributes to represent the complex structure of a message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, raw_message: Dict[str, Any], _is_quoted: bool = False):
        self.raw = raw_message
        self._msg_info = (
            raw_message.get('messages', [{}])[0]
            if raw_message.get('messages')
            else {}
        )

        self.key: Dict[str, Any] = self._msg_info.get('key', {})
        self.id: Optional[str] = self.key.get('id')
        self.chat: Optional[str] = self.key.get('remoteJid')
        self.from_me: bool = self.key.get('fromMe', False)
        self.sender: Optional[str] = self.key.get('participant') or self.chat

        self.sender_name: str = self._msg_info.get('pushName') or "Unknown"
        self.timestamp: Optional[int] = self._msg_info.get('messageTimestamp')

        self.message: Dict[str, Any] = self._msg_info.get('message') or {}
        ephemeral_msg = (
            self.message.get('ephemeralMessage', {}).get('message') or {}
        )
        self.text: Optional[str] = (
            self.message.get('conversation')
            or self.message.get('extendedTextMessage', {}).get('text')
            or ephemeral_msg.get('extendedTextMessage', {}).get('text')
            or self.message.get('imageMessage', {}).get('caption')
            or self.message.get('videoMessage', {}).get('caption')
            or self.message.get('locationMessage', {}).get('comment')
        )

        self.location: Optional[Dict[str, Any]] = self.message.get(
            'locationMessage'
        )
        self.document: Optional[Dict[str, Any]] = self.message.get(
            'documentMessage'
        )
        self.image: Optional[Dict[str, Any]] = self.message.get('imageMessage')
        self.video: Optional[Dict[str, Any]] = self.message.get('videoMessage')
        self.audio: Optional[Dict[str, Any]] = self.message.get('audioMessage')
        self.live_location: Optional[
            Dict[str, Any]
        ] = self.message.get('liveLocationMessage')
        self.sticker: Optional[Dict[str, Any]] = self.message.get('stickerMessage')
        self.contact: Optional[Dict[str, Any]] = self.message.get('contactMessage')
        self.quoted: Optional['WaMessage'] = None

        if not _is_quoted:
            context_info = None
            # The contextInfo can be in the main message dictionary or inside an ephemeral message
            message_containers = [self.message, ephemeral_msg]
            for container in message_containers:
                if not container:
                    continue
                for _, value in container.items():
                    if isinstance(value, dict) and 'contextInfo' in value:
                        context_info = value['contextInfo']
                        break
                if context_info:
                    break

            if context_info and context_info.get('quotedMessage'):
                fake_msg_info = {
                    'key': {
                        'remoteJid': self.chat,
                        'id': context_info.get('stanzaId'),
                        'fromMe': False,  # Quoted message is never "from me" in this context
                        'participant': context_info.get('participant'),
                    },
                    'message': context_info.get('quotedMessage'),
                    'pushName': None,  # Not available for quoted messages
                    'messageTimestamp': None,  # Not available for quoted messages
                }
                self.quoted = WaMessage(
                    {'messages': [fake_msg_info]}, _is_quoted=True
                )

    def get_location(self) -> Optional[Dict[str, Any]]:
        """Extracts standard location data from the message."""
        if self.location:
            return {
                'latitude': self.location.get('degreesLatitude'),
                'longitude': self.location.get('degreesLongitude'),
                'comment': self.location.get('comment'),
            }
        return None

    def get_live_location(self) -> Optional[Dict[str, Any]]:
        """Extracts live location data from the message."""
        if self.live_location:
            return {
                'latitude': self.live_location.get('degreesLatitude'),
                'longitude': self.live_location.get('degreesLongitude'),
                'caption': self.live_location.get('caption'),
                'speed': self.live_location.get('speedInMps'),
                'degrees': self.live_location.get('degrees'),
                'sequence': self.live_location.get('sequenceNumber'),
            }
        return None

    def is_media(self) -> bool:
        """Checks if the message contains any media type."""
        return any([
            self.image, self.video, self.audio, self.document,
            self.sticker, self.contact, self.location, self.live_location
        ])

    def is_pure_text(self) -> bool:
        """
        Checks if the message is purely text-based (not a caption for media).
        """
        return bool(
            (self.message.get('conversation') or
             self.message.get('extendedTextMessage')) and not self.is_media()
        )


class WaGroupMetadata:
    """
    A class representing metadata for a WhatsApp group.
    This class requires many attributes to detail group information.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, metadata: Dict[str, Any]):
        self.id: Optional[str] = metadata.get('id')
        self.owner: Optional[str] = metadata.get('owner')
        self.subject: Optional[str] = metadata.get('subject')
        self.creation: Optional[int] = metadata.get('creation')
        self.desc: Optional[str] = metadata.get('desc')
        self.participants: List[Dict[str, Any]] = metadata.get(
            'participants', []
        )

    def __str__(self) -> str:
        return f"Group: {self.subject} ({self.id})"


class PollMessage:
    """
    A class representing a poll message.
    This class requires many attributes to describe a poll.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, data: Dict[str, Any]):
        self.id: Optional[str] = data.get('id')
        self.chat: Optional[str] = data.get('chat')
        self.sender: Optional[str] = data.get('sender')
        self.name: Optional[str] = data.get('name')
        self.options: List[str] = data.get('options', [])
        self.selectable_options_count: Optional[int] = data.get(
            'selectableOptionsCount'
        )

    def __str__(self) -> str:
        return f"Poll: {self.name} with options: {self.options}"


class LinkPreview:
    """
    A class representing a link preview.
    This class requires many attributes to describe a link preview.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, data: Dict[str, Any]):
        self.id: Optional[str] = data.get('id')
        self.chat: Optional[str] = data.get('chat')
        self.sender: Optional[str] = data.get('sender')
        self.text: Optional[str] = data.get('text')
        self.url: Optional[str] = data.get('url')
        self.title: Optional[str] = data.get('title')
        self.description: Optional[str] = data.get('description')
        self.thumbnail_url: Optional[str] = data.get('thumbnailUrl')

    def __str__(self) -> str:
        return f"Link Preview: {self.title} ({self.url})"


@dataclass
class Gif:
    """Dataclass for sending a GIF."""

    url: str
    caption: Optional[str] = None


@dataclass
class Image:
    """Dataclass for sending an Image."""

    url: str
    caption: Optional[str] = None


@dataclass
class Audio:
    """Dataclass for sending an Audio file."""

    url: str
    mimetype: str


@dataclass
class Video:
    """Dataclass for sending a Video."""

    url: str
    caption: Optional[str] = None


@dataclass
class Document:
    """Dataclass for sending a Document."""

    url: str
    mimetype: str
    filename: str
    caption: Optional[str] = None
