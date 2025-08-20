#!/usr/bin/env python3
"""
Control script for the Telegram Monitor
Provides easy commands to start, stop, and check status of the monitor.
"""

import asyncio
import json
import subprocess
import sys
import os
import signal
from pathlib import Path


def load_config():
    """Load configuration from JSON file."""
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config.json: {e}")
        return None


def check_monitor_running():
    """Check if monitor is currently running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'telegram_monitor.py'], 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        # pgrep not available, try ps
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return 'telegram_monitor.py' in result.stdout, ""
        except:
            return False, ""


def start_monitor():
    """Start the monitor in background."""
    is_running, pid = check_monitor_running()
    if is_running:
        print(f"⚠️  Monitor is already running (PID: {pid})")
        return
        
    print("🚀 Starting Telegram Monitor...")
    
    # Start monitor in background
    try:
        process = subprocess.Popen([
            sys.executable, 'telegram_monitor.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Monitor started with PID: {process.pid}")
        print("📡 Real-time monitoring is now active!")
        print("💡 Use 'python monitor_control.py status' to check status")
        print("💡 Use 'python monitor_control.py stop' to stop monitoring")
        
    except Exception as e:
        print(f"❌ Error starting monitor: {e}")


def stop_monitor():
    """Stop the running monitor."""
    is_running, pid = check_monitor_running()
    if not is_running:
        print("ℹ️  Monitor is not running")
        return
        
    print("🛑 Stopping Telegram Monitor...")
    
    try:
        if pid:
            for p in pid.split('\n'):
                if p.strip():
                    os.kill(int(p.strip()), signal.SIGTERM)
                    print(f"✅ Stopped monitor process (PID: {p.strip()})")
        else:
            print("✅ Monitor stopped")
    except Exception as e:
        print(f"❌ Error stopping monitor: {e}")


def show_status():
    """Show monitor status and statistics."""
    print("📊 Telegram Monitor Status")
    print("=" * 30)
    
    # Check if running
    is_running, pid = check_monitor_running()
    if is_running:
        print(f"🟢 Status: RUNNING (PID: {pid})")
    else:
        print("🔴 Status: STOPPED")
    
    # Load config to show monitored channels
    config = load_config()
    if config:
        enabled_channels = [
            channel for channel in config["channels"] 
            if channel.get("enabled", True)
        ]
        print(f"📋 Configured channels: {len(enabled_channels)}")
        for channel in enabled_channels:
            print(f"   • {channel['name']}")
        
        print(f"📥 Media download: {'✅ Enabled' if config['archive_settings'].get('download_media', True) else '❌ Disabled'}")
    
    # Check live archive directory
    live_archive = Path("live_archive")
    if live_archive.exists():
        channel_dirs = [d for d in live_archive.iterdir() if d.is_dir()]
        print(f"📁 Live archive channels: {len(channel_dirs)}")
        
        total_files = 0
        for channel_dir in channel_dirs:
            md_files = list(channel_dir.glob("*.md"))
            total_files += len(md_files)
            if md_files:
                latest_file = max(md_files, key=lambda x: x.stat().st_mtime)
                print(f"   • {channel_dir.name}: {len(md_files)} files (latest: {latest_file.name})")
        
        print(f"📄 Total archive files: {total_files}")


def show_logs():
    """Show recent monitor logs."""
    print("📋 Recent Monitor Activity")
    print("=" * 30)
    
    live_archive = Path("live_archive")
    if not live_archive.exists():
        print("ℹ️  No live archive found")
        return
        
    # Find most recent log files
    all_md_files = []
    for channel_dir in live_archive.iterdir():
        if channel_dir.is_dir():
            md_files = list(channel_dir.glob("*_live.md"))
            all_md_files.extend(md_files)
    
    if not all_md_files:
        print("ℹ️  No live archive files found")
        return
        
    # Sort by modification time
    all_md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📄 Found {len(all_md_files)} live archive files")
    print("\n🕒 Recent activity:")
    
    for i, file_path in enumerate(all_md_files[:3]):  # Show last 3 files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                message_count = len([line for line in lines if line.startswith("## Message")])
                
            mod_time = file_path.stat().st_mtime
            from datetime import datetime
            mod_datetime = datetime.fromtimestamp(mod_time)
            
            print(f"   {i+1}. {file_path.parent.name}")
            print(f"      📄 {file_path.name}")
            print(f"      💬 {message_count} messages")
            print(f"      🕒 Last updated: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error reading {file_path.name}: {e}")


def main():
    """Main control function."""
    if len(sys.argv) < 2:
        print("🎧 Telegram Monitor Control")
        print("=" * 30)
        print("Usage:")
        print("  python monitor_control.py start   - Start real-time monitoring")
        print("  python monitor_control.py stop    - Stop monitoring")
        print("  python monitor_control.py status  - Show status and stats")
        print("  python monitor_control.py logs    - Show recent activity")
        print("  python monitor_control.py restart - Restart monitoring")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_monitor()
    elif command == "stop":
        stop_monitor()
    elif command == "status":
        show_status()
    elif command == "logs":
        show_logs()
    elif command == "restart":
        stop_monitor()
        import time
        time.sleep(2)  # Wait a bit
        start_monitor()
    else:
        print(f"❌ Unknown command: {command}")
        print("💡 Use 'python monitor_control.py' to see available commands")


if __name__ == "__main__":
    main()