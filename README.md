# 🤖 Telegram Channel Archiver & Real-Time Monitor

A powerful Python tool to archive Telegram channel messages and monitor channels in real-time with automatic media downloads.

## 🌟 Features

### 📚 Batch Archiver (`run_archiver.py`)
- Archive messages from multiple channels at once
- Download images, videos, and documents automatically
- Generate clean markdown files with embedded media
- Configurable date ranges and message limits
- Metadata tracking with JSON files

### 🎧 Real-Time Monitor (`telegram_monitor.py`)
- **Live monitoring** of channel messages as they arrive
- **Instant archiving** of new messages
- **Real-time media downloads**
- **Daily log files** organized by channel
- **Background operation** with graceful shutdown

### 🎛️ Easy Control (`monitor_control.py`)
- Start/stop monitoring with simple commands
- Check status and statistics
- View recent activity logs
- Restart monitoring easily

## 🚀 Quick Start

### 1. Setup API Credentials
1. Get credentials from https://my.telegram.org/apps
2. Update `config.json` with your API ID and Hash

### 2. Configure Channels
Edit `config.json` to add your channels:
```json
{
  "channels": [
    {
      "identifier": "@channelname",
      "name": "Channel Name",
      "enabled": true
    }
  ]
}
```

### 3. Choose Your Mode

#### 📚 Batch Archive (one-time)
```bash
# Archive recent messages from all channels
python run_archiver.py
```

#### 🎧 Real-Time Monitoring (continuous)
```bash
# Start monitoring (runs in background)
python monitor_control.py start

# Check status
python monitor_control.py status

# Stop monitoring
python monitor_control.py stop
```

## 📁 Output Structure

### Batch Archive
```
archived_channels/
├── Channel_Name/
│   ├── media/
│   │   ├── msg_123.jpg
│   │   └── msg_124.mp4
│   ├── Channel_Name_2024-01-15_14-30-00.md
│   └── Channel_Name_2024-01-15_14-30-00_metadata.json
```

### Live Monitor
```
live_archive/
├── Channel_Name/
│   ├── media/
│   │   ├── msg_456.jpg
│   │   └── msg_457.pdf
│   └── Channel_Name_2024-01-15_live.md
```

## ⚙️ Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `messages_per_channel` | Max messages per batch archive | 100 |
| `days_back` | Days back for batch archive | 7 |
| `download_media` | Download images/videos/docs | true |

## 🎯 Use Cases

### 📊 Research & Analysis
- Archive channels for later analysis
- Download media for offline viewing
- Track message patterns over time

### 🔔 Real-Time Alerts
- Monitor important channels live
- Never miss critical updates
- Automatic backup of all content

### 📱 Content Curation
- Collect content from multiple sources
- Organize by channel and date
- Search through markdown files easily

## 🛠️ Commands Reference

### Batch Archiver
```bash
python run_archiver.py          # Archive all enabled channels
python test_setup.py            # Test your setup
```

### Real-Time Monitor
```bash
python monitor_control.py start    # Start monitoring
python monitor_control.py stop     # Stop monitoring
python monitor_control.py status   # Show status & stats
python monitor_control.py logs     # Show recent activity
python monitor_control.py restart  # Restart monitoring
```

### Direct Monitor (advanced)
```bash
python telegram_monitor.py      # Run monitor directly (foreground)
```

## 📋 Requirements

- Python 3.7+
- Telethon library
- Telegram API credentials (user application, not bot)

## 🔒 Privacy & Security

- Uses official Telegram API
- No data sent to third parties
- All files stored locally
- Session files encrypted by Telethon

## 🆘 Troubleshooting

### Common Issues

**"Could not find the input entity"**
- Ensure you're a member of the channel
- Check channel identifier format
- For private channels, use full invite link

**"API access restricted"**
- Make sure you're using user application credentials (not bot)
- Get credentials from my.telegram.org/apps

**Monitor not starting**
- Check if already running: `python monitor_control.py status`
- Verify config.json is valid
- Check API credentials

### Getting Help

1. Run `python test_setup.py` to verify setup
2. Check console output for specific errors
3. Verify channel access in Telegram app
4. Ensure API credentials are correct

## 🔄 Automation Ideas

- **Cron jobs**: Schedule batch archives
- **Systemd service**: Run monitor as system service  
- **Docker**: Containerized deployment
- **GitHub Actions**: Cloud-based automation

Example systemd service:
```ini
[Unit]
Description=Telegram Channel Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/archiver
ExecStart=/path/to/venv/bin/python telegram_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Future Enhancements

- Web dashboard for monitoring
- Message filtering and search
- Export to different formats
- Integration with databases
- Webhook notifications