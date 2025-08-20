#!/usr/bin/env python3
"""
Telegram Channel Archiver
Automatically fetches messages from Telegram channels and saves them as markdown files.
"""

import asyncio
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User, MessageMediaPhoto, MessageMediaDocument


class TelegramArchiver:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "archiver_session", download_media: bool = True):
        """
        Initialize the Telegram Archiver.
        
        Args:
            api_id: Your Telegram API ID
            api_hash: Your Telegram API Hash
            session_name: Name for the session file
            download_media: Whether to download images and media files
        """
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.output_dir = Path("archived_channels")
        self.output_dir.mkdir(exist_ok=True)
        self.download_media = download_media
        
    async def start(self):
        """Start the Telegram client."""
        await self.client.start()
        print("✅ Connected to Telegram!")
        
    async def stop(self):
        """Stop the Telegram client."""
        await self.client.disconnect()
        
    def sanitize_filename(self, text: str) -> str:
        """Sanitize text for use as filename."""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', text)
        # Limit length
        return sanitized[:100] if len(sanitized) > 100 else sanitized
        
    async def download_media_file(self, message, media_dir: Path, message_id: int) -> Optional[str]:
        """
        Download media from a message and return the relative file path.
        
        Args:
            message: Telegram message object
            media_dir: Directory to save media files
            message_id: Message ID for unique naming
            
        Returns:
            str: Relative path to downloaded file, or None if no media/download failed
        """
        if not message.media or not self.download_media:
            return None
            
        try:
            # Create media directory if it doesn't exist
            media_dir.mkdir(exist_ok=True)
            
            # Generate a unique filename based on message ID and media hash
            file_extension = ""
            file_prefix = f"msg_{message_id}"
            
            if isinstance(message.media, MessageMediaPhoto):
                file_extension = ".jpg"
            elif isinstance(message.media, MessageMediaDocument):
                if message.media.document:
                    # Try to get original filename
                    for attr in message.media.document.attributes:
                        if hasattr(attr, 'file_name') and attr.file_name:
                            original_name = attr.file_name
                            file_extension = Path(original_name).suffix
                            break
                    
                    # Fallback to mime type
                    if not file_extension and message.media.document.mime_type:
                        mime_to_ext = {
                            'image/jpeg': '.jpg',
                            'image/png': '.png',
                            'image/gif': '.gif',
                            'image/webp': '.webp',
                            'video/mp4': '.mp4',
                            'video/webm': '.webm',
                            'application/pdf': '.pdf',
                            'text/plain': '.txt'
                        }
                        file_extension = mime_to_ext.get(message.media.document.mime_type, '.bin')
            
            # Create unique filename
            filename = f"{file_prefix}{file_extension}"
            file_path = media_dir / filename
            
            # Download the media
            print(f"   📥 Downloading media: {filename}")
            downloaded_path = await self.client.download_media(message, file=str(file_path))
            
            if downloaded_path:
                # Return relative path for markdown
                return f"media/{filename}"
            else:
                print(f"   ❌ Failed to download media for message {message_id}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error downloading media for message {message_id}: {e}")
            return None
        
    def format_message_as_markdown(self, message, channel_name: str, media_path: Optional[str] = None) -> str:
        """Convert a Telegram message to markdown format."""
        # Message header
        timestamp = message.date.strftime("%Y-%m-%d %H:%M:%S")
        sender = "Unknown"
        
        if message.sender:
            if hasattr(message.sender, 'first_name'):
                sender = message.sender.first_name or "Unknown"
                if hasattr(message.sender, 'last_name') and message.sender.last_name:
                    sender += f" {message.sender.last_name}"
            elif hasattr(message.sender, 'title'):
                sender = message.sender.title
                
        markdown_content = f"## Message {message.id}\n\n"
        markdown_content += f"**Channel:** {channel_name}\n"
        markdown_content += f"**Sender:** {sender}\n"
        markdown_content += f"**Date:** {timestamp}\n"
        markdown_content += f"**Message ID:** {message.id}\n\n"
        
        # Message content
        if message.text:
            # Clean up the text and preserve formatting
            text = message.text.strip()
            markdown_content += f"### Content\n\n{text}\n\n"
            
        # Handle media
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                if media_path:
                    markdown_content += f"**Media:** 📷 Photo\n\n![Photo]({media_path})\n\n"
                else:
                    markdown_content += "**Media:** 📷 Photo\n\n"
            elif isinstance(message.media, MessageMediaDocument):
                if message.media.document:
                    file_name = "Unknown"
                    for attr in message.media.document.attributes:
                        if hasattr(attr, 'file_name') and attr.file_name:
                            file_name = attr.file_name
                            break
                    
                    if media_path:
                        # Check if it's an image document
                        if message.media.document.mime_type and message.media.document.mime_type.startswith('image/'):
                            markdown_content += f"**Media:** 📷 Image Document ({file_name})\n\n![{file_name}]({media_path})\n\n"
                        else:
                            markdown_content += f"**Media:** 📎 Document ({file_name})\n\n[Download {file_name}]({media_path})\n\n"
                    else:
                        markdown_content += f"**Media:** 📎 Document ({file_name})\n\n"
            else:
                markdown_content += f"**Media:** {type(message.media).__name__}\n\n"
                
        # Handle forwarded messages
        if message.forward:
            markdown_content += "**Forwarded Message**\n\n"
            
        # Handle replies
        if message.reply_to:
            markdown_content += f"**Reply to:** Message {message.reply_to.reply_to_msg_id}\n\n"
            
        markdown_content += "---\n\n"
        return markdown_content
        
    async def get_channel_info(self, channel_identifier: str) -> Dict:
        """Get information about a channel."""
        try:
            entity = await self.client.get_entity(channel_identifier)
            if isinstance(entity, Channel):
                return {
                    "id": entity.id,
                    "title": entity.title,
                    "username": entity.username,
                    "type": "channel"
                }
            elif isinstance(entity, Chat):
                return {
                    "id": entity.id,
                    "title": entity.title,
                    "username": None,
                    "type": "chat"
                }
            else:
                raise ValueError(f"Entity {channel_identifier} is not a channel or chat")
        except Exception as e:
            print(f"❌ Error getting channel info for {channel_identifier}: {e}")
            return None
            
    async def archive_channel_messages(self, 
                                     channel_identifier: str, 
                                     limit: int = 100,
                                     days_back: int = 7) -> bool:
        """
        Archive messages from a specific channel.
        
        Args:
            channel_identifier: Channel username (with @) or invite link
            limit: Maximum number of messages to fetch
            days_back: How many days back to fetch messages
            
        Returns:
            bool: Success status
        """
        try:
            print(f"📥 Fetching messages from {channel_identifier}...")
            
            # Get channel info
            channel_info = await self.get_channel_info(channel_identifier)
            if not channel_info:
                return False
                
            channel_name = channel_info["title"]
            print(f"📋 Channel: {channel_name}")
            
            # Calculate date range (timezone-aware)
            from datetime import timezone
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_back)
            
            # Create channel directory
            safe_channel_name = self.sanitize_filename(channel_name)
            channel_dir = self.output_dir / safe_channel_name
            channel_dir.mkdir(exist_ok=True)
            
            # Create media directory
            media_dir = channel_dir / "media"
            if self.download_media:
                media_dir.mkdir(exist_ok=True)
            
            # Fetch messages
            messages = []
            async for message in self.client.iter_messages(
                channel_identifier, 
                limit=limit,
                offset_date=end_date
            ):
                if message.date < start_date:
                    break
                messages.append(message)
                
            if not messages:
                print(f"📭 No messages found in the specified date range")
                return True
                
            print(f"📨 Found {len(messages)} messages")
            
            # Create markdown file
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{safe_channel_name}_{date_str}.md"
            filepath = channel_dir / filename
            
            # Write messages to markdown file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {channel_name}\n\n")
                f.write(f"**Archive Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Messages:** {len(messages)}\n")
                f.write(f"**Date Range:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n")
                f.write("---\n\n")
                
                # Sort messages by date (oldest first)
                messages.sort(key=lambda x: x.date)
                
                # Process messages and download media
                media_downloads = 0
                for message in messages:
                    # Download media if present
                    media_path = None
                    if message.media and self.download_media:
                        media_path = await self.download_media_file(message, media_dir, message.id)
                        if media_path:
                            media_downloads += 1
                    
                    # Generate markdown content
                    markdown_content = self.format_message_as_markdown(message, channel_name, media_path)
                    f.write(markdown_content)
                    
            print(f"✅ Saved {len(messages)} messages to {filepath}")
            if self.download_media and media_downloads > 0:
                print(f"📥 Downloaded {media_downloads} media files to {media_dir}")
            
            # Save metadata
            metadata = {
                "channel_info": channel_info,
                "archive_date": datetime.now().isoformat(),
                "message_count": len(messages),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "file_path": str(filepath)
            }
            
            metadata_file = channel_dir / f"{safe_channel_name}_{date_str}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"❌ Error archiving channel {channel_identifier}: {e}")
            return False
            
    async def archive_multiple_channels(self, 
                                      channels: List[str], 
                                      limit: int = 100,
                                      days_back: int = 7):
        """Archive messages from multiple channels."""
        print(f"🚀 Starting archive process for {len(channels)} channels...")
        
        results = {}
        for channel in channels:
            print(f"\n📂 Processing {channel}...")
            success = await self.archive_channel_messages(channel, limit, days_back)
            results[channel] = success
            
        # Summary
        print(f"\n📊 Archive Summary:")
        successful = sum(1 for success in results.values() if success)
        print(f"✅ Successful: {successful}/{len(channels)}")
        
        for channel, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {channel}")


async def main():
    """Main function to run the archiver."""
    # You need to get these from https://my.telegram.org/apps
    API_ID = "YOUR_API_ID"  # Replace with your API ID
    API_HASH = "YOUR_API_HASH"  # Replace with your API Hash
    
    if API_ID == "YOUR_API_ID" or API_HASH == "YOUR_API_HASH":
        print("❌ Please set your API_ID and API_HASH in the script!")
        print("Get them from: https://my.telegram.org/apps")
        return
        
    # Initialize archiver
    archiver = TelegramArchiver(API_ID, API_HASH)
    
    try:
        await archiver.start()
        
        # Example channels to archive (replace with your channels)
        channels_to_archive = [
            "@example_channel",  # Channel username
            "https://t.me/another_channel",  # Channel link
            # Add more channels here
        ]
        
        # Archive messages from the last 7 days, max 100 messages per channel
        await archiver.archive_multiple_channels(
            channels=channels_to_archive,
            limit=100,
            days_back=7
        )
        
    finally:
        await archiver.stop()


if __name__ == "__main__":
    asyncio.run(main())