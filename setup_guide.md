# Telegram Channel Archiver Setup Guide

## 📋 Prerequisites

1. **Python 3.7+** with virtual environment
2. **Telethon library** (already installed)
3. **Telegram API credentials**

## 🔑 Getting Telegram API Credentials

1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your phone number
3. Click "Create application"
4. Fill in the form:
   - **App title**: Something like "Channel Archiver"
   - **Short name**: Something like "archiver"
   - **Platform**: Desktop
   - **Description**: Personal channel archiver
5. Copy the **API ID** and **API Hash**

## ⚙️ Configuration

1. Open `config.json`
2. Replace `YOUR_API_ID` with your actual API ID (number)
3. Replace `YOUR_API_HASH` with your actual API Hash (string)
4. Add your channels to the `channels` array:

```json
{
  "identifier": "@channelname",
  "name": "Friendly Channel Name",
  "enabled": true
}
```

### Channel Identifier Formats

- **Username**: `@channelname` 
- **Invite link**: `https://t.me/channelname`
- **Private channel**: Use the invite link

## 🚀 Usage

### Basic Usage
```bash
# Activate virtual environment
source venv/bin/activate

# Run the archiver
python run_archiver.py
```

### Advanced Usage
```python
# Use the TelegramArchiver class directly
from telegram_archiver import TelegramArchiver

archiver = TelegramArchiver(API_ID, API_HASH)
await archiver.start()
await archiver.archive_channel_messages("@channel", limit=50, days_back=3)
await archiver.stop()
```

## 📁 Output Structure

```
archived_channels/
├── Channel_Name_1/
│   ├── Channel_Name_1_2024-01-15_14-30-00.md
│   └── Channel_Name_1_2024-01-15_14-30-00_metadata.json
└── Channel_Name_2/
    ├── Channel_Name_2_2024-01-15_14-30-00.md
    └── Channel_Name_2_2024-01-15_14-30-00_metadata.json
```

## 📝 Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `messages_per_channel` | Max messages to fetch per channel | 100 |
| `days_back` | How many days back to fetch | 7 |
| `output_directory` | Where to save markdown files | "archived_channels" |

## 🔒 Authentication

On first run, Telegram will send you a verification code via the app. Enter it when prompted. The session will be saved for future runs.

## 📊 Markdown Output Features

- **Message metadata**: Sender, timestamp, message ID
- **Content formatting**: Preserves text formatting
- **Media detection**: Notes photos, documents, etc.
- **Forward/reply tracking**: Shows message relationships
- **Channel organization**: Separate files per channel
- **JSON metadata**: Additional data for analysis

## 🛠️ Troubleshooting

### Common Issues

1. **"Could not find the input entity"**
   - Make sure you're a member of the channel
   - Check the channel identifier format
   - For private channels, use the full invite link

2. **"API ID/Hash invalid"**
   - Double-check your credentials from my.telegram.org
   - Make sure API_ID is a number, API_HASH is a string

3. **"No messages found"**
   - Increase `days_back` in config
   - Check if the channel has recent messages
   - Verify you have access to the channel

### Getting Help

- Check the console output for specific error messages
- Verify your channel access in the Telegram app
- Make sure your API credentials are correct

## 🔄 Automation Ideas

You can set up automated archiving using:

- **Cron jobs** (Linux/Mac): Run daily/weekly
- **Task Scheduler** (Windows): Schedule regular runs
- **GitHub Actions**: Cloud-based automation
- **Docker**: Containerized deployment

Example cron job (daily at 9 AM):
```bash
0 9 * * * cd /path/to/archiver && source venv/bin/activate && python run_archiver.py
```