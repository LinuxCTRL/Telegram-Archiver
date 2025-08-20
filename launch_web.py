#!/usr/bin/env python3
"""
Quick launcher for the Telegram Archive Web Frontend
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path


def check_archives():
    """Check if there are any archives to display."""
    archive_dirs = ["archived_channels", "live_archive"]
    has_archives = False
    
    for archive_dir in archive_dirs:
        path = Path(archive_dir)
        if path.exists():
            for channel_dir in path.iterdir():
                if channel_dir.is_dir() and list(channel_dir.glob("*.md")):
                    has_archives = True
                    break
    
    return has_archives


def main():
    """Launch the web frontend."""
    print("🚀 Launching Telegram Archive Web Frontend...")
    print("=" * 50)
    
    # Check if archives exist
    if not check_archives():
        print("⚠️  No archives found!")
        print("💡 Run one of these first:")
        print("   • python run_archiver.py          (batch archive)")
        print("   • python monitor_control.py start (real-time monitoring)")
        print()
        
        choice = input("Continue anyway? (y/N): ").lower().strip()
        if choice != 'y':
            print("👋 Exiting...")
            return
    
    print("🌐 Starting web server...")
    print("📱 The web interface will open automatically")
    print("🔍 Features available:")
    print("   • Browse all archived channels")
    print("   • Search across all messages")
    print("   • View embedded media")
    print("   • Download files")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the web server
        process = subprocess.Popen([
            sys.executable, 'web_frontend.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        # Show server output
        for line in process.stdout:
            print(line.strip())
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web server...")
        process.terminate()
        print("👋 Web frontend stopped")
    except Exception as e:
        print(f"❌ Error starting web frontend: {e}")


if __name__ == "__main__":
    main()