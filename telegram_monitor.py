#!/usr/bin/env python3
"""
Real-time Telegram Channel Monitor
Automatically archives new messages as they arrive in specified channels.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Set
import signal
import sys

from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat
from telegram_archiver import TelegramArchiver


class TelegramMonitor:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "monitor_session", download_media: bool = True):
        """
        Initialize the Telegram Monitor.
        
        Args:
            api_id: Your Telegram API ID
            api_hash: Your Telegram API Hash
            session_name: Name for the session file
            download_media: Whether to download images and media files
        """
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.archiver = TelegramArchiver(api_id, api_hash, session_name, download_media)
        self.output_dir = Path("live_archive")
        self.output_dir.mkdir(exist_ok=True)
        self.monitored_channels: Dict[int, str] = {}  # channel_id -> channel_name
        self.download_media = download_media
        self.running = False
        
    async def start(self):
        """Start the monitor client."""
        await self.client.start()
        await self.archiver.start()
        print("✅ Connected to Telegram for real-time monitoring!")
        
    async def stop(self):
        """Stop the monitor client."""
        self.running = False
        await self.client.disconnect()
        await self.archiver.stop()
        print("🛑 Monitor stopped")
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def add_channel_to_monitor(self, channel_identifier: str) -> bool:
        """
        Add a channel to the monitoring list.
        
        Args:
            channel_identifier: Channel username or link
            
        Returns:
            bool: Success status
        """
        try:
            entity = await self.client.get_entity(channel_identifier)
            if isinstance(entity, (Channel, Chat)):
                self.monitored_channels[entity.id] = entity.title
                print(f"📡 Now monitoring: {entity.title} (ID: {entity.id})")
                return True
            else:
                print(f"❌ {channel_identifier} is not a channel or chat")
                return False
        except Exception as e:
            print(f"❌ Error adding channel {channel_identifier}: {e}")
            return False
            
    async def save_single_message(self, message, channel_name: str):
        """
        Save a single message to the live archive.
        
        Args:
            message: Telegram message object
            channel_name: Name of the channel
        """
        try:
            # Create channel directory
            safe_channel_name = self.archiver.sanitize_filename(channel_name)
            channel_dir = self.output_dir / safe_channel_name
            channel_dir.mkdir(exist_ok=True)
            
            # Create media directory
            media_dir = channel_dir / "media"
            if self.download_media:
                media_dir.mkdir(exist_ok=True)
            
            # Download media if present
            media_path = None
            if message.media and self.download_media:
                media_path = await self.archiver.download_media_file(message, media_dir, message.id)
                if media_path:
                    print(f"   📥 Downloaded media for message {message.id}")
            
            # Create daily log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = channel_dir / f"{safe_channel_name}_{date_str}_live.md"
            
            # Check if this is a new file
            is_new_file = not log_file.exists()
            
            # Append message to daily log
            with open(log_file, 'a', encoding='utf-8') as f:
                if is_new_file:
                    # Write header for new file
                    f.write(f"# {channel_name} - Live Archive\n\n")
                    f.write(f"**Date:** {date_str}\n")
                    f.write(f"**Real-time monitoring started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("---\n\n")
                
                # Write the message
                markdown_content = self.archiver.format_message_as_markdown(message, channel_name, media_path)
                f.write(markdown_content)
                
            print(f"💾 Saved message {message.id} from {channel_name}")
            
        except Exception as e:
            print(f"❌ Error saving message {message.id}: {e}")
            
    async def setup_event_handlers(self):
        """Setup event handlers for new messages."""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handle new message events."""
            try:
                # Check if message is from a monitored channel
                if event.chat_id in self.monitored_channels:
                    channel_name = self.monitored_channels[event.chat_id]
                    
                    # Get message details
                    message = event.message
                    timestamp = message.date.strftime("%Y-%m-%d %H:%M:%S")
                    sender = "Unknown"
                    
                    if message.sender:
                        if hasattr(message.sender, 'first_name'):
                            sender = message.sender.first_name or "Unknown"
                        elif hasattr(message.sender, 'title'):
                            sender = message.sender.title
                    
                    # Show notification
                    text_preview = message.text[:50] + "..." if message.text and len(message.text) > 50 else message.text or "[Media/No text]"
                    print(f"\n🔔 NEW MESSAGE in {channel_name}")
                    print(f"   📅 {timestamp}")
                    print(f"   👤 {sender}")
                    print(f"   💬 {text_preview}")
                    
                    # Save the message
                    await self.save_single_message(message, channel_name)
                    
            except Exception as e:
                print(f"❌ Error handling new message: {e}")
                
        print("🎧 Event handlers set up successfully!")
        
    async def monitor_channels(self, channels: List[str]):
        """
        Start monitoring specified channels for new messages.
        
        Args:
            channels: List of channel identifiers to monitor
        """
        print(f"🚀 Setting up monitoring for {len(channels)} channels...")
        
        # Add channels to monitoring list
        successful_channels = 0
        for channel in channels:
            if await self.add_channel_to_monitor(channel):
                successful_channels += 1
                
        if successful_channels == 0:
            print("❌ No channels could be added to monitoring!")
            return
            
        print(f"✅ Successfully monitoring {successful_channels}/{len(channels)} channels")
        
        # Setup event handlers
        await self.setup_event_handlers()
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
        # Start monitoring
        self.running = True
        print(f"\n🎯 Real-time monitoring started!")
        print("📡 Listening for new messages...")
        print("💡 Press Ctrl+C to stop monitoring")
        print("=" * 50)
        
        try:
            # Keep the client running
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring interrupted by user")
        finally:
            await self.stop()
            
    def get_monitoring_stats(self) -> Dict:
        """Get statistics about the monitoring session."""
        stats = {
            "monitored_channels": len(self.monitored_channels),
            "channels": list(self.monitored_channels.values()),
            "output_directory": str(self.output_dir),
            "media_download_enabled": self.download_media
        }
        return stats


async def main():
    """Main function to run the monitor."""
    print("🎧 Telegram Channel Real-Time Monitor")
    print("=" * 50)
    
    # Load configuration
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config.json: {e}")
        return
        
    # Check API credentials
    api_id = config["api_credentials"]["api_id"]
    api_hash = config["api_credentials"]["api_hash"]
    
    if api_id == "YOUR_API_ID" or api_hash == "YOUR_API_HASH":
        print("❌ Please configure your API credentials in config.json!")
        return
        
    # Get enabled channels
    enabled_channels = [
        channel["identifier"] 
        for channel in config["channels"] 
        if channel.get("enabled", True)
    ]
    
    if not enabled_channels:
        print("❌ No enabled channels found in config.json!")
        return
        
    # Initialize monitor
    monitor = TelegramMonitor(
        api_id=int(api_id),
        api_hash=api_hash,
        session_name=config["api_credentials"]["session_name"] + "_monitor",
        download_media=config["archive_settings"].get("download_media", True)
    )
    
    try:
        await monitor.start()
        await monitor.monitor_channels(enabled_channels)
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
    finally:
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())