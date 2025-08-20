# 🚀 Telegram Archive Browser

> **A modern, elegant web-based Telegram channel archiver with real-time monitoring, smart file handling, and beautiful dark theme UI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.0+-06B6D4.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🎨 **Modern Web Interface**
- **Dark/Light Theme Toggle** - Professional dark mode with smooth transitions
- **Glass Morphism Design** - Beautiful translucent cards with backdrop blur effects
- **Custom OperatorMono Font** - Elegant monospace typography throughout
- **Responsive Design** - Perfect on desktop, tablet, and mobile devices
- **Real-time Updates** - Live progress monitoring and status indicators

### 📱 **Channel Management**
- **Web-based Configuration** - No more manual config.json editing
- **Add/Edit/Delete Channels** - Full CRUD operations with beautiful modals
- **Smart URL Validation** - Supports `https://t.me/channel` and `@channel` formats
- **Auto-name Generation** - Automatically suggests friendly names from URLs
- **Enable/Disable Channels** - Toggle archiving without deleting configuration
- **Bulk Operations** - Manage multiple channels efficiently

### 🔄 **Frontend Archiving Control**
- **Start/Stop Archiving** - Full control from the web interface
- **Real-time Progress Tracking** - Live progress bars and channel status
- **Smart File Handling** - Configurable file size limits (skip large files)
- **Live Logs Terminal** - Real-time archiving logs with terminal styling
- **Process Monitoring** - Track current channel, processed count, and timing

### 📊 **Advanced Dashboard**
- **Statistics Cards** - Animated counters for channels, messages, files, and media
- **Archive Overview** - Visual representation of your archive collection
- **Channel Status** - Live indicators for archiving activity
- **Quick Actions** - Fast access to search, refresh, and system info

### 🔍 **Powerful Search**
- **Full-text Search** - Find content across all archived channels
- **Channel Filtering** - Search within specific channels
- **Highlighted Results** - Search terms highlighted in results
- **Advanced Filters** - Date ranges, media types, and more
- **Export Results** - Save search results for later analysis

### 📁 **Smart File Management**
- **Markdown + JSON Format** - Human-readable archives with metadata
- **Media Organization** - Automatic media file organization and linking
- **Image Previews** - Click images for full-size modal previews
- **File Type Detection** - Smart icons and handling for different media types
- **Size Optimization** - Configurable file size limits to prevent long downloads

### 🛡️ **Security & Performance**
- **Secure Configuration** - API credentials safely stored
- **Error Handling** - Graceful failure recovery and user feedback
- **Performance Optimized** - Efficient CSS, lazy loading, and smart caching
- **Cross-platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram API credentials (api_id and api_hash)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/telegram-archive-browser.git
   cd telegram-archive-browser
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**
   ```bash
   python test_setup.py
   ```
   Follow the prompts to enter your Telegram API credentials.

4. **Start the web interface**
   ```bash
   python web_frontend.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000` and enjoy your modern archive browser!

## 📖 Usage Guide

### 🎛️ **Channel Management**

#### Adding Channels
1. Click the **"Add Channel"** button in the Channel Management section
2. Enter the Telegram channel URL (`https://t.me/channelname`) or username (`@channelname`)
3. The display name will be auto-generated, or you can customize it
4. Choose whether to enable archiving immediately
5. Click **"Add Channel"** to save

#### Managing Existing Channels
- **Edit**: Click the edit button to modify channel details
- **Enable/Disable**: Toggle archiving without deleting the channel
- **Delete**: Remove channels with confirmation (archived files remain)

### 🔄 **Archiving Control**

#### Starting Archiving
1. Configure **Max File Size** (default: 50MB)
2. Choose **File Handling**: Skip or Download large files
3. Click **"Start Archiving"** to begin
4. Monitor progress in real-time with live logs

#### Monitoring Progress
- **Progress Bar**: Visual completion percentage
- **Current Channel**: See which channel is being processed
- **Live Logs**: Terminal-style output with timestamps
- **Statistics**: Processed vs. total channels

### 🔍 **Searching Archives**

#### Basic Search
1. Use the search bar in the navigation or go to the Search page
2. Enter keywords to find across all channels
3. Optionally filter by specific channel
4. View highlighted results with context

#### Advanced Features
- **Case-insensitive**: Search works regardless of capitalization
- **Multi-word**: Search for phrases or multiple keywords
- **Media filtering**: Find messages with specific media types
- **Export results**: Save search results for analysis

### 🎨 **Customization**

#### Theme Switching
- Click the **theme toggle button** in the navigation
- Supports both light and dark modes
- Preference saved automatically

#### Font Customization
- Custom OperatorMono font included
- Fallback to system monospace fonts
- Optimized for readability and code display

## 📁 Project Structure

