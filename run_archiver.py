#!/usr/bin/env python3
"""
Simple runner script for the Telegram Archiver using config.json
"""

import asyncio
import json
from pathlib import Path
from telegram_archiver import TelegramArchiver


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_path} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        return None


async def main():
    """Main function."""
    print("🤖 Telegram Channel Archiver")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    if not config:
        return
        
    # Check API credentials
    api_id = config["api_credentials"]["api_id"]
    api_hash = config["api_credentials"]["api_hash"]
    
    if api_id == "YOUR_API_ID" or api_hash == "YOUR_API_HASH":
        print("❌ Please configure your API credentials in config.json!")
        print("Get them from: https://my.telegram.org/apps")
        print("\n📝 Steps to get API credentials:")
        print("1. Go to https://my.telegram.org/apps")
        print("2. Log in with your phone number")
        print("3. Create a new application")
        print("4. Copy the API ID and API Hash to config.json")
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
        
    print(f"📋 Found {len(enabled_channels)} enabled channels:")
    for channel in config["channels"]:
        if channel.get("enabled", True):
            status = "✅"
            print(f"  {status} {channel['name']} ({channel['identifier']})")
        
    # Initialize archiver
    try:
        archiver = TelegramArchiver(
            api_id=int(api_id),
            api_hash=api_hash,
            session_name=config["api_credentials"]["session_name"],
            download_media=config["archive_settings"].get("download_media", True)
        )
    except ValueError:
        print("❌ Error: 'api_id' in config.json must be an integer. Please check your config file.")
        return
    
    try:
        await archiver.start()
        
        # Archive channels
        await archiver.archive_multiple_channels(
            channels=enabled_channels,
            limit=config["archive_settings"]["messages_per_channel"],
            days_back=config["archive_settings"]["days_back"]
        )
        
        print(f"\n🎉 Archive complete! Check the '{config['archive_settings']['output_directory']}' folder.")
        
    except Exception as e:
        print(f"❌ Error during archiving: {e}")
    finally:
        await archiver.stop()


if __name__ == "__main__":
    asyncio.run(main())