```
telegram-archive-browser/
├── 📄 web_frontend.py          # Main Flask application
├── 📄 telegram_archiver.py     # Core archiving functionality
├── 📄 monitor_control.py       # Process monitoring and control
├── 📄 run_archiver.py          # Archiving script runner
├── 📄 config.json              # Configuration file
├── 📁 templates/               # HTML templates
│   ├── 📄 base.html            # Base template with navigation
│   ├── 📄 index.html           # Dashboard and channel management
│   ├── 📄 search.html          # Search interface
│   ├── 📄 channel.html         # Channel file listings
│   └── 📄 view.html            # File viewer with media support
├── 📁 static/                  # Static assets
│   ├── 📁 css/
│   │   └── 📄 style.css        # Custom Tailwind CSS styles
│   ├── 📁 fonts/
│   │   └── 📄 OperatorMonoLig-Book.otf  # Custom font
│   └── 📁 js/
│       └── 📄 app.js           # Frontend JavaScript
└── 📁 archived_channels/       # Archived content storage
    └── 📁 [Channel Name]/
        ├── 📄 [Channel]_[Date].md     # Markdown archives
        ├── 📄 [Channel]_[Date]_metadata.json  # Metadata
        └── 📁 media/               # Downloaded media files
```

## ⚙️ Configuration

### API Credentials
```json
{
  "api_credentials": {
    "api_id": "your_api_id",
    "api_hash": "your_api_hash",
    "session_name": "telegram_archiver"
  }
}
```

### Channel Configuration
```json
{
  "channels": [
    {
      "identifier": "https://t.me/channelname",
      "name": "Display Name",
      "enabled": true
    }
  ]
}
```

### Archive Settings
```json
{
  "archive_settings": {
    "messages_per_channel": 100,
    "days_back": 7,
    "output_directory": "archived_channels",
    "download_media": true
  }
}
```

## 🔧 Advanced Features

### Smart File Handling
- **Size Limits**: Configure maximum file size for downloads
- **Skip Large Files**: Automatically skip files exceeding limits
- **Media Organization**: Automatic folder structure for media files
- **Format Support**: Images, videos, documents, and audio files

### Real-time Monitoring
- **Live Progress**: Real-time updates during archiving
- **Process Control**: Start/stop archiving from the web interface
- **Error Handling**: Graceful recovery from network issues
- **Logging**: Comprehensive logs with timestamps

### Performance Optimization
- **Lazy Loading**: Efficient loading of large archive lists
- **Caching**: Smart caching for faster page loads
- **Compression**: Optimized assets and images
- **Responsive**: Adaptive layouts for all screen sizes

## 🎨 UI/UX Features

### Design System
- **Glass Morphism**: Modern translucent design elements
- **Gradient Accents**: Beautiful color transitions
- **Micro-interactions**: Smooth hover effects and animations
- **Typography**: Custom OperatorMono font for elegance

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Proper ARIA labels and semantic HTML
- **Color Contrast**: WCAG compliant color schemes
- **Focus Management**: Clear focus indicators

### Mobile Experience
- **Touch Friendly**: Large touch targets and gestures
- **Responsive Grid**: Adaptive layouts for all devices
- **Mobile Navigation**: Collapsible menu for small screens
- **Performance**: Optimized for mobile networks

## 🛠️ Development

### Local Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python web_frontend.py

# Access at http://localhost:5000
```

### Customization
- **Themes**: Modify CSS variables for custom colors
- **Fonts**: Replace OperatorMono with your preferred font
- **Layout**: Adjust Tailwind classes for different layouts
- **Features**: Extend API endpoints for additional functionality

## 📊 API Reference

### Channel Management
- `GET /api/channels` - Get all channels
- `POST /api/channels` - Add new channel
- `PUT /api/channels/{index}` - Update channel
- `DELETE /api/channels/{index}` - Delete channel

### Archiving Control
- `POST /api/archiving/start` - Start archiving process
- `POST /api/archiving/stop` - Stop archiving process
- `GET /api/archiving/status` - Get archiving status

### Settings
- `GET /api/settings` - Get archive settings
- `POST /api/settings` - Update archive settings

## 🔒 Security

### Best Practices
- **API Credentials**: Stored securely in config.json
- **Input Validation**: All user inputs validated and sanitized
- **CSRF Protection**: Forms protected against cross-site requests
- **Error Handling**: Sensitive information not exposed in errors

### Privacy
- **Local Storage**: All data stored locally on your machine
- **No Tracking**: No analytics or tracking scripts
- **Secure Sessions**: Telegram sessions handled securely
- **Data Control**: Full control over your archived data

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Telethon** - Telegram client library
- **Flask** - Web framework
- **Tailwind CSS** - Utility-first CSS framework
- **OperatorMono** - Beautiful monospace font
- **Heroicons** - Beautiful SVG icons

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/telegram-archive-browser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/telegram-archive-browser/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/telegram-archive-browser/wiki)

---

<div align="center">

**Built with ❤️ for secure and elegant Telegram archiving**

[⭐ Star this repo](https://github.com/yourusername/telegram-archive-browser) | [🐛 Report Bug](https://github.com/yourusername/telegram-archive-browser/issues) | [💡 Request Feature](https://github.com/yourusername/telegram-archive-browser/issues)

</div